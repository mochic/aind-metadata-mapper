from aind_data_schema import device, rig

from . import utils


# class CamstimDAQDevice(
#     device.DAQDevice,
#     meta=utils.AllOptionalMeta,
#     required_fields=[
#         "channels",
#     ]
# ):
#     """
#     """


# def extract(content: str) -> CamstimDAQDevice:
#     pass


# def transform(daq: CamstimDAQDevice, current: rig.Rig) -> None:
#     pass