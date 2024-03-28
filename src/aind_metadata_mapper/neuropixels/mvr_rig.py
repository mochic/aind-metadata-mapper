import logging
import pathlib
from aind_data_schema.core import rig  # type: ignore
from aind_data_schema.models import devices  # type: ignore
from . import neuropixels_rig, utils


logger = logging.getLogger(__name__)


class ExtractContext(neuropixels_rig.NeuropixelsRigContext):

    serial_numbers: list[tuple[str, str]]


class MvrRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    def __init__(self, 
            input_source: pathlib.Path,
            output_directory: pathlib.Path,
            mvr_config_source: pathlib.Path,
            mvr_mapping: dict[str, str],
            **kwargs
    ):
        super().__init__(input_source, output_directory, **kwargs)
        self.mvr_mapping = mvr_mapping
        self.mvr_config_source = mvr_config_source

    def _extract(self) -> ExtractContext:
        mvr_config = utils.load_config(self.mvr_config_source)
        serial_numbers = []
        for mvr_name, assembly_name in self.mvr_mapping.items():
            try:
                mvr_camera_config = mvr_config[mvr_name]
            except KeyError:
                logger.debug(
                    "No camera found for: %s in mvr config." %
                    mvr_name
                )
            serial_numbers.append(
                (
                    assembly_name,
                    "".join(mvr_camera_config["sn"]),
                )
            )
        return ExtractContext(
            current=super()._extract(),
            serial_numbers=serial_numbers,
        )

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        for assembly_name, serial_number in extracted_source.serial_numbers:
            utils.find_update(
                extracted_source.current.cameras,
                filters=[
                    ("camera_assembly_name", assembly_name, ),
                ],
                setter=\
                    lambda item, name, value: setattr(item.camera, name, value),
                serial_number=serial_number,
                recording_software=devices.Software(
                    name="MVR",
                    version="Not detected/provided.",
                )
            )

        return super()._transform(extracted_source.current)
