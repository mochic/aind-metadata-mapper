"""Module to map bergamo metadata into a session model"""

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from aind_data_schema.core.session import (
    DetectorConfig,
    FieldOfView,
    LaserConfig,
    Modality,
    Session,
    Stream,
    TriggerType,
)
from aind_data_schema.models.stimulus import (
    PhotoStimulation,
    PhotoStimulationGroup,
    StimulusEpoch,
)
from aind_data_schema.models.units import PowerUnit
from pydantic import Field
from decimal import Decimal
from ScanImageTiffReader import ScanImageTiffReader

from aind_metadata_mapper.core import BaseEtl


class BergamoDetectorConfig(DetectorConfig):
    # Fields with default values specific to Bergamo Sessions
    trigger_type: TriggerType = Field(TriggerType.INTERNAL)
    name: str = Field("PMT A", title="Name")
    exposure_time: Decimal = Field(Decimal('0.1'), title="Exposure time (ms)")


class BergamoFieldOfView(FieldOfView):
    # Fields with default values specific to Bergamo Sessions
    index: int = Field(default=0, title="Index")
    imaging_depth: int = Field(default=150, title="Imaging depth (um)")
    targeted_structure: str = Field(default="M1", title="Targeted structure")
    fov_coordinate_ml: Decimal = Field(
        default=Decimal('1.5'), title="FOV coordinate ML"
    )
    fov_coordinate_ap: Decimal = Field(
        default=Decimal('1.5'), title="FOV coordinate AP"
    )
    fov_reference: str = Field(
        default="Bregma",
        title="FOV reference",
        description="Reference for ML/AP coordinates",
    )
    magnification: str = Field(default="16x", title="Magnification")

    # Required fields that will be parsed from files.
    fov_width: Optional[int] = Field(None, title="FOV width (pixels)")
    fov_height: Optional[int] = Field(None, title="FOV height (pixels)")
    fov_scale_factor: Optional[Decimal] = Field(
        None, title="FOV scale factor (um/pixel)"
    )


class BergamoLaserConfig(LaserConfig):
    # Fields with default values specific to Bergamo Sessions
    name: str = Field(
        "Laser A", title="Name", description="Must match rig json"
    )
    wavelength: int = Field(920, title="Wavelength (nm)")
    excitation_power_unit: PowerUnit = Field(
        PowerUnit.PERCENT, title="Excitation power unit"
    )


class BergamoPhotoStimulationGroup(PhotoStimulationGroup):
    # Fields with default values specific to Bergamo Sessions
    group_index: int = Field(default=0, title="Group index")
    number_trials: int = Field(default=5, title="Number of trials")

    # Required fields that will be parsed from files.
    number_of_neurons: Optional[int] = Field(None, title="Number of neurons")
    stimulation_laser_power: Optional[Decimal] = Field(
        None, title="Stimulation laser power (mW)"
    )
    number_spirals: Optional[int] = Field(None, title="Number of spirals")
    spiral_duration: Optional[Decimal] = Field(
        None, title="Spiral duration (s)"
    )
    inter_spiral_interval: Optional[Decimal] = Field(
        None, title="Inter trial interval (s)"
    )


class BergamoPhotoStimulation(PhotoStimulation):
    # Fields with default values specific to Bergamo Sessions
    stimulus_name: str = Field(
        default="PhotoStimulation", title="Stimulus name"
    )
    inter_trial_interval: Decimal = Field(
        default=Decimal('10'), title="Inter trial interval (s)"
    )
    number_groups: Optional[int] = Field(2, title="Number of groups")

    # Required fields that will be parsed from files.
    groups: List[BergamoPhotoStimulationGroup] = Field(
        [BergamoPhotoStimulationGroup(), BergamoPhotoStimulationGroup()],
        title="Groups",
    )


class BergamoStimulusEpoch(StimulusEpoch):
    # Required fields that will be parsed from files.
    stimulus: BergamoPhotoStimulation = Field(
        BergamoPhotoStimulation(), title="Stimulus"
    )


