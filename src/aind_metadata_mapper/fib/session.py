"""Module to write valid OptoStim and Subject schemas"""

from datetime import datetime, timedelta
import re
from pathlib import Path
from typing import Optional, List

from aind_data_schema.core.session import (
    DetectorConfig,
    FiberConnectionConfig,
    Session,
    Stream, LIGHT_SOURCE_CONFIGS,
)
from aind_data_schema.models.modalities import Modality
from aind_data_schema.models.stimulus import (
    OptoStimulation,
    PulseShape,
    StimulusEpoch,
)
from pydantic_settings import BaseSettings
from pydantic import Field

from aind_metadata_mapper.core import BaseEtl


class UserSettings(BaseSettings):
    teensy_str: str = Field(
        ...,
        description=(
            "Parsed contents from teensy file. In the future, we can consider "
            "replacing this and just parse the file ourselves."
        )
    )
    # The following fields are required in the Session model, but can't be
    # parsed from raw files. The user will have to supply these.
    stream_start_time: datetime
    subject_id: str
    iacuc_protocol: str
    rig_id: str
    experimenter_full_name: List[str]
    mouse_platform_name: str
    active_mouse_platform: bool
    light_sources: List[LIGHT_SOURCE_CONFIGS]
    detectors: List[DetectorConfig]
    fiber_connections: List[FiberConnectionConfig]
    session_type: str
    notes: Optional[str] = Field(default=None)


class FIBEtl(BaseEtl[UserSettings]):
    """This class contains the methods to write OphysScreening data"""

    _dictionary_mapping = {
        "o": "OptoStim10Hz",
        "p": "OptoStim20Hz",
        "q": "OptoStim5Hz",
    }

    # Define regular expressions to extract the values
    command_regex = re.compile(r"Received command (\w)")
    frequency_regex = re.compile(r"OptoStim\s*([0-9.]+)")
    trial_regex = re.compile(r"OptoTrialN:\s*([0-9.]+)")
    pulse_regex = re.compile(r"PulseW\(um\):\s*([0-9.]+)")
    duration_regex = re.compile(r"OptoDuration\(s\):\s*([0-9.]+)")
    interval_regex = re.compile(r"OptoInterval\(s\):\s*([0-9.]+)")
    base_regex = re.compile(r"OptoBase\(s\):\s*([0-9.]+)")

    def __init__(
        self,
        additional_info: UserSettings,
        output_directory: Optional[Path] = None,
    ):
        """
        Class constructor for FIBEtl class.
        Parameters
        ----------
        additional_info : UserSettings
          Variables for a particular session that can't be parsed from files
          and need to be set manually.
        output_directory : Optional[Path]
          The directory where to save the metadata file. Default is None.
        """
        super().__init__(output_directory=output_directory, additional_info=additional_info)

    def _transform(self, extracted_source: Optional[str] = None) -> Session:
        """
        Parses params from teensy string and creates ophys session model
        Parameters
        ----------
        extracted_source : Optional[str]
          In the future, if we parse the teensy from files, we can change this.

        Returns
        -------
        Session

        """
        string_to_parse = self.additional_info.teensy_str
        start_datetime = self.additional_info.probe_stream_start_time

        # Use regular expressions to extract the values
        frequency_match = re.search(self.frequency_regex, string_to_parse)
        trial_match = re.search(self.trial_regex, string_to_parse)
        pulse_match = re.search(self.pulse_regex, string_to_parse)
        duration_match = re.search(self.duration_regex, string_to_parse)
        interval_match = re.search(self.interval_regex, string_to_parse)
        base_match = re.search(self.base_regex, string_to_parse)
        command_match = re.search(self.command_regex, string_to_parse)

        # Store the float values as variables
        frequency = int(frequency_match.group(1))
        trial_num = int(trial_match.group(1))
        pulse_width = int(pulse_match.group(1))
        opto_duration = float(duration_match.group(1))
        opto_interval = float(interval_match.group(1))
        opto_base = float(base_match.group(1))

        # maps stimulus_name from command
        command = command_match.group(1)
        stimulus_name = self._dictionary_mapping.get(command, "")

        # create opto stim instance
        opto_stim = OptoStimulation(
            stimulus_name=stimulus_name,
            pulse_shape=PulseShape.SQUARE,
            pulse_frequency=frequency,
            number_pulse_trains=trial_num,
            pulse_width=pulse_width,
            pulse_train_duration=opto_duration,
            pulse_train_interval=opto_interval,
            baseline_duration=opto_base,
            fixed_pulse_train_interval=True,  # TODO: Check this is right
        )

        # create stimulus presentation instance
        experiment_duration = (
            opto_base + opto_duration + (opto_interval * trial_num)
        )
        end_datetime = start_datetime + timedelta(
            seconds=experiment_duration
        )
        stimulus_epochs = StimulusEpoch(
            stimulus=opto_stim,
            stimulus_start_time=start_datetime,
            stimulus_end_time=end_datetime,
        )

        data_stream = [
            Stream(
                stream_start_time=start_datetime,
                stream_end_time=end_datetime,
                light_sources=self.additional_info.light_sources,
                stream_modalities=[Modality.FIB],
                mouse_platform_name=self.additional_info.mouse_platform_name,
                active_mouse_platform=self.additional_info.active_mouse_platform,
                detectors=self.additional_info.detectors,
                fiber_connections=self.additional_info.fiber_connections,
            )
        ]

        # and finally, create ophys session
        # TODO: Handle situations where session is invalid?
        ophys_session = Session(
            stimulus_epochs=[stimulus_epochs],
            subject_id=self.additional_info.subject_id,
            iacuc_protocol=self.additional_info.iacuc_protocol,
            session_start_time=start_datetime,
            session_end_time=end_datetime,
            rig_id=self.additional_info.rig_id,
            experimenter_full_name=self.additional_info.experimenter_full_name,
            session_type=self.additional_info.session_type,
            notes=self.additional_info.notes,
            data_streams=data_stream,
        )

        return ophys_session

    def _extract(self) -> None:
        """In the future, we can parse the teensy files if needed."""
        pass
