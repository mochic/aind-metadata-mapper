import logging
import pydantic
import configparser
from aind_data_schema import device, rig

from . import utils, NeuropixelsRigException


logger = logging.getLogger(__name__)


# class MVRCamera(pydantic.BaseModel):

#     assembly_name: str
#     serial_number: str
#     height: int
#     width: int
#     frame_rate: float

class MVRCamera(
    device.Camera,
    metaclass=utils.AllOptionalMeta,
    required_fields=[
        "name",
        "serial_number",
        "pixel_height",
        "pixel_width",
        "size_unit",
    ]
):
    """
    """

class MVRCameraAssembly(
    rig.CameraAssembly,
    metaclass=utils.AllOptionalMeta,
    required_fields=[
        "camera_assembly_name",
    ]
):
    """
    """
    camera: MVRCamera


def extract(content: str, mapping: dict) -> list[MVRCamera]:
    """Extracts camera-related information from MPE mvr config.
    """
    config = configparser.ConfigParser()
    config.read_string(content)

    # doesnt return a correct value?
    # frame_rate = float(
    #     config["CAMERA_DEFAULT_CONFIG"]["frames_per_second"]
    # )
    height = int(config["CAMERA_DEFAULT_CONFIG"]["height"])
    width = int(config["CAMERA_DEFAULT_CONFIG"]["width"])

    extracted = []
    for mvr_name, assembly_name in mapping.items():
        try:
            extracted.append(
                MVRCamera(
                    name=assembly_name,
                    serial_number="".join(config[mvr_name]["sn"]),
                    pixel_height=height,
                    pixel_width=width,
                    size_unit="pixel",
                )
            )
        except KeyError:
            raise NeuropixelsRigException(
                "No camera found for: %s in mvr.ini" %
                mvr_name
            )
    return extracted


def transform(
        mvr_cameras: list[MVRCamera],
        current: rig.Rig,

) -> None:
    for mvr_camera in mvr_cameras:
        # camera assembly name is assumed to be the same as child camera name
        matches = filter(
            lambda camera_assembly: \
                camera_assembly.camera_assembly_name == mvr_camera.name,
            current.cameras,
        )

        try:
            matching_camera_assembly = next(matches)
            utils.merge_devices(
                matching_camera_assembly.camera,
                mvr_camera,
            )
        except StopIteration:
            raise NeuropixelsRigException(
                "Matching rig camera name not found. mvr_camera.name=%s"
                % mvr_camera.name
            )


    # return device.Camera(
    #     name=camera.assembly_name,
    #     serial_number=camera.serial_number,
    #     pixel_height=camera.height,
    #     pixel_width=camera.width,
    #     size_unit="pixel",
    #     max_frame_rate=camera.frame_rate,
    #     manufacturer=manufacturer,
    #     data_interface=data_interface,
    #     computer_name=computer_name,
    #     chroma=chroma,
    #     **overloads
    # )

class MVRMapping(pydantic.BaseModel):

    pass


def extract_transform(
    content: str,
    mapping: dict,
    current_dict: dict,
) -> dict:
    config = configparser.ConfigParser()
    config.read_string(content)

    # doesnt return a correct value?
    # frame_rate = float(
    #     config["CAMERA_DEFAULT_CONFIG"]["frames_per_second"]
    # )
    height = int(config["CAMERA_DEFAULT_CONFIG"]["height"])
    width = int(config["CAMERA_DEFAULT_CONFIG"]["width"])

    extracted = []
    for mvr_name, assembly_name in mapping.items():
        try:
            extracted.append(
                MVRCamera(
                    name=assembly_name,
                    serial_number="".join(config[mvr_name]["sn"]),
                    pixel_height=height,
                    pixel_width=width,
                    size_unit="pixel",
                )
            )
        except KeyError:
            raise NeuropixelsRigException(
                "No camera found for: %s in mvr.ini" %
                mvr_name
            )