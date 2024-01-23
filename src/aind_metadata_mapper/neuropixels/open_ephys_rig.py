import typing
import logging
import pathlib
from xml.etree import ElementTree
from aind_data_schema.core import rig
from . import neuropixels_rig, utils, NeuropixelsRigException


logger = logging.getLogger(__name__)

# the format of open_ephys settings.xml will vary based on version
SUPPORTED_SETTINGS_VERSIONS = (
    "0.6.6",
)


class OpenEphysRigContext(neuropixels_rig.RigContext):

    model_config = {
        "arbitrary_types_allowed": True,
    }

    settings: ElementTree


class OpenEphysRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    def __init__(self, 
            *args,
            open_ephys_settings_source: pathlib.Path,
            probe_manipulator_serial_numbers: typing.Optional[dict] = None,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.open_ephys_settings_source = open_ephys_settings_source
        self.probe_manipulator_serial_numbers = probe_manipulator_serial_numbers

    def _extract(self) -> OpenEphysRigContext:
        return OpenEphysRigContext(
            current=super()._extract().current,
            settings=ElementTree.fromstring(
                self.open_ephys_settings_source.read_text(),
            )
        )

    def _transform(
            self,
            extracted_source: OpenEphysRigContext) -> rig.Rig:
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

        # return super()._transform(extracted_source.current)
        return super()._transform(extracted_source)
