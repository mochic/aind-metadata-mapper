import pydantic
import typing
import pathlib
from configparser import ConfigParser
from aind_data_schema.core import rig
from . import neuropixels_rig, utils, NeuropixelsRigException


class MvrRigContext(neuropixels_rig.RigContext):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    mvr_config: ConfigParser


class MvrRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    def __init__(self, 
            *args,
            hostname: str,
            mvr_mapping: dict[str, str],
            mvr_config_source: pathlib.Path,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.hostname = hostname
        self.mvr_mapping = mvr_mapping
        self.mvr_config_source = mvr_config_source

    def _extract(self) -> MvrRigContext:
        return MvrRigContext(
            current=super()._extract().current,
            mvr_config=utils.load_config(
                self.mvr_config_source,
            )
        )

    def _transform(
            self,
            extracted_source: MvrRigContext) -> rig.Rig:

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

        # return super()._transform(extracted_source.current)
        return super()._transform(extracted_source)
