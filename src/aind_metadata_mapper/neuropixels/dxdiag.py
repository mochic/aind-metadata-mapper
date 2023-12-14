import re
from xml.etree import ElementTree

from . import utils, NeuropixelsRigException


def transform_monitor(
    config: ElementTree,
    current_dict: dict,
    monitor_name: str,
) -> None:
    """
    Notes
    -----
    modifies current_dict inplace.
    """
    modes = list(utils.find_elements(config, "currentmode"))
    height = None
    width = None
    if len(modes) > 0:
        parsed_mode = re.match(
            r"(\d*) x (\d*) (\(\d{2} bit\)) \((\d*)Hz\)",
            modes[0].text
        )
        if parsed_mode:
            height = int(parsed_mode[2])
            width = int(parsed_mode[1])

    models = list(utils.find_elements(config, "monitormodel"))
    if len(models) < 1:
        model = None
    else:
        model = models[0].text

    for stimulus_device in current_dict["stimulus_devices"]:
        if stimulus_device["device_type"] == "Monitor" and \
            stimulus_device["name"] == monitor_name:
                if not height is None and \
                    not width is None:
                    stimulus_device["height"] = height
                    stimulus_device["width"] = width
                    stimulus_device["size_unit"] = "pixel"
                if model:
                    stimulus_device["model"] = model
                break
    else:
        raise NeuropixelsRigException("Failed to find monitor in rig.")


def transform_audio(
    config: ElementTree,
    current_dict: dict,
    soundcard_names: str,
):
    pass