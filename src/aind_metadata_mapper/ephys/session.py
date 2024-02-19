"""Module to write valid ephys schemas"""

import csv
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Union
from xml.dom.minidom import Document, parse

from aind_data_schema.core.session import EphysModule, Session, Stream
from aind_data_schema.models.coordinates import Coordinates3d
from aind_data_schema.models.modalities import Modality
from pydantic import BaseModel, ConfigDict, Field, field_validator

from aind_metadata_mapper.core import BaseEtl


class OpenEphysModule(EphysModule):
    """Required fields in the EphysModule model will be overriden here if the
    information can be pulled from other sources."""

    # The following are required fields in the EphysModule that we will parse
    # from files or set manually.
    manipulator_coordinates: Optional[Coordinates3d] = Field(default=None)


class OpenEphysStream(Stream):
    """Required fields in the Stream model will be overriden here if the
    information can be pulled from other sources."""

    # The following are required fields in the Stream that we will parse
    # from files or set manually.
    stream_start_time: Optional[datetime] = Field(None)
    stream_end_time: Optional[datetime] = Field(None)
    stream_modalities: List[Modality.ONE_OF] = Field([Modality.ECEPHYS])
    ephys_modules: List[OpenEphysModule] = Field(default=[])


class OpenEphysSession(Session):
    """Required fields in the Session model will be overriden here if the
    information can be pulled from other sources. A user will still be expected
    to build an IncompleteSession model to attach data to."""

    # The following are required fields in the Stream that we will parse
    # from files or set manually.
    data_streams: List[OpenEphysStream] = Field(default=[])
    session_start_time: Optional[datetime] = Field(
        None, title="Session start time"
    )


class StageLogRow(BaseModel):
    log_timestamp: datetime = Field(...)
    probe_name: str = Field(...)
    coordinate1: Decimal
    coordinate2: Decimal
    coordinate3: Decimal
    coordinate4: Decimal
    coordinate5: Decimal
    coordinate6: Decimal

    @field_validator("log_timestamp", mode="before")
    def parse_log_timestamp(cls, value: Union[str, datetime]) -> datetime:
        """Parses the log timestamps from their given format"""
        if isinstance(value, str):
            return datetime.strptime(value, "%Y/%m/%d %H:%M:%S.%f")
        else:
            return value

    @property
    def probe_name_no_prefix(self) -> str:
        """Strips the prefix off the probe name. For example, 'SN12345' gets
        mapped to just '12345'"""
        return self.probe_name.replace("SN", "")


class StageLog(BaseModel):
    filename: str
    # We can consider changing this to an iterator if the log files are large
    contents: List[StageLogRow]

    @classmethod
    def from_csv_file(cls, csv_file_path: Path):
        field_names = [f for f in StageLogRow.model_fields]
        with open(csv_file_path, "r") as f:
            reader = csv.DictReader(
                f, fieldnames=field_names, skipinitialspace=True
            )
            return cls(
                filename=csv_file_path.name,
                contents=[StageLogRow(**row) for row in reader],
            )


