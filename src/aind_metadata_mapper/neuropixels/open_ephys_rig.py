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

    settings_list: list[typing.Any] = []


class OpenEphysRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    def __init__(self, 
            input_source: pathlib.Path,
            output_directory: pathlib.Path,
            open_ephys_settings_sources: list[pathlib.Path],
            probe_manipulator_serial_numbers: typing.Optional[dict] = None,
            **kwargs
    ):
        super().__init__(input_source, output_directory, **kwargs)
        self.open_ephys_settings_sources = open_ephys_settings_sources
        self.probe_manipulator_serial_numbers = probe_manipulator_serial_numbers

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            settings_list=[
                ElementTree.fromstring(source.read_text())
                for source in self.open_ephys_settings_sources
            ],
        )

    def _transform_settings(self, current: rig.Rig, settings: typing.Any) -> \
            rig.Rig:
        version_elements = utils.find_elements(settings, "version")
        version = next(version_elements).text
        if version not in SUPPORTED_SETTINGS_VERSIONS:
            logger.warn(
                "Unsupported open ephys settings version: %s. Supported versions: %s"
                % (version, SUPPORTED_SETTINGS_VERSIONS, )
            )

        for element in utils.find_elements(settings, "np_probe"):
            probe_name = element.get("custom_probe_name")
            for ephys_assembly in current.ephys_assemblies:
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
                    logger.debug(
                        "Error updating probe: %s" % probe_name, exc_info=True)
        
        return current

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        for settings in extracted_source.settings_list:
            self._transform_settings(extracted_source.current, settings)

        return super()._transform(extracted_source.current)
