"""ETL class for neuropixels rigs."""

import json
import pathlib
import datetime
import typing
from aind_data_schema import rig

from ..core import BaseEtl
from . import open_ephys, mvr, dxdiag, sync, utils, NeuropixelsRigException


# partial rig, mvr cameras, sync daq, open ephys probes, dxdiag settings
RigContext = tuple[
    dict,
    list[mvr.MVRCamera],
    sync.SyncSettings,
    list[open_ephys.OpenEphysProbe],
    dxdiag.DxdiagSettings,
]


class NeuropixelsRigEtl(BaseEtl):
    """Neuropixels rig ETL class. Extracts information from rig-related files
    and transforms them into an aind-data-schema rig.Rig instance.
    """

    def __init__(
        self,
        input_directory: pathlib.Path,
        output_directory: pathlib.Path,
        modification_date: typing.Optional[datetime.date] = None,
    ):
        """Class constructor for Neuropixels rig etl class.

        Parameters
        ----------
        input_directory : Path
          The directory containing required resource files.
        output_directory : Path
          The directory where to save the json files.
        modification_date: datetime.date
          Date of modification, defaults to today.
        """
        super().__init__(input_directory, output_directory)
        if modification_date is None:
            self.modification_date = datetime.date.today()
        else:
            self.modification_date = modification_date

    def _extract(self) -> RigContext:
        """Extracts rig-related information from config files.
        """
        if not self.input_source.is_dir():
            raise NeuropixelsRigException(
                "Input source is not a directory. %s" % self.input_source
            )

        return (
            json.loads(
                (self.input_source / "rig.partial.json").read_text(),
            ),
            mvr.extract(
                (self.input_source / "mvr.ini").read_text(),
                json.loads(
                    (self.input_source / "mvr.mapping.json").read_text(),
                ),
            ),
            sync.extract(
                (self.input_source / "sync.yml").read_text(),
            ),
            open_ephys.extract(
                (self.input_source / "settings.open_ephys.xml").read_text(),
            ),
            dxdiag.extract(
                (self.input_source / "dxdiag.xml").read_text(),
            ),
        )

    def _transform(self, extracted_source: RigContext) -> rig.Rig:
        """Transforms extracted rig context into aind-data-schema rig.Rig
        instance.
        """
        partial, mvr_cameras, sync_settings, open_ephys_probes, \
            dxdiag_settings = extracted_source

        sync_daq_channels = [
            channel.dict()
            for channel in sync.transform(sync_settings)
        ]
        daqs = utils.find_transform_replace(
            partial["daqs"],
            lambda partial_daq: partial_daq["name"] == "Sync",
            lambda partial_sync_daq: \
                {**partial_sync_daq, "channels": sync_daq_channels}
        )

        stimulus_devices = utils.find_transform_replace(
            partial["stimulus_devices"],
            lambda device: device["device_type"] == "Monitor",
            lambda partial_monitor: dxdiag.transform(
                dxdiag_settings, **partial_monitor).dict()
        )

        camera_assemblies = []
        for partial_camera_assembly in partial["cameras"]:
            name = partial_camera_assembly["camera_assembly_name"]
            
            found = list(filter(
                lambda camera: camera.assembly_name == name,
                mvr_cameras,
            ))
            if len(found) < 1:
                raise NeuropixelsRigException(
                    "Camera assembly not found in partial rig. expected=%s"
                    % name
                )
            
            camera_assemblies.append({
                **partial_camera_assembly,
                "camera": {
                    **partial_camera_assembly["camera"],
                    "name": found[0].assembly_name,
                    "serial_number": found[0].serial_number,
                    "pixel_height": found[0].height,
                    "pixel_width": found[0].width,
                    "size_unit": "pixel",
                    "max_frame_rate": found[0].frame_rate,
                }
            })

        ephys_assemblies = []
        for partial_ephys_assembly in partial["ephys_assemblies"]:
            assembly_name = partial_ephys_assembly["ephys_assembly_name"]
            found = list(filter(
                lambda probe: probe.name == \
                    assembly_name,
                open_ephys_probes,
            ))
            if len(found) < 1:
                raise NeuropixelsRigException(
                    "Open ephys probe not found for partial rig. expected=%s"
                    % assembly_name
                )
            for open_ephys_probe in found:
                partial_ephys_assembly = utils.find_transform_replace(
                    partial_ephys_assembly["probes"],
                    lambda partial_probe: partial_probe["name"] == \
                        open_ephys_probe.name,
                    lambda partial_probe: open_ephys.transform(
                        open_ephys_probe, **partial_probe).dict()
                )
            ephys_assemblies.append({
                **partial_ephys_assembly,
                "probes": [
                    open_ephys.transform(found[0]).dict(),
                ]
            })

        return rig.Rig.parse_obj({
            **partial,
            "stimulus_devices": stimulus_devices,
            "modification_date": self.modification_date,
            "daqs": daqs,
            "cameras": camera_assemblies,
            "ephys_assemblies": ephys_assemblies,
        })
