"""Grabs all device managed by camstim via camstim config file
"""
import datetime
import logging

from . import utils, NeuropixelsRigException


logger = logging.getLogger(__name__)


def transform(
    config: dict,
    current: dict,
    monitor_name: str,
    reward_delivery_name: str,
) -> None:
    stim = config["shared"].get("Stim", {})
    # update monitor settings
    utils.find_update(
        current["stimulus_devices"],
        filters=[
          ("name", monitor_name),
        ],
        contrast=stim.get("monitor_contrast"),
        brightness=stim.get("monitor_brightness"),
    )

    try:
        water_calibration = config["shared"]["water_calibration"][reward_delivery_name]
    except KeyError:
        logger.debug(
            "No water calibrations found for reward delivery: %s" %
            reward_delivery_name
        )
        return

    # update water calibrations
    water_calibration = {
        "calibration_date": datetime.datetime.strptime(
            water_calibration["datetime"],
            "%m/%d/%Y %H:%M:%S"
        ),
        "device_name": reward_delivery_name,
        "output": {
            "intercept": water_calibration["intercept"],
            "slope": water_calibration["slope"],
        },
        "description": (
            "Solenoid water calibration. Standardizes solenoid" 
            "open time to volume of water dispensed."
        ),
    }

    try:
        utils.find_update(
            current["calibrations"],
            filters=[
                ("device_name", reward_delivery_name),
            ],
            **water_calibration
        )
    except NeuropixelsRigException:  # TODO: just do this a normal way
        current["calibrations"].append(water_calibration)
