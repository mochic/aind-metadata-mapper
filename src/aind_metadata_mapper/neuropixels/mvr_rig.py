import typing
import pathlib
from aind_data_schema.core import rig  # type: ignore
from . import neuropixels_rig, utils, NeuropixelsRigException


class ExtractContext(neuropixels_rig.NeuropixelsRigContext):

    mvr_config: typing.Any


class MvrRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    def __init__(self, 
            input_source: pathlib.Path,
            output_directory: pathlib.Path,
            mvr_config: typing.Any,
            mvr_mapping: dict[str, str],
            hostname: str = "localhost",
            **kwargs
    ):
        super().__init__(input_source, output_directory, **kwargs)
        self.hostname = hostname
        self.mvr_mapping = mvr_mapping
        self.mvr_config = mvr_config

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            mvr_config=self.mvr_config,
        )

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        height = int(
            extracted_source.mvr_config["CAMERA_DEFAULT_CONFIG"]["height"]
        )
        width = int(
            extracted_source.mvr_config["CAMERA_DEFAULT_CONFIG"]["width"]
        )

        for mvr_name, assembly_name in self.mvr_mapping.items():
            try:
                mvr_camera_config = extracted_source.mvr_config[mvr_name]
            except KeyError:
                raise NeuropixelsRigException(
                    "No camera found for: %s in mvr config." %
                    mvr_name
                )
            serial_number = "".join(mvr_camera_config["sn"])
            utils.find_update(
                extracted_source.current.cameras,
                filters=[
                    ("camera_assembly_name", assembly_name, ),
                ],
                setter=lambda item, name, value: setattr(item.camera, name, value),
                computer_name=self.hostname,
                serial_number=serial_number,
                pixel_height=height,
                pixel_width=width,
                size_unit="pixel",
            )

        return super()._transform(extracted_source.current)
