import typing
import logging
import datetime
import numpy as np
import pathlib
import h5py  # type: ignore
from aind_data_schema.core import rig  # type: ignore
from aind_data_schema.models import devices  # type: ignore
from . import neuropixels_rig, utils


logger = logging.getLogger(__name__)


class ExtractContext(neuropixels_rig.NeuropixelsRigContext):

    task: typing.Any


SUPPORTED_VERSIONS = [
    b'https://raw.githubusercontent.com/samgale/DynamicRoutingTask//9ea009a6c787c0049648ab9a93eb8d9df46d3f7b/DynamicRouting1.py',
]


def extract_paired_values(h5_file: h5py.File, *paths: list[str]) -> \
        typing.Union[list[typing.Any], None]:
    values = []
    for path in paths:
        value = None
        try:
            value = None
            for part in path:
                value = h5_file[part]
            
            if isinstance(value, h5py.Dataset):
                values.append(value[()])
            else:
                values.append(value)
        except KeyError:
            logger.warning(f"Key not found: {part}")
            return None

    return values


class DynamicRoutingTaskRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    """DynamicRouting rig ETL class. Extracts information from rig-related 
    files"""
    
    def __init__(self, 
            input_source: pathlib.Path,
            output_directory: pathlib.Path,
            task_source: pathlib.Path,
            monitor_name: str = "Stim",
            speaker_name: str = "Speaker",
            behavior_daq_name: str = "Behavior",
            behavior_sync_daq_name: str = "BehaviorSync",
            opto_daq_name: str = "Opto",
            reward_delivery_name: str = "Reward delivery",
            laser_name: str = "Laser Assembly #0 Laser #0",
            sound_calibration_date: typing.Optional[datetime.date] = None,
            reward_calibration_date: typing.Optional[datetime.date] = None,
            laser_calibration_date: typing.Optional[datetime.date] = None,
            **kwargs,
    ):
        super().__init__(input_source, output_directory, **kwargs)
        self.task_source = task_source
        self.monitor_name = monitor_name
        self.speaker_name = speaker_name
        self.behavior_daq_name = behavior_daq_name
        self.behavior_sync_daq_name = behavior_sync_daq_name
        self.opto_daq_name = opto_daq_name
        self.reward_delivery_name = reward_delivery_name
        self.sound_calibration_date = sound_calibration_date
        self.reward_calibration_date = reward_calibration_date
        self.laser_name = laser_name
        self.laser_calibration_date = laser_calibration_date

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            task=h5py.File(self.task_source, "r"),
        )

    # def _extract_daq_channel(
    #         self,
    #         extracted_source: ExtractContext,
    #     ) -> devices.DAQChannel:
    #     pass

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        extracted_version = extract_paired_values(
            extracted_source.task,
            ["githubTaskScript"],
        )
        if extracted_version is not None:
            version = extracted_version[0]
            if version not in SUPPORTED_VERSIONS:
                logger.warning(
                    f"Unsupported task version: {version}",
                )

        # find replace
        behavior_daq_channels = []

        extracted_reward_line = extract_paired_values(
            extracted_source.task,
            ["rewardLine"],
        )
        if extracted_reward_line is not None:
            logger.debug("Updating reward line on %s" % self.behavior_daq_name)
            port, channel_index = extracted_reward_line[0]
            behavior_daq_channels.append(
                devices.DAQChannel(
                    device_name=self.behavior_daq_name,
                    channel_name="solenoid",
                    channel_type=devices.DaqChannelType.DO,
                    port=port,
                    channel_index=channel_index,
                )
            )

        extracted_reward_sound_line = extract_paired_values(
            extracted_source.task,
            ["rewardSoundLine"],
        )
        if extracted_reward_sound_line is not None:
            logger.debug(
                "Updating reward sound line on %s" % self.behavior_daq_name)
            port, channel_index = extracted_reward_sound_line[0]
            behavior_daq_channels.append(
                devices.DAQChannel(
                    device_name=self.behavior_daq_name,
                    channel_name="reward_sound",
                    channel_type=devices.DaqChannelType.DO,
                    port=port,
                    channel_index=channel_index,
                )
            )

        extracted_lick_line = extract_paired_values(
            extracted_source.task,
            ["lickLine"],
        )
        if extracted_lick_line is not None:
            logger.debug(
                "Updating lick line on %s" % self.behavior_daq_name)
            port, channel_index = extracted_lick_line[0]
            behavior_daq_channels.append(
                devices.DAQChannel(
                    device_name=self.behavior_daq_name,
                    channel_name="lick",
                    channel_type=devices.DaqChannelType.DI,
                    port=port,
                    channel_index=channel_index,
                )
            )

        behavior_sync_daq_channels = []

        extracted_frame_signal_line = extract_paired_values(
            extracted_source.task,
            ["frameSignalLine"],
        )
        if extracted_frame_signal_line is not None:
            logger.debug(
                "Updating frame signal line on %s" % 
                self.behavior_sync_daq_name)
            port, channel_index = extracted_frame_signal_line[0]
            behavior_sync_daq_channels.append(
                devices.DAQChannel(
                    device_name=self.behavior_sync_daq_name,
                    channel_name="stim_frame",
                    channel_type=devices.DaqChannelType.DO,
                    port=port,
                    channel_index=channel_index,
                )
            )

        extracted_acquisition_signal_line = extract_paired_values(
            extracted_source.task,
            ["acquisitionSignalLine"],
        )
        if extracted_acquisition_signal_line is not None:
            logger.debug(
                "Updating acquisition signal line on %s" % 
                self.behavior_sync_daq_name)
            port, channel_index = extracted_acquisition_signal_line[0]
            behavior_sync_daq_channels.append(
                devices.DAQChannel(
                    device_name=self.behavior_sync_daq_name,
                    channel_name="stim_running",
                    channel_type=devices.DaqChannelType.DO,
                    port=port,
                    channel_index=channel_index,
                )
            )

        opto_daq_channels = []

        extracted_opto = extract_paired_values(
            extracted_source.task,
            ["optoChannels"],
            ["optoSampleRate"],
        )

        if extracted_opto is not None:
            logger.debug("Updating %s" % self.opto_daq_name)
            opto_channels, opto_sample_rate = extracted_opto
            opto_daq_channels = []
            if opto_channels:
                channels = [
                    ch for dev in opto_channels
                    for ch in opto_channels[dev]
                    if not np.isnan(ch)
                ]
                sample_rate = float(opto_sample_rate)
                for idx, channel in enumerate(range(max(channels))):
                    opto_daq_channels.append(
                        devices.DAQChannel(
                            device_name=self.opto_daq_name,
                            channel_name=f"{self.opto_daq_name} #{idx}",
                            channel_type=devices.DaqChannelType.AO,
                            port=0,
                            channel_index=channel,
                            sample_rate=sample_rate,
                        )
                    )

        # find replace daqs
        for idx, daq in enumerate(extracted_source.current.daqs):
            if daq.name == self.opto_daq_name:
                daq.channels.extend(opto_daq_channels)
            elif daq.name == self.behavior_daq_name:
                daq.channels.extend(behavior_daq_channels)
            elif daq.name == self.behavior_sync_daq_name:
                daq.channels.extend(behavior_sync_daq_channels)
            else:
                pass

        # monitor information
        extracted_monitor_values = extract_paired_values(
            extracted_source.task,
            ["monDistance"],
            ["monSizePix"],
        )
        if extracted_monitor_values is not None:
            monitor_distance, monitor_size = extracted_monitor_values
            for idx, device in \
                    enumerate(extracted_source.current.stimulus_devices):
                if device.name == "Stim" and device.device_type == "Monitor":
                    if monitor_distance is not None:
                        device.viewing_distance = float(monitor_distance)
                        device.viewing_distance_unit = devices.SizeUnit.CM
                    
                    if monitor_size is not None:
                        width, height = monitor_size
                        if not np.isnan(width) and not np.isnan(height):
                            device.width = int(width)
                            device.height = int(height)
                            device.size_unit = devices.SizeUnit.PX
                    
                    extracted_source.current.stimulus_devices[idx] = \
                        devices.Monitor.model_validate(
                            device.__dict__
                        )
                    break

        # wheel info
        extracted_wheel_radius = extract_paired_values(
            extracted_source.task,
            ["wheelRadius"],
        )
        if extracted_wheel_radius is not None:
            logger.debug("Updating wheel information")
            extracted_source.current.mouse_platform.radius = \
                extracted_wheel_radius[0]
            extracted_source.current.mouse_platform.radius_unit = \
                devices.SizeUnit.CM
            extracted_source.current.mouse_platform = \
                devices.Disc.model_validate(
                    extracted_source.current.mouse_platform.__dict__
                )

        # calibrations
        default_calibration_date = datetime.datetime.now()

        # sound
        extracted_sound_calibration_fit = extract_paired_values(
            extracted_source.task,
            ["soundCalibrationFit"],
        )
        if extracted_sound_calibration_fit is not None:
            logger.debug("Updating sound calibration")
            sound_calibration_fit  = extracted_sound_calibration_fit[0]
            utils.find_replace_or_append(
                extracted_source.current.calibrations,
                [
                    ("device_name", self.speaker_name),
                ],
                devices.Calibration(
                    calibration_date=self.sound_calibration_date or \
                        default_calibration_date,
                    device_name=self.speaker_name,
                    input={},
                    output={
                        "a": sound_calibration_fit[0],
                        "b": sound_calibration_fit[1],
                        "c": sound_calibration_fit[2],
                    },
                    description=(
                        "sound_volume = log(1 - ((dB - c) / a)) / b;"
                        "dB is sound pressure"
                    ),
                    notes=(
                        "Calibration date is a placeholder. "
                    ),
                ),
            )

        # water
        extracted_solenoid_open_time = extract_paired_values(
            extracted_source.task,
            ["solenoidOpenTime"],
        )

        if extracted_solenoid_open_time is not None:
            logger.debug("Updating reward delivery calibration")
            solenoid_open_time = extracted_solenoid_open_time[0]
            extracted_water_calibration_fit = extract_paired_values(
                extracted_source.task,
                ["waterCalibrationSlope"],
                ["waterCalibrationIntercept"],
            )
            if extracted_water_calibration_fit is not None:
                task_water_calibration_slope, task_water_calibration_intercept = \
                    extracted_water_calibration_fit
                if np.isnan(task_water_calibration_intercept):
                    water_calibration_intercept = 0
                else:
                    water_calibration_intercept = task_water_calibration_intercept
                if np.isnan(task_water_calibration_slope):
                    water_calibration_slope = 0
                else:
                    water_calibration_slope = task_water_calibration_slope
            else:
                water_calibration_intercept = 0
                water_calibration_slope = 0

            utils.find_replace_or_append(
                extracted_source.current.calibrations,
                [
                    ("device_name", self.reward_delivery_name),
                ],
                devices.Calibration(
                    calibration_date=self.reward_calibration_date or \
                        default_calibration_date,
                    device_name=self.reward_delivery_name,
                    input={
                        "intercept": water_calibration_intercept,
                        "slope": water_calibration_slope,
                    },
                    output={
                        "solonoid_open_time": solenoid_open_time,
                    },
                    description=(
                        "solenoid open time (ms) = slope * expected water volume (mL) + intercept;"
                        "licks is the number of lick events"
                    ),
                    notes=(
                        "Calibration date is a placeholder. "
                        "If intercept and slope are 0, "
                        "their requisite values are missing but "
                        "solenoid open time should still be accurate."
                    ),
                ),
            )

        return super()._transform(extracted_source.current)