class BergamoStream(Stream):
    # Fields with default values specific to Bergamo Sessions
    camera_names: List[str] = Field(default=["Side Camera"], title="Cameras")
    stream_modalities: List[Modality.ONE_OF] = Field(
        default=[Modality.POPHYS], title="Modalities"
    )

    # Required fields that will be parsed from files.
    light_sources: List[BergamoLaserConfig] = Field(
        default=[BergamoLaserConfig()], title="Light Sources"
    )
    detectors: List[BergamoDetectorConfig] = Field(
        default=[BergamoDetectorConfig()], title="Detectors"
    )
    ophys_fovs: List[BergamoFieldOfView] = Field(
        default=[BergamoFieldOfView()], title="Fields of view"
    )


class BergamoSession(Session):
    # Fields with default values specific to Bergamo Sessions
    iacuc_protocol: Optional[str] = Field(
        default="2115", title="IACUC protocol"
    )
    session_type: str = Field(default="BCI", title="Session type")
    rig_id: str = Field(default="Bergamo photostim.", title="Rig ID")

    # Required fields that will be parsed from files.

    data_streams: List[BergamoStream] = Field(
        ...,
        title="Data streams",
        description=(
            "A data stream is a collection of devices that are recorded"
            " simultaneously. Each session can include"
            " multiple streams (e.g., if the manipulators are moved to a new"
            " location)"
        ),
    )
    stimulus_epochs: List[BergamoStimulusEpoch] = Field(..., title="Stimulus")


@dataclass(frozen=True)
class RawImageInfo:
    """Metadata from tif files"""

    metadata: str
    description0: str
    shape: List[int]


@dataclass(frozen=True)
class ParsedMetadata:
    """RawImageInfo gets parsed into this data"""

    metadata: dict
    roi_data: dict
    roi_metadata: List[dict]
    frame_rate: str
    num_planes: int
    shape: List[int]
    description_first_frame: dict
    movie_start_time: datetime


