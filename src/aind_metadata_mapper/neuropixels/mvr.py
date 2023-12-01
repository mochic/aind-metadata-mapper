import pydantic
import configparser
from aind_data_schema import device

from . import NeuropixelsRigException


class MVRCamera(pydantic.BaseModel):

    assembly_name: str
    serial_number: str
    height: int
    width: int
    frame_rate: float


def extract(content: str, mapping: dict) -> list[MVRCamera]:
    """Extracts camera-related information from MPE mvr config.
    """
    config = configparser.ConfigParser()
    config.read_string(content)

    frame_rate = float(
        config["CAMERA_DEFAULT_CONFIG"]["frames_per_second"]
    )
    height = int(config["CAMERA_DEFAULT_CONFIG"]["height"])
    width = int(config["CAMERA_DEFAULT_CONFIG"]["width"])

    extracted = []
    for mvr_name, assembly_name in mapping.items():
        try:
            extracted.append(
                MVRCamera(
                    assembly_name=assembly_name,
                    serial_number="".join(config[mvr_name]["sn"]),
                    height=height,
                    width=width,
                    frame_rate=frame_rate,
                )
            )
        except KeyError:
            raise NeuropixelsRigException(
                "No camera found for: %s in mvr.ini" %
                mvr_name
            )
    return extracted


def transform(
        camera: MVRCamera,
        manufacturer: str,
        data_interface: str,
        computer_name: str,
        chroma: str,
        **overloads
) -> device.Camera:
    return device.Camera(
        name=camera.assembly_name,
        serial_number=camera.serial_number,
        pixel_height=camera.height,
        pixel_width=camera.width,
        size_unit="pixel",
        max_frame_rate=camera.frame_rate,
        manufacturer=manufacturer,
        data_interface=data_interface,
        computer_name=computer_name,
        chroma=chroma,
        **overloads
    )
