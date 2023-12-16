import logging
import pydantic
import configparser

from . import NeuropixelsRigException


logger = logging.getLogger(__name__)


def transform(
    config: configparser.ConfigParser,
    mapping: dict,
    camera_hostname: str,
    current_dict: dict,
) -> dict:
    height = int(config["CAMERA_DEFAULT_CONFIG"]["height"])
    width = int(config["CAMERA_DEFAULT_CONFIG"]["width"])

    for mvr_name, assembly_name in mapping.items():
        try:
            mvr_camera_config = config[mvr_name]
        except KeyError:
            raise NeuropixelsRigException(
                "No camera found for: %s in mvr config." %
                mvr_name
            )
        serial_number = "".join(mvr_camera_config["sn"])
        for camera_assembly in current_dict["cameras"]:
            if camera_assembly["camera_assembly_name"] == assembly_name:
                camera_assembly["camera"] = {
                    **camera_assembly["camera"],
                    "computer_name": camera_hostname,
                    "serial_number": serial_number,
                    "pixel_height": height,
                    "pixel_width": width,
                    "size_unit": "pixel",
                }
                break
        else:
            raise NeuropixelsRigException(
                "No camera assembly found for: %s in rig." %
                assembly_name
            )
    
    return current_dict