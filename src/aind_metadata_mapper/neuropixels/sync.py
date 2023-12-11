import yaml
import pydantic
import typing 

# from aind_data_schema import device, rig

from . import utils, NeuropixelsRigException


# class SyncSettings(pydantic.BaseModel):

#     name: str
#     freq: float
#     line_labels: list[tuple[int, str]]


# class SyncDAQChannel(
#     device.DAQChannel,
#     metaclass=utils.AllOptionalMeta,
#     required_fields=[
#         "device_name",
#         "channel_name",
#         "channel_index",
#         "sample_rate",
#     ]
# ):
#     """
#     """


# def extract(content: str) -> list[SyncDAQChannel]:
#     """Extracts DAQ-related information from MPE sync config.
#     """
#     config = yaml.safe_load(content)
#     return [
#         SyncDAQChannel(
#             channel_name=name,
#             channel_type="Digital Input",
#             device_name=config["device"],
#             event_based_sampling=False,
#             channel_index=line,
#             sample_rate=config["freq"],
#             sample_rate_unit="hertz",
#         )
#         for line, name in config["line_labels"].items()
#     ]


# def transform(
#         sync_daq_channels: list[SyncDAQChannel],
#         current_rig: rig.Rig,
#         sync_name: str,
# ) -> list[device.DAQChannel]:
#     for daq in current_rig.daqs:
#         if daq.name == sync_name:
#             daq.channels = [
#                 device.DAQChannel.parse_obj(sync_daq_channel.dict())
#                 for sync_daq_channel in sync_daq_channels
#             ]
#             break
#     else:
#         raise NeuropixelsRigException(
#             "Sync daq not found on current rig. name=%s" % sync_name
#         )
#     return current_rig

def transform(
    config: dict,
    current: dict,
    sync_name: str,
) -> None:
    for daq in current["daqs"]:
        if daq["name"] == sync_name:
            daq["channels"] = [
                {
                    "channel_name": name,
                    "channel_type": "Digital Input",
                    "device_name": config["device"],
                    "event_based_sampling": False,
                    "channel_index": line,
                    "sample_rate": config["freq"],
                    "sample_rate_unit": "hertz"
                }
                for line, name in config["line_labels"].items()
            ]
            break
    else:
        raise NeuropixelsRigException(
            "Sync daq not found on current rig. name=%s" % sync_name
        )
