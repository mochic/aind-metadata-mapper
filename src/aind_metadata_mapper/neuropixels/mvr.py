import configparser

from . import NeuropixelsRigException


def transform(
    config: configparser.ConfigParser,
    mapping: dict,
    current_dict: dict,
) -> dict:
    default_config = config["CAMERA_DEFAULT_CONFIG"]
    height = int(default_config["height"])
    width = int(default_config["width"])

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