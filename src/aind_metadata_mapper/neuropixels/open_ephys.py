import logging
import pydantic
from xml.etree import ElementTree
from aind_data_schema import device

from . import utils, NeuropixelsRigException


logger = logging.getLogger(__name__)


class OpenEphysProbe(pydantic.BaseModel):

    name: str
    model: str
    serial_number: str


SUPPORTED_VERSIONS = ("0.6.6", )


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
            name=element.get("custom_probe_name"),
            model=element.get("probe_name"),
            serial_number=element.get("probe_serial_number"),
        )
        for element in utils.find_elements(loaded, "np_probe")
    ]


def transform(probe: OpenEphysProbe, **overloads) -> device.EphysProbe:
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
    return device.EphysProbe(
        name=probe.name,
        probe_model=probe.model,
        serial_number=probe.serial_number,
        **overloads,
    )
