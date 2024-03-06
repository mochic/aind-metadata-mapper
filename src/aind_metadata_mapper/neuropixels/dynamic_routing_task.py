import typing
import logging
import datetime
import numpy as np
import pathlib
import h5py
from aind_data_schema.core import rig  # type: ignore
from aind_data_schema.models import devices  # type: ignore
from . import neuropixels_rig, utils


logger = logging.getLogger(__name__)


class ExtractContext(neuropixels_rig.NeuropixelsRigContext):

    task: typing.Any


SUPPORTED_VERSIONS = [
    b'https://raw.githubusercontent.com/samgale/DynamicRoutingTask//9ea009a6c787c0049648ab9a93eb8d9df46d3f7b/DynamicRouting1.py',
]


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

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        try:
            version = extracted_source.task["githubTaskScript"][()]
            if version not in SUPPORTED_VERSIONS:
                logger.warn(
                    f"Unsupported task version: {version}",
                )
        except KeyError:
            logger.warn("No task version found")

        # find replace
        behavior_daq_channels = [
            devices.DAQChannel(
                device_name="Behavior",
                channel_name="solenoid",
                channel_type=devices.DaqChannelType.DO,
                port=extracted_source.task["rewardLine"][0],
                channel_index=extracted_source.task["rewardLine"][1],
            ),
            devices.DAQChannel(
                device_name="Behavior",
                channel_name="reward_sound",
                channel_type=devices.DaqChannelType.DO,
                port=extracted_source.task["rewardSoundLine"][0],
                channel_index=extracted_source.task["rewardSoundLine"][1],
            ),
            devices.DAQChannel(
                device_name="Behavior",
                channel_name="lick",
                channel_type=devices.DaqChannelType.DI,
                port=extracted_source.task["lickLine"][0],
                channel_index=extracted_source.task["lickLine"][1],
            ),
        ]

        behavior_sync_daq_channels = [
            devices.DAQChannel(
                device_name="BehaviorSync",
                channel_name="stim_frame",
                channel_type=devices.DaqChannelType.DO,
                port=extracted_source.task["frameSignalLine"][0],
                channel_index=extracted_source.task["frameSignalLine"][1],
            ),
            devices.DAQChannel(
                device_name="BehaviorSync",
                channel_name="stim_running",
                channel_type=devices.DaqChannelType.DO,
                port=extracted_source.task["acquisitionSignalLine"][0],
                channel_index=extracted_source.task["acquisitionSignalLine"][1],
            ),
        ]

        task_opto_channels = extracted_source.task["optoChannels"]
        opto_daq_channels = []
        if task_opto_channels:
            opto_daq_device_name = "Opto"
            channels = [
                ch for dev in task_opto_channels
                for ch in task_opto_channels[dev]
                if not np.isnan(ch)
            ]
            sample_rate = float(extracted_source.task["optoSampleRate"][()])
            for idx, channel in enumerate(range(max(channels))):
                opto_daq_channels.append(
                    devices.DAQChannel(
                        device_name=opto_daq_device_name,
                        channel_name=f"{opto_daq_device_name} #{idx}",
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

        for idx, device in enumerate(extracted_source.current.stimulus_devices):
            if device.name == "Stim" and device.device_type == "Monitor":
                device.viewing_distance = \
                    float(extracted_source.task["monDistance"][()])
                device.viewing_distance_unit = devices.SizeUnit.CM
                device.height = int(extracted_source.task["monSizePix"][1])
                device.width = int(extracted_source.task["monSizePix"][0])
                device.size_unit = devices.SizeUnit.PX
                extracted_source.current.stimulus_devices[idx] = \
                    devices.Monitor.model_validate(
                        device.__dict__
                    )
                break

        extracted_source.current.mouse_platform.radius = \
            extracted_source.task["wheelRadius"][()]
        extracted_source.current.mouse_platform.radius_unit = \
            devices.SizeUnit.CM
        extracted_source.current.mouse_platform = devices.Disc.model_validate(
            extracted_source.current.mouse_platform.__dict__
        )

        # calibrations
        default_calibration_date = datetime.datetime.now()

        # sound
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
                    "a": extracted_source.task["soundCalibrationFit"][0],
                    "b": extracted_source.task["soundCalibrationFit"][1],
                    "c": extracted_source.task["soundCalibrationFit"][2],
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
        task_water_calibration_intercept = \
            extracted_source.task["waterCalibrationIntercept"][()]
        task_water_calibration_slope = \
            extracted_source.task["waterCalibrationSlope"][()]
        if np.isnan(task_water_calibration_intercept):
            water_calibration_intercept = 0
        else:
            water_calibration_intercept = task_water_calibration_intercept
        if np.isnan(task_water_calibration_slope):
            water_calibration_slope = 0
        else:
            water_calibration_slope = task_water_calibration_slope

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
                    "solonoid_open_time": extracted_source.task["solenoidOpenTime"][()],
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
