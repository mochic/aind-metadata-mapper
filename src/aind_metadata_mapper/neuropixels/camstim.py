"""Grabs all device managed by camstim via camstim config file
"""
import datetime
# from aind_data_schema import device, rig

from . import utils, NeuropixelsRigException


# class CamstimMonitor(
#     device.Monitor,
#     meta=utils.AllOptionalMeta,
#     required_fields=[
#         "name",
#         "brightness",
#         "contrast",
#     ]
# ):
#     """
#     """

# class CamstimRewardCalibration(
#     device.Calibration,
#     meta=utils.AllOptionalMeta,
#     required_fields=[
#         "name",
#         "channels",
#     ]
# ):
#     """
#     """


# CamstimMeta = tuple[CamstimMonitor, list[device.Calibration]]  # monitor settings, daq devices, water calibration

# def extract(content: str) -> CamstimMeta:
#     parsed = yaml.safe_load(content)
#     stim = parsed.get("Stim", {})
#     monitor = CamstimMonitor(
#         name="visual_stimulus",
#         contrast=stim.get("monitor_contrast"),
#         brightness=stim.get("monitor_brightness"),
#     )
#     calibrations = list(map(
#         lambda water_calibration, idx: CamstimRewardCalibration(
#             calibration_date=water_calibration["date"],
#             device_name=f"Reward delivery {idx}",
#             output={
#                 "intercept": water_calibration["intercept"],
#                 "slope": water_calibration["slope"],
#             }
#         ),
#         parsed.get("shared", {}).get("water_calibrations", [])
#     ))
#     return monitor, calibrations


def transform(
    config: dict,
    current: dict,
    monitor_name: str,
    reward_delivery_name: str,
) -> None:
    stim = config.get("Stim", {})
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
        raise NeuropixelsRigException(
            "No water calibrations found for reward delivery: %s" %
            reward_delivery_name
        )

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
        "description": "Solenoid water calibration."
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

    # for stimulus_device in current["stimulus_devices"]:
    #     if stimulus_device["device_type"] == "Monitor" \
    #         and stimulus_device["name"] == monitor_name:
    #             updated_stimulus_devices.append(utils.update_model_dict(
    #                  stimulus_device,
    #                  monitor,
    #             ))
    #     else:
    #          updated_stimulus_devices.append(stimulus_device.dict())

    # calibrations = list(map(
    #     lambda water_calibration, idx: CamstimRewardCalibration(
    #         calibration_date=water_calibration["date"],
    #         device_name=f"Reward delivery {idx}",
    #         output={
    #             "intercept": water_calibration["intercept"],
    #             "slope": water_calibration["slope"],
    #         }
    #     ),
    #     config.get("shared", {}).get("water_calibrations", [])
    # ))

    # updated_stimulus_devices = []
    # for stimulus_device in current["stimulus_devices"]:
    #     if stimulus_device["device_type"] == "Monitor" \
    #         and stimulus_device["name"] == monitor_name:
    #             updated_stimulus_devices.append(utils.update_model_dict(
    #                  stimulus_device,
    #                  monitor,
    #             ))
    #     else:
    #          updated_stimulus_devices.append(stimulus_device.dict())

    # updated_calibrations = []
    # for calibration in current["calibrations"]:
    #      for water_calibration in water_calibrations:
    #         if calibration.device_name == water_calibration.device_name:
    #              updated = utils.merge_models(
                      
    #              )
    

    # return updated_rig
# def extract_transform(current: rig.Rig, **overrides): 
#     current_dict = current.dict()
