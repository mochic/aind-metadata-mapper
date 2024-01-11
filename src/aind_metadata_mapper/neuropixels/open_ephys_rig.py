import pydantic
import typing
from xml.etree import ElementTree
from aind_data_schema.core import rig
from . import directory_context_rig, utils, NeuropixelsRigException


# the format of open_ephys settings.xml will vary based on version
SUPPORTED_SETTINGS_VERSIONS = (
    "0.6.6",
)


class ExtractContext(pydantic.BaseModel):

    current: typing.Any
    settings: typing.Any


class OpenEphysRigEtl(directory_context_rig.DirectoryContextRigEtl):

    def __init__(self, 
            *args,
            open_ephys_settings_resource_name: str = "settings.xml",
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.open_ephys_settings_resource_name = \
            open_ephys_settings_resource_name

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            settings=ElementTree.fromstring(
                (self.input_source / self.open_ephys_settings_resource_name)
                    .read_text()
            )
        )

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        version_elements = utils.find_elements(
            extracted_source.settings, "version")
        version = next(version_elements).text
        if version not in SUPPORTED_SETTINGS_VERSIONS:
            raise NeuropixelsRigException(
                "Unsupported open ephys settings version: %s. Supported versions: %s"
                % (version, SUPPORTED_SETTINGS_VERSIONS, )
            )

        for element in utils.find_elements(extracted_source.settings, "np_probe"):
            probe_name = element.get("custom_probe_name")
            for ephys_assembly in extracted_source.current.ephys_assemblies:
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
