import json
import pathlib
import configparser
import typing
import pydantic
from aind_data_schema import device, rig

from ..core import BaseEtl


class MVRException(Exception):
    """General error for MVR."""


# class PartialCameraAssembly(device.CameraAssembly):

#     camera: typing.Optional[device.Camera] = None


# class MVRMeta(pydantic.BaseModel):

#     host: str
#     partials: list[tuple[str, PartialCameraAssembly]]


# class MVRMeta(pydantic.BaseModel):

#     host: str
#     partials: list[tuple[str, dict]]



# MVRMeta = tuple[str, list[tuple[str, dict]]]
MVRCameraInfo = tuple[str, str, int, int, float]  # serial number, height, width, frame rate
MVRContext = tuple[MVRCameraInfo, dict]  # mvr info, partial camera

class MVREtl(BaseEtl):

    def __init__(
        self,
        input_source: pathlib.Path,
        output_directory: pathlib.Path,
    ):
        """Class constructor for transforming MVR config and metadata into CameraAssembly.
        
        Parameters
        ----------
        input_source : Path
          Can be a string or a Path
        output_directory : Path
          The directory where to save the json files.
        """
        super().__init__(input_source, output_directory)

    def _extract(self) -> MVRContext:
        if not self.input_source.is_dir():
            raise Exception("Input source is not a directory. %s" % self.input_source)
        
        mvr_path = self.input_source / "mvr.ini"
        if not mvr_path.exists():
            raise Exception("%s not found." % mvr_path)

        # partial_filename = "camera.partial.json"
        partial_path = self.input_source / "camera.partial.json"
        if not partial_path.exists():
            raise Exception("%s not found." % partial_path)
        
        mvr_name, partial = json.loads(partial_path.read_text())
        extracted = self._extract_mvr(mvr_path.read_text(), mvr_name)
        return (extracted, partial)
    
    def _extract_mvr(self, mvr_contents: str, camera_name: str) -> MVRCameraInfo:        
        config = configparser.ConfigParser()
        config.read_string(mvr_contents)

        try:
            return (
                # camera_name,
                # "".join(config[camera_name]["label"]),
                "".join(config[camera_name]["sn"]),
                int(config["CAMERA_DEFAULT_CONFIG"]["height"]),
                int(config["CAMERA_DEFAULT_CONFIG"]["width"]),
                float(config["CAMERA_DEFAULT_CONFIG"]["frames_per_second"]),
            )
        except KeyError:
            raise MVRException("camera_name: %s not found in mvr.ini.")

    def _transform(self, extracted_source: MVRContext) -> device.CameraAssembly:
        # mvr_camera_infos, meta = extracted_source
        # camera_assemblies = []
        # for (name, partial_camera_assembly) in meta.partials:
        #     filtered = list(filter(
        #         lambda info: info[0] == name,
        #         mvr_camera_infos,
        #     ))
        #     if len(filtered) < 1:
        #         raise MVRException("MVR camera name: %s not found in mvr.ini" % name)
        #     name, _, serial_number, height, width, frame_rate = filtered[0]
        #     camera_assemblies.append(device.CameraAssembly.parse_obj({
        #         **partial_camera_assembly,
        #         "camera": {
        #             "computer_name": meta.host,
        #             "name": name,
        #             "serial_number": serial_number,
        #             "pixel_height": height,
        #             "pixel_width": width,
        #             "max_frame_rate": frame_rate,
        #             **partial_camera_assembly["camera"]
        #         },
        #     }))
        # return camera_assemblies
        (serial_number, height, width, frame_rate), partial = extracted_source
        d = device.CameraAssembly.parse_obj({
            **partial,
            "camera": {
                    **partial["camera"],
                    "serial_number": serial_number,
                    "pixel_height": height,
                    "pixel_width": width,
                    "max_frame_rate": frame_rate,
            },
        })
        print(dir(rig.CameraAssembly))
        print(dir(d))
        print(type(d))
        return d