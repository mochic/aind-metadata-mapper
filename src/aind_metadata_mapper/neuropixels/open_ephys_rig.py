import typing
import logging
import pathlib
from xml.etree import ElementTree
from aind_data_schema.core import rig  # type: ignore
from . import neuropixels_rig, utils, NeuropixelsRigException


logger = logging.getLogger(__name__)

# the format of open_ephys settings.xml will vary based on version
SUPPORTED_SETTINGS_VERSIONS = (
    "0.6.6",
)


class ExtractContext(neuropixels_rig.NeuropixelsRigContext):

    settings: typing.Any


class OpenEphysRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    def __init__(self, 
            input_source: pathlib.Path,
            output_directory: pathlib.Path,
            open_ephys_settings: typing.Any,
            probe_manipulator_serial_numbers: typing.Optional[dict] = None,
            **kwargs
    ):
        super().__init__(input_source, output_directory, **kwargs)
        self.open_ephys_settings = open_ephys_settings
        self.probe_manipulator_serial_numbers = probe_manipulator_serial_numbers

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            settings=self.open_ephys_settings,
        )

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        version_elements = utils.find_elements(
            extracted_source.settings, "version")
        version = next(version_elements).text
        if version not in SUPPORTED_SETTINGS_VERSIONS:
            logger.warn(
                "Unsupported open ephys settings version: %s. Supported versions: %s"
                % (version, SUPPORTED_SETTINGS_VERSIONS, )
            )

        for element in utils.find_elements(extracted_source.settings, "np_probe"):
            probe_name = element.get("custom_probe_name")
            for ephys_assembly in extracted_source.current.ephys_assemblies:
                if self.probe_manipulator_serial_numbers and \
                        ephys_assembly.ephys_assembly_name in \
                        self.probe_manipulator_serial_numbers:
                    ephys_assembly.manipulator.serial_number = \
                        self.probe_manipulator_serial_numbers[ephys_assembly.ephys_assembly_name]
  
                try:
                    utils.find_update(
                        ephys_assembly.probes,
                        filters=[
                            ("name", probe_name),
                        ],
                        model=element.get("probe_name"),
                        serial_number=element.get("probe_serial_number"),
                    )
                    break
                except NeuropixelsRigException:
                    pass

        return super()._transform(extracted_source.current)
