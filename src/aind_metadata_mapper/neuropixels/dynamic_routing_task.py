import pydantic
import typing
import h5py
import logging
import datetime
import numpy as np
from aind_data_schema.core import rig
from aind_data_schema.models import devices
from . import directory_context_rig


logger = logging.getLogger(__name__)


class ExtractContext(pydantic.BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    current: rig.Rig
    task: h5py.File


SUPPORTED_VERSIONS = [
    b'https://raw.githubusercontent.com/samgale/DynamicRoutingTask//9ea009a6c787c0049648ab9a93eb8d9df46d3f7b/DynamicRouting1.py',
]


class DynamicRoutingTaskRigEtl(directory_context_rig.DirectoryContextRigEtl):

    def __init__(self, 
            *args,
            task_resource_name: str = "DynamicRoutingTask.hdf5",
            monitor_name: str = "Stim",
            speaker_name: str = "Speaker",
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.task_resource_name = task_resource_name
        self.monitor_name = monitor_name
        self.speaker_name = speaker_name

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            task=h5py.File(
                self.input_source / self.task_resource_name,
                "r",
            )
        )

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        version = extracted_source.task["githubTaskScript"][()]
        if version not in SUPPORTED_VERSIONS:
            logger.warn(
                f"Unsupported task version: {version}",
            )

        # find replace
        daqs = [
            devices.DAQDevice(
                name="Behavior",
                manufacturer=devices.Manufacturer.NATIONAL_INSTRUMENTS,
                computer_name="127.0.0.1",
                data_interface=devices.DataInterface.USB,
                channels=[
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
            ),
            devices.DAQDevice(
                name="BehaviorSync",
                manufacturer=devices.Manufacturer.NATIONAL_INSTRUMENTS,
                computer_name="127.0.0.1",
                data_interface=devices.DataInterface.PCIE,
                channels=[
                    devices.DAQChannel(
                        device_name="BehaviorSync",
                        channel_name="frame_received",
                        channel_type=devices.DaqChannelType.DO,
                        port=extracted_source.task["frameSignalLine"][0],
                        channel_index=extracted_source.task["frameSignalLine"][1],
                    ),
                    devices.DAQChannel(
                        device_name="BehaviorSync",
                        channel_name="acquisition",
                        channel_type=devices.DaqChannelType.DO,
                        port=extracted_source.task["acquisitionSignalLine"][0],
                        channel_index=extracted_source.task["acquisitionSignalLine"][1],
                    ),
                ]
            ),
        ]

        opto_channels = extracted_source.task["optoChannels"]
        if opto_channels:
            opto_daq_device_name = "Opto"
            opto_daq = devices.DAQDevice(
                name=opto_daq_device_name,
                manufacturer=devices.Manufacturer.NATIONAL_INSTRUMENTS,
                computer_name="127.0.0.1",
                data_interface=devices.DataInterface.ETH,
                channels=[],
            )
            channels = [
                ch for dev in opto_channels
                for ch in opto_channels[dev]
                if not np.isnan(ch)
            ]
            sample_rate = float(extracted_source.task["optoSampleRate"][()])
            for idx, channel in enumerate(range(max(channels))):
                opto_daq.channels.append(
                    devices.DAQChannel(
                        device_name=opto_daq_device_name,
                        channel_name=f"{opto_daq_device_name} #{idx}",
                        channel_type=devices.DaqChannelType.AO,
                        port=0,
                        channel_index=channel,
                        sample_rate=sample_rate,
                    )
                )
            daqs.append(opto_daq)

        # find replace daqs
        for idx, current_daq in enumerate(extracted_source.current.daqs):
            for d_idx, daq in enumerate(daqs):
                if daq.name == current_daq.name:
                    extracted_source.current.daqs[idx] = daqs.pop(d_idx)
        extracted_source.current.daqs.extend(daqs)  # append daqs that werent already present 

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
        sound_calibration = devices.Calibration(
            calibration_date=datetime.datetime.now(),
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
        )
        for idx, current_calibration in enumerate(extracted_source.current.calibrations):
            if sound_calibration.device_name == current_calibration.device_name:
                extracted_source.current.calibrations[idx] = sound_calibration
                break
        else:
            extracted_source.current.calibrations.append(sound_calibration)

        # can't add reward calibration yet, due to aind-data-schema reward delivery bug
        return super()._transform(extracted_source.current)
