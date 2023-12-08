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


CamstimMeta = tuple[CamstimMonitor, list[device.Calibration]]  # monitor settings, daq devices, water calibration

def extract(content: str) -> CamstimMeta:
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


def transform(
        camstim_meta: CamstimMeta,
        monitor_name: str,
        rig_dict: dict,
) -> rig.Rig:
    monitor, water_calibrations = camstim_meta

    updated_stimulus_devices = []
    for stimulus_device in rig_dict["stimulus_devices"]:
        if stimulus_device["device_type"] == "Monitor" \
            and stimulus_device["name"] == monitor_name:
                updated_stimulus_devices.append(utils.update_model_dict(
                     stimulus_device,
                     monitor,
                ))
        else:
             updated_stimulus_devices.append(stimulus_device.dict())

    updated_calibrations = []
    for calibration in rig_dict.calibrations:
         for water_calibration in water_calibrations:
            if calibration.device_name == water_calibration.device_name:
                 updated = utils.merge_models(
                      
                 )
    

    return updated_rig
# def extract_transform(current: rig.Rig, **overrides): 
#     current_dict = current.dict()
