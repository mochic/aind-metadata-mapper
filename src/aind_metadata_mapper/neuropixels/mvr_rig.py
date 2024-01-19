import pydantic
import typing
from configparser import ConfigParser
from aind_data_schema.core import rig
from . import directory_context_rig, utils, NeuropixelsRigException


class ExtractContext(pydantic.BaseModel):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    current: rig.Rig
    mvr_config: ConfigParser


class MvrRigEtl(directory_context_rig.DirectoryContextRigEtl):

    def __init__(self, 
            *args,
            hostname: str,
            mvr_mapping: dict[str, str],
            mvr_resource_name: str = "mvr.ini",
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.hostname = hostname
        self.mvr_mapping = mvr_mapping
        self.mvr_resource_name = mvr_resource_name

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            mvr_config=utils.load_config(
                self.input_source / self.mvr_resource_name
            )
        )

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:

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
            )

        return super()._transform(extracted_source.current)