class OpenEphysLog(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    filename: str
    # TODO: It might be better to use a different data type
    contents: Document

    @classmethod
    def from_xml_file(cls, xml_file_path: Path):
        with open(xml_file_path, "r") as f:
            contents = parse(f)
        return cls(filename=xml_file_path.name, contents=contents)


@dataclass(frozen=True)
class RawInformation:
    """RawImageInfo gets parsed into this data"""

    stage_logs: List[StageLog]
    openephys_logs: List[OpenEphysLog]


@dataclass(frozen=True)
class StageLogProbeInfo:
    probe_stream_start_time: datetime
    probe_stream_end_time: datetime
    manipulator_coordinates: Coordinates3d


@dataclass(frozen=True)
class StageLogParsedInfo:
    filename: str
    stream_start_time: datetime
    stream_end_time: datetime
    probe_map: Dict[str, StageLogProbeInfo]

    @classmethod
    def from_stage_log(cls, stage_log: StageLog):
        filename = stage_log.filename
        stream_start_time: Optional[datetime] = None
        stream_end_time: Optional[datetime] = None
        probe_map = {}
        for stage_log_row in stage_log.contents:
            probe_name_no_prefix = stage_log_row.probe_name_no_prefix
            log_timestamp = stage_log_row.log_timestamp
            manipulator_coordinates = Coordinates3d(
                x=stage_log_row.coordinate1,
                y=stage_log_row.coordinate2,
                z=stage_log_row.coordinate3,
            )
            if stream_start_time is None or log_timestamp < stream_start_time:
                stream_start_time = log_timestamp
            if stream_end_time is None or log_timestamp > stream_end_time:
                stream_end_time = log_timestamp

            if probe_map.get(probe_name_no_prefix) is None:
                probe_map[probe_name_no_prefix] = StageLogProbeInfo(
                    probe_stream_end_time=log_timestamp,
                    probe_stream_start_time=log_timestamp,
                    manipulator_coordinates=manipulator_coordinates,
                )
            else:
                old_info = probe_map[probe_name_no_prefix]
                if log_timestamp < old_info.probe_stream_start_time:
                    new_probe_stream_start_time = log_timestamp
                    new_probe_stream_end_time = old_info.probe_stream_end_time
                    new_manipulator_coordinates = manipulator_coordinates
                else:
                    new_probe_stream_start_time = (
                        old_info.probe_stream_start_time
                    )
                    new_probe_stream_end_time = log_timestamp
                    new_manipulator_coordinates = (
                        old_info.manipulator_coordinates
                    )
                probe_map[probe_name_no_prefix] = StageLogProbeInfo(
                    probe_stream_start_time=new_probe_stream_start_time,
                    probe_stream_end_time=new_probe_stream_end_time,
                    manipulator_coordinates=new_manipulator_coordinates,
                )
        return cls(
            stream_start_time=stream_start_time,
            stream_end_time=stream_end_time,
            probe_map=probe_map,
            filename=filename,
        )


@dataclass(frozen=True)
class ParsedInformation:
    parsed_stage_logs: List[StageLogParsedInfo]
    session_start_time: datetime

    @property
    def session_end_time(self):
        session_end_time = max(
            [
                parsed_log.stream_end_time
                for parsed_log in self.parsed_stage_logs
            ]
        )
        return session_end_time


class EphysEtl(BaseEtl[OpenEphysSession, Dict[str, List[Path]]]):
    """This class contains the methods to write ephys session"""

    def __init__(
        self,
        input_sources: Dict[str, List[Path]],
        specific_model: OpenEphysSession,
        output_directory: Optional[Path] = None,
    ):
        """
        Class constructor for FIBEtl class.
        Parameters
        ----------
        input_sources : Dict[str, List[Path]]
          Locations of stage logs and settings.xml files. Can be defined like:
          {"stage_logs": [Path["newscale_main.csv"]],
          "settings_xml": [Path["settings_main.xml"]]}
        specific_model : OpenEphysSession
          A Session model that is missing required fields that need to
          be parsed from files.
        output_directory : Optional[Path]
          The directory where to save the metadata file. Default is None.
        """
        super().__init__(
            output_directory=output_directory,
            specific_model=specific_model,
            input_sources=input_sources,
        )

    def _extract(self) -> RawInformation:
        stage_logs = []
        openephys_logs = []
        for stage_log in self.input_sources["stage_logs"]:
            stage_logs.append(StageLog.from_csv_file(stage_log))
        for openephys in self.input_sources["settings_xml"]:
            openephys_logs.append(OpenEphysLog.from_xml_file(openephys))
        # TODO: Parse only the necessary information needed from the sources?
        return RawInformation(
            stage_logs=stage_logs, openephys_logs=openephys_logs
        )

    # @staticmethod
    # def _update_probe_map(probe_map: Dict[str, StageLogProbeInfo], row: StageLogRow) -> None:
    #     probe_name = row.probe_name_no_prefix
    #     map_key = probe_name
    #     if probe_map.get(map_key) is None:
    #         stream_start_time = row.log_timestamp
    #         stream_end_time = row.log_timestamp
    #         manipulator_coordinates = Coordinates3d(x=row.coordinate1, y=row.coordinate2, z=row.coordinate3)
    #         probe_map[map_key] = StageLogProbeInfo(
    #             stream_start_time=stream_start_time,
    #             stream_end_time=stream_end_time,
    #             manipulator_coordinates=manipulator_coordinates)
    #     else:
    #         old_info = probe_map[map_key]
    #         if old_info.probe_stream_start_time <= row.log_timestamp:
    #             manipulator_coordinates = old_info.manipulator_coordinates
    #             stream_start_time = old_info.probe_stream_start_time
    #             stream_end_time = row.log_timestamp
    #         else:
    #             manipulator_coordinates = Coordinates3d(
    #                 x=row.coordinate1,
    #                 y=row.coordinate2,
    #                 z=row.coordinate3
    #             )
    #             stream_start_time = row.log_timestamp
    #             stream_end_time = old_info.probe_stream_end_time
    #         probe_map[map_key] = StageLogProbeInfo(
    #             stream_start_time=stream_start_time,
    #             stream_end_time=stream_end_time,
    #             manipulator_coordinates=manipulator_coordinates)
    #     return None

    @staticmethod
    def _parse_stage_logs(raw_info: RawInformation) -> ParsedInformation:
        session_start_time_str = (
            raw_info.openephys_logs[0]
            .contents.getElementsByTagName("DATE")[0]
            .firstChild.nodeValue
        )
        session_start_time = datetime.strptime(
            session_start_time_str, "%d %b %Y %H:%M:%S"
        )
        parsed_stage_logs = []
        for stage_log in raw_info.stage_logs:
            parsed_stage_logs.append(
                StageLogParsedInfo.from_stage_log(stage_log=stage_log)
            )
        return ParsedInformation(
            session_start_time=session_start_time,
            parsed_stage_logs=parsed_stage_logs,
        )

    def _transform(self, extracted_source: RawInformation) -> Session:
        """
        Transforms data into a Session model
        Parameters
        ----------
        extracted_source : Optional[str]
          In the future, we'll need to read and parse files directly.

        Returns
        -------
        Session

        """

        parsed_info = self._parse_stage_logs(raw_info=extracted_source)
        updated_model = self.specific_model.model_copy(deep=True)

        updated_model.session_start_time = parsed_info.session_start_time
        updated_model.session_end_time = parsed_info.session_end_time

        data_streams = updated_model.data_streams
        for data_stream, parsed_stage_log_info in zip(
            data_streams, parsed_info.parsed_stage_logs
        ):
            data_stream.stream_start_time = (
                parsed_stage_log_info.stream_start_time
            )
            data_stream.stream_end_time = parsed_stage_log_info.stream_end_time
            probe_map = parsed_stage_log_info.probe_map
            ephys_modules = data_stream.ephys_modules
            for ephys_module in ephys_modules:
                probe_name = ephys_module.ephys_probes[0].name
                probe_info = probe_map.get(probe_name)
                manipulator_coordinates = (
                    None
                    if probe_info is None
                    else probe_info.manipulator_coordinates
                )
                ephys_module.manipulator_coordinates = manipulator_coordinates

        # TODO: If model does not validate return object as is?
        return Session.model_validate(updated_model.model_dump())