class BergamoEtl(BaseEtl[BergamoSession, Dict[str, Path]]):
    """Class to manage transforming bergamo data files into a Session object"""

    def __init__(
        self,
        input_source: Path,
        output_directory: Optional[Path],
        specific_model: BergamoSession,
    ):
        """
        Class constructor for Base etl class.
        Parameters
        ----------
        input_source : Path
          Directory of tiff files to parse
        output_directory : Optional[Path]
          The directory where to save the metadata file. Default is None.
        specific_model : BergamoSession
          Model for a Bergamo session
        """
        super().__init__(
            input_sources={"tiff_directory": input_source},
            output_directory=output_directory,
            specific_model=specific_model,
        )
        self.input_source = input_source

    @staticmethod
    def _flat_dict_to_nested(flat: dict, key_delim: str = ".") -> dict:
        """
        Utility method to convert a flat dictionary into a nested dictionary.
        Modified from https://stackoverflow.com/a/50607551
        Parameters
        ----------
        flat : dict
          Example {"a.b.c": 1, "a.b.d": 2, "e.f": 3}
        key_delim : str
          Delimiter on dictionary keys. Default is '.'.

        Returns
        -------
        dict
          A nested dictionary like {"a": {"b": {"c":1, "d":2}, "e": {"f":3}}
        """

        def __nest_dict_rec(k, v, out) -> None:
            """Simple recursive method being called."""
            k, *rest = k.split(key_delim, 1)
            if rest:
                __nest_dict_rec(rest[0], v, out.setdefault(k, {}))
            else:
                out[k] = v

        result = {}
        for flat_key, flat_val in flat.items():
            __nest_dict_rec(flat_key, flat_val, result)
        return result

    def _parse_raw_image_info(
        self, raw_image_info: RawImageInfo
    ) -> ParsedMetadata:
        """
        Parses metadata from raw image info.
        Parameters
        ----------
        raw_image_info : RawImageInfo

        Returns
        -------
        ParsedMetadata
        """

        # The metadata contains two parts separated by \n\n. The top part
        # looks like
        # 'SI.abc.def = 1\n SI.abc.ghf=2'
        # We'll convert that to a nested dict.
        metadata_first_part = raw_image_info.metadata.split("\n\n")[0]
        flat_metadata_header_dict = dict(
            [
                (s.split(" = ", 1)[0], s.split(" = ", 1)[1])
                for s in metadata_first_part.split("\n")
            ]
        )
        metadata = self._flat_dict_to_nested(flat_metadata_header_dict)
        # Move SI dictionary up one level
        if "SI" in metadata.keys():
            si_contents = metadata.pop("SI")
            metadata.update(si_contents)

        # The second part is a standard json string. We'll extract it and
        # append it to our dictionary
        metadata_json = json.loads(raw_image_info.metadata.split("\n\n")[1])
        metadata["json"] = metadata_json

        # Convert description string to a dictionary
        first_frame_description_str = raw_image_info.description0.strip()
        description_first_image_dict = dict(
            [
                (s.split(" = ", 1)[0], s.split(" = ", 1)[1])
                for s in first_frame_description_str.split("\n")
            ]
        )
        frame_rate = metadata["hRoiManager"]["scanVolumeRate"]
        # TODO: Use .get instead of try/except and add coverage test
        try:
            z_collection = metadata["hFastZ"]["userZs"]
            num_planes = len(z_collection)  # pragma: no cover
        except Exception as e:  # new scanimage version
            logging.error(
                f"Multiple planes not handled in metadata collection. "
                f"HANDLE ME!!!: {repr(e)}"
            )
            # TODO: Check if this if/else is necessary
            if metadata["hFastZ"]["enable"] == "true":
                num_planes = 1  # pragma: no cover
            else:
                num_planes = 1

        roi_metadata = metadata["json"]["RoiGroups"]["imagingRoiGroup"]["rois"]

        if isinstance(roi_metadata, dict):
            roi_metadata = [roi_metadata]
        num_rois = len(roi_metadata)
        roi = {}
        w_px = []
        h_px = []
        cXY = []
        szXY = []
        for r in range(num_rois):
            roi[r] = {}
            roi[r]["w_px"] = roi_metadata[r]["scanfields"][
                "pixelResolutionXY"
            ][0]
            w_px.append(roi[r]["w_px"])
            roi[r]["h_px"] = roi_metadata[r]["scanfields"][
                "pixelResolutionXY"
            ][1]
            h_px.append(roi[r]["h_px"])
            roi[r]["center"] = roi_metadata[r]["scanfields"]["centerXY"]
            cXY.append(roi[r]["center"])
            roi[r]["size"] = roi_metadata[r]["scanfields"]["sizeXY"]
            szXY.append(roi[r]["size"])

        w_px = np.asarray(w_px)
        h_px = np.asarray(h_px)
        szXY = np.asarray(szXY)
        cXY = np.asarray(cXY)
        cXY = cXY - szXY / 2
        cXY = cXY - np.amin(cXY, axis=0)
        mu = np.median(np.transpose(np.asarray([w_px, h_px])) / szXY, axis=0)
        imin = cXY * mu

        n_rows_sum = np.sum(h_px)
        n_flyback = (raw_image_info.shape[1] - n_rows_sum) / np.max(
            [1, num_rois - 1]
        )

        irow = np.insert(np.cumsum(np.transpose(h_px) + n_flyback), 0, 0)
        irow = np.delete(irow, -1)
        irow = np.vstack((irow, irow + np.transpose(h_px)))

        data = {"fs": frame_rate, "nplanes": num_planes, "nrois": num_rois}
        if data["nrois"] == 1:
            data["mesoscan"] = 0
        else:
            # TODO: Add coverage example
            data["mesoscan"] = 1  # pragma: no cover
        # TODO: Add coverage example
        if data["mesoscan"]:  # pragma: no cover
            # data['nrois'] = num_rois #or irow.shape[1]?
            data["dx"] = []
            data["dy"] = []
            data["lines"] = []
            for i in range(num_rois):
                data["dx"] = np.hstack((data["dx"], imin[i, 1]))
                data["dy"] = np.hstack((data["dy"], imin[i, 0]))
                # TODO: NOT QUITE RIGHT YET
                data["lines"] = list(
                    range(
                        irow[0, i].astype("int32"),
                        irow[1, i].astype("int32") - 1,
                    )
                )
            data["dx"] = data["dx"].astype("int32")
            data["dy"] = data["dy"].astype("int32")
            logging.debug(f"data[dx]: {data['dx']}")
            logging.debug(f"data[dy]: {data['dy']}")
            logging.debug(f"data[lines]: {data['lines']}")
        movie_start_time = datetime.strptime(
            description_first_image_dict["epoch"], "[%Y %m %d %H %M %S.%f]"
        )

        return ParsedMetadata(
            metadata=metadata,
            roi_data=data,
            roi_metadata=roi_metadata,
            frame_rate=frame_rate,
            num_planes=num_planes,
            shape=raw_image_info.shape,
            description_first_frame=description_first_image_dict,
            movie_start_time=movie_start_time,
        )

    @staticmethod
    def _get_si_file_from_dir(
        source_dir: Path, regex_pattern: str = r"^.*?(\d+).tif+$"
    ) -> Path:
        """
        Utility method to scan top level of source_dir for .tif or .tiff files.
        Sorts them by file number and collects the first one. The directory
        contains files that look like neuron50_00001.tif, neuron50_00002.tif.
        Parameters
        ----------
        source_dir : Path
          Directory where the tif files are located
        regex_pattern : str
          Format of how files are expected to be organized. Default matches
          against something that ends with a series of digits and .tif(f)

        Returns
        -------
        Path
          File path of the first tif file.

        """
        compiled_regex = re.compile(regex_pattern)
        tif_filepath = None
        old_tif_number = None
        for root, dirs, files in os.walk(source_dir):
            for name in files:
                matched = re.match(compiled_regex, name)
                if matched:
                    tif_number = matched.group(1)
                    if old_tif_number is None or tif_number < old_tif_number:
                        old_tif_number = tif_number
                        tif_filepath = Path(os.path.join(root, name))

            # Only scan the top level files
            break
        if tif_filepath is None:
            raise FileNotFoundError("Directory must contain tif or tiff file!")
        else:
            return tif_filepath

    def _extract(self) -> RawImageInfo:
        """Extract metadata from bergamo session. If input source is a file,
        will extract data from file. If input source is a directory, will
        attempt to find a file."""
        if isinstance(self.input_sources["tiff_directory"], str):
            input_source = Path(self.input_sources["tiff_directory"])
        else:
            input_source = self.input_sources["tiff_directory"]

        if os.path.isfile(input_source):
            file_with_metadata = input_source
        else:
            file_with_metadata = self._get_si_file_from_dir(input_source)
        # Not sure if a custom header was appended, but we can't use
        # o=json.loads(reader.metadata()) directly
        with ScanImageTiffReader(str(file_with_metadata)) as reader:
            img_metadata = reader.metadata()
            img_description = reader.description(0)
            img_shape = reader.shape()
        return RawImageInfo(
            metadata=img_metadata,
            description0=img_description,
            shape=img_shape,
        )

    def _transform(self, extracted_source: RawImageInfo) -> Session:
        """
        Transforms the raw data extracted from the tif directory into a
        Session object.
        Parameters
        ----------
        extracted_source : RawImageInfo

        Returns
        -------
        Session

        """
        siHeader = self._parse_raw_image_info(extracted_source)
        photostim_groups = siHeader.metadata["json"]["RoiGroups"][
            "photostimRoiGroups"
        ]

        updated_session = self.specific_model.model_copy(deep=True)

        # Update data_streams with information from files
        data_stream = updated_session.data_streams[0]
        light_sources = data_stream.light_sources[0]
        light_sources.excitation_power = Decimal(
            str(siHeader.metadata["hBeams"]["powers"][1:-1].split()[0])
        )
        field_of_view = data_stream.ophys_fovs[0]
        field_of_view.fov_width = int(
            siHeader.metadata["hRoiManager"]["pixelsPerLine"]
        )
        field_of_view.fov_height = int(
            siHeader.metadata["hRoiManager"]["linesPerFrame"]
        )
        field_of_view.fov_scale_factor = Decimal(
            str(siHeader.metadata["hRoiManager"]["scanZoomFactor"])
        )
        field_of_view.frame_rate = Decimal(
            str(siHeader.metadata["hRoiManager"]["scanFrameRate"])
        )

        # Update stimulus_epochs with information from files
        stimulus_epoch = updated_session.stimulus_epochs[0]
        stimulus_epoch_stimulus = stimulus_epoch.stimulus
        stimulus_epoch_stimulus_groups = stimulus_epoch_stimulus.groups
        group0 = stimulus_epoch_stimulus_groups[0]
        group0.number_of_neurons = int(
            np.array(
                photostim_groups[0]["rois"][1]["scanfields"]["slmPattern"]
            ).shape[0]
        )
        group0.stimulation_laser_power = Decimal(
            str(photostim_groups[0]["rois"][1]["scanfields"]["powers"])
        )
        group0.number_spirals = int(
            photostim_groups[0]["rois"][1]["scanfields"]["repetitions"]
        )
        group0.spiral_duration = Decimal(
            str(photostim_groups[0]["rois"][1]["scanfields"]["duration"])
        )
        group0.inter_spiral_interval = Decimal(
            str(photostim_groups[0]["rois"][2]["scanfields"]["duration"])
        )

        group1 = stimulus_epoch_stimulus_groups[1]
        # TODO: These indexes are the same as the ones above. Check if this
        #  is correct.
        group1.number_of_neurons = int(
            np.array(
                photostim_groups[0]["rois"][1]["scanfields"]["slmPattern"]
            ).shape[0]
        )
        group1.stimulation_laser_power = Decimal(
            str(photostim_groups[0]["rois"][1]["scanfields"]["powers"])
        )
        group1.number_spirals = int(
            photostim_groups[0]["rois"][1]["scanfields"]["repetitions"]
        )
        group1.spiral_duration = Decimal(
            str(photostim_groups[0]["rois"][1]["scanfields"]["duration"])
        )
        group1.inter_spiral_interval = Decimal(
            str(photostim_groups[0]["rois"][2]["scanfields"]["duration"])
        )

        return Session.model_validate(updated_session.model_dump())

    @classmethod
    def from_args(cls, args: list):
        """
        Adds ability to construct settings from a list of arguments.
        Parameters
        ----------
        args : list
        A list of command line arguments to parse.
        """

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-i",
            "--input-source",
            required=False,
            type=str,
            help="Directory where tif files are located",
        )
        parser.add_argument(
            "-o",
            "--output-directory",
            required=False,
            default=".",
            type=str,
            help=(
                "Directory to save json file to. Defaults to current working "
                "directory."
            ),
        )
        parser.add_argument(
            "-s",
            "--specific-model",
            required=True,
            type=str,
            help="JSON serialized string of a BergamoSession model",
        )
        job_args = parser.parse_args(args)
        return cls(
            input_source=Path(job_args.input_source),
            output_directory=Path(job_args.output_directory),
            specific_model=BergamoSession.model_validate_json(
                job_args.specified_model
            ),
        )


if __name__ == "__main__":
    sys_args = sys.argv[1:]
    etl = BergamoEtl.from_args(sys_args)
    etl.run_job()
