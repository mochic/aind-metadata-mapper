import logging
import json
from xml.etree import ElementTree
from aind_data_schema import device, rig

from . import utils, NeuropixelsRigException


logger = logging.getLogger(__name__)


class OpenEphysProbe(
    device.EphysProbe,
    metaclass=utils.AllOptionalMeta,
    required_fields=[
        "name",
        "model",
        "serial_number",
        "notes",
    ]
):
    """
    """


SUPPORTED_VERSIONS = ("0.6.6", )


def _get_probe_element_property(element: ElementTree.Element, prop_name: str):
    """Adds debug logging to probe element propery getting.
    """
    value = element.get(prop_name)
    if value is None:
        logger.debug(
            "Failed to find property for probe element. prop_name=%s"
            % prop_name
        )
    return value

def extract(content: str) -> list[OpenEphysProbe]:
    """Extracts probe meta data from the contents of a settings file produced at
     the end of each experiment.

    Parameters
    ----------
    content: str
        Content of the settings file

    Returns
    -------
    probes
        Extracted open ephys probes
    """
    loaded = ElementTree.fromstring(content)
    version_elements = utils.find_elements(loaded, "version")
    version = next(version_elements).text
    if version not in SUPPORTED_VERSIONS:
        raise NeuropixelsRigException(
            "Unsupported open ephys settings version: %s. Supported versions: %s"
            % (version, SUPPORTED_VERSIONS, )
        )

    return [
        OpenEphysProbe(
            name=_get_probe_element_property(
                element,
                "custom_probe_name",
            ),
            model=_get_probe_element_property(
                element,
                "probe_name",
            ),
            serial_number=_get_probe_element_property(
                element,
                "probe_serial_number",
            ),
        )
        for element in utils.find_elements(loaded, "np_probe")
    ]


def find_matching_probe(
        ephys_assemblies: device.EphysAssembly,
        probe_name: str
) -> device.EphysProbe:
    matches = []
    for assembly in ephys_assemblies:
        for probe in assembly.probes:
            if probe.name == probe_name:
                matches.append(probe)
    
    if len(matches) > 1:
        raise Exception("More than one matching probe found.")
    
    return matches[0]


def transform(
        open_ephys_probes: list[OpenEphysProbe],
        current: rig.Rig,
        maximum_match_log_count: int = 20
        ) -> None:
    """Transforms OpenEphysProbe into aind-data-schema probe.

    Parameters
    ----------
    probe: OpenEphysProbe
        open ephys probe
    overloads:
        argument overloads for EphysProbe

    Returns
    -------
    probe: EphysProbe
        transformed ephys probe
    """
    for open_ephys_probe in open_ephys_probes:
        probe = find_matching_probe(
            current.ephys_assemblies,
            open_ephys_probe.name,
        )
        utils.merge_devices(
            probe,
            open_ephys_probe,
        )

    return current
