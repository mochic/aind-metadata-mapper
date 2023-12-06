"""Grabs all device managed by camstim via camstim config file
"""
from aind_data_schema import device, rig
import yaml

from . import utils


class CamstimMonitor(
    device.DAQDevice,
    meta=utils.AllOptionalMeta,
    required_fields=[
        "name",
        "channels",
    ]
):
    """
    """

class RewardDelivery(
    device.RewardDelivery,
    meta=utils.AllOptionalMeta,
    required_fields=[
        "name",
        "channels",
    ]
):
    """
    """


CamstimDevices = tuple[CamstimMonitor, device.Calibration]

def extract(content: str) -> CamstimDevices:
    parsed = yaml.safe_load(content)
    monitor = CamstimMonitor()


# def transform(daq: CamstimDAQDevice, current: rig.Rig) -> None:
#     pass