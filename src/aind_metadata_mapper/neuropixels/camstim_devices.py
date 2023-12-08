"""Grabs all device managed by camstim via camstim config file
"""
from aind_data_schema import device, rig
import yaml

from . import utils


class CamstimMonitor(
    device.Monitor,
    meta=utils.AllOptionalMeta,
    required_fields=[
        "name",
        "brightness",
        "contrast",
    ]
):
    """
    """

class CamstimRewardCalibration(
    device.Calibration,
    meta=utils.AllOptionalMeta,
    required_fields=[
        "name",
        "channels",
    ]
):
    """
    """


CamstimDevices = tuple[CamstimMonitor, list[device.Calibration]]  # monitor settings, daq devices, water calibration

def extract(content: str) -> CamstimDevices:
    parsed = yaml.safe_load(content)
    stim = parsed.get("Stim", {})
    monitor = CamstimMonitor(
        name="visual_stimulus",
        contrast=stim.get("monitor_contrast"),
        brightness=stim.get("monitor_brightness"),
    )
    calibrations = list(map(
        lambda water_calibration, idx: CamstimRewardCalibration(
            calibration_date=water_calibration["date"],
            device_name=f"Reward delivery {idx}",
            output={
                "intercept": water_calibration["intercept"],
                "slope": water_calibration["slope"],
            }
        ),
        parsed.get("shared", {}).get("water_calibrations", [])
    ))
    return monitor, calibrations

# def transform(daq: CamstimDAQDevice, current: rig.Rig) -> None:
#     pass

# def extract_transform(current: rig.Rig, **overrides): 
#     current_dict = current.dict()
