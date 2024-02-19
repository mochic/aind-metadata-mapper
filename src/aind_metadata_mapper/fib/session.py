"""Module to write valid OptoStim and Subject schemas"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from aind_data_schema.core.session import Session, Stream
from aind_data_schema.models.modalities import Modality
from aind_data_schema.models.stimulus import (
    OptoStimulation,
    PulseShape,
    StimulusEpoch,
)
from pydantic import Field

from aind_metadata_mapper.core import BaseEtl


class FibStream(Stream):
    """Overrides Stream class to mark some fields as Optional or sets
    defaults."""

    # Fields that will be set by file information
    stream_start_time: Optional[datetime] = Field(
        None, title="Stream start time"
    )
    stream_end_time: Optional[datetime] = Field(None, title="Stream stop time")
    stream_modalities: List[Modality.ONE_OF] = [Modality.FIB]


class FibSession(Session):
    """Overrides Session class to mark some fields as Optional or sets
    defaults."""

    # Fields that will be set by file information
    data_streams: List[FibStream]


class FIBEtl(BaseEtl[FibSession, Dict[str, str]]):
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
        teensy_str: str,
        specific_model: FibSession,
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
        super().__init__(
            input_sources={"teensy_str": teensy_str},
            output_directory=output_directory,
            specific_model=specific_model,
        )

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
        string_to_parse = self.input_sources["teensy_str"]
        updated_session = self.specific_model.model_copy(deep=True)
        # start_datetime = self.additional_info.probe_stream_start_time

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
        updated_session.session_end_time = (
            updated_session.session_start_time
            + timedelta(seconds=experiment_duration)
        )

        stimulus_epoch = StimulusEpoch(
            stimulus=opto_stim,
            stimulus_start_time=updated_session.session_start_time,
            stimulus_end_time=updated_session.session_end_time,
        )

        data_stream = updated_session.data_streams[0]
        data_stream.stream_start_time = updated_session.session_start_time
        data_stream.stream_end_time = updated_session.session_end_time
        updated_session.stimulus_epochs = [stimulus_epoch]

        # and finally, create ophys session
        # TODO: Handle situations where session is invalid?
        return Session.model_validate(updated_session.model_dump())

    def _extract(self) -> None:
        """In the future, we can parse the teensy files if needed."""
        pass  # pragma: no cover
