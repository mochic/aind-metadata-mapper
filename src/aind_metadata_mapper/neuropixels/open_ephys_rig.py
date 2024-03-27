import typing
import logging
import pathlib
import pydantic
from xml.etree import ElementTree
from aind_data_schema.core import rig  # type: ignore
from aind_data_schema.models import devices  # type: ignore

from . import neuropixels_rig, utils, NeuropixelsRigException


logger = logging.getLogger(__name__)


class ExtractedProbe(pydantic.BaseModel):

    name: typing.Optional[str]
    model: typing.Optional[str]
    serial_number: typing.Optional[str]


class ExtractContext(neuropixels_rig.NeuropixelsRigContext):

    probes: list[ExtractedProbe]
    versions: list[typing.Union[str, None]]


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
        current = super()._extract()
        versions = []
        probes = []
        for source in self.open_ephys_settings_sources:
            parsed = ElementTree.fromstring(source.read_text())
            versions.append(self._extract_version(parsed))
            probes.extend(self._extract_probes(
                current,
                parsed,
            ))
        return ExtractContext(
            current=current,
            probes=probes,
            versions=versions,
        )

    def _extract_version(self, settings: ElementTree.Element) -> \
            typing.Union[str, None]:
        version_elements = utils.find_elements(settings, "version")
        return next(version_elements).text

    def _extract_probes(self, current: rig.Rig,
            settings: ElementTree.Element) -> list[ExtractedProbe]:
        extracted_probes = [
            ExtractedProbe(
                name=element.get("custom_probe_name"),
                model=element.get("probe_name"),
                serial_number=element.get("probe_serial_number"),
            )
            for element in utils.find_elements(settings, "np_probe")
        ]
        
        probes = []
        for element in utils.find_elements(settings, "np_probe"):
            probe_name = element.get("custom_probe_name")
            for ephys_assembly in current.ephys_assemblies:
                extracted_probe = None
                for probe in ephys_assembly.probes:
                    if probe.name == probe_name:
                        extracted_probe = \
                            ExtractedProbe(
                                name=probe.name,
                                model=element.get("probe_name"),
                                serial_number=element.get("probe_serial_number"),
                            )
                if extracted_probe is not None:
                    probes.append(extracted_probe)
                    break
            else:
                logger.warning(
                    "Error finding probe from open ephys settings: %s"
                    % probe_name)
                return self._infer_extracted_probes(current, settings)

        return probes

    def _get_rig_probe_names(self, current: rig.Rig) -> \
            list[str]:
        return [
            probe.name
            for assembly in current.ephys_assemblies
            for probe in assembly.probes
        ]

    def _infer_extracted_probes(self, current: rig.Rig,
            settings: ElementTree.Element) -> list[ExtractedProbe]:
        logger.debug(
            "Inferring associated probes from np_probe element order in open "
            "ephys settings.")
        probe_elements = list(utils.find_elements(settings, "np_probe"))
        n_probe_elements = len(probe_elements)
        n_rig_probes = sum(
            len(assembly.probes) for assembly in current.ephys_assemblies
        )
        if len(current.ephys_assemblies) != n_probe_elements:
            logger.warning(
                "Number of ephys assemblies doesnt match probes in settings. "
                "Skipping probe inference.")
            return []
        
        if n_probe_elements != n_rig_probes:
            logger.warning(
                "Number of probes in settings does not match number of probes "
                "in rig. Skipping probe inference. settings probes count: %s,"
                " rig probes count: %s" % (n_probe_elements, n_rig_probes)
            )
            return []

        probes = []
        for ephys_assembly, probe_element in \
                zip(current.ephys_assemblies, probe_elements):
            probes.append(ExtractedProbe(
                name=ephys_assembly.probes[0].name,
                model=probe_element.get("probe_name"),
                serial_number=probe_element.get("probe_serial_number"),
            ))
        return probes

    def _transform_ephys_assembly(
        self,
        ephys_assembly_name: str,
        ephys_assembly_updates: dict[str, typing.Any],
        probe_updates: list[dict[str, typing.Any]], 
    ):
        pass

    def _transform(
        self,
        extracted_source: ExtractContext,
    ) -> rig.Rig:
        # update manipulator serial numbers
        for ephys_assembly in extracted_source.current.ephys_assemblies:
            if self.probe_manipulator_serial_numbers and \
                    ephys_assembly.ephys_assembly_name in \
                    self.probe_manipulator_serial_numbers:
                ephys_assembly.manipulator.serial_number = \
                    self.probe_manipulator_serial_numbers[ephys_assembly.ephys_assembly_name]

        # update probe models and serial numbers
        for probe in extracted_source.probes:
            for ephys_assembly in extracted_source.current.ephys_assemblies:  
                try:
                    utils.find_update(
                        ephys_assembly.probes,
                        filters=[
                            ("name", probe.name),
                        ],
                        model=probe.model,
                        serial_number=probe.serial_number,
                    )
                    break
                except NeuropixelsRigException:
                    pass
            else:
                logger.warning("No probe found in rig for: %s" % probe.name)

        version = None  # default version if None was scraped
        # uses version of first settings file, TODO: handle multiple versions?
        # for v in extracted_source.versions:
        #     if v is not None:
        #         version = v
        #         break

        # self.update_software(
        #     extracted_source.current,
        #     "Open Ephys",
        #     url=version,
        # )

        # self.update_software(
        #     extracted_source.current,
        #     "Open Ephys",
        #     url=version,
        # )

        return super()._transform(extracted_source.current)
