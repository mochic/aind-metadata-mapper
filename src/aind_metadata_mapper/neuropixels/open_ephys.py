import logging
import json
from xml.etree import ElementTree
# from aind_data_schema import device, rig

from . import utils, NeuropixelsRigException


logger = logging.getLogger(__name__)


SUPPORTED_VERSIONS = ("0.6.6", )


def transform_probes(config: ElementTree, current: dict) -> dict:
    version_elements = utils.find_elements(config, "version")
    version = next(version_elements).text
    if version not in SUPPORTED_VERSIONS:
        logger.debug(
            "Unsupported open ephys settings version: %s. Supported versions: %s"
            % (version, SUPPORTED_VERSIONS, )
        )

    for element in utils.find_elements(config, "np_probe"):
        probe_name = element.get("custom_probe_name")
        for ephys_assembly in current["ephys_assemblies"]:
            utils.find_update(
                ephys_assembly["probes"],
                filters=[
                    ("name", probe_name),
                ],
                model=element.get("probe_name"),
                serial_number=element.get("probe_serial_number"),
            )


def transform_manipulators(config: dict, current: dict):
    for ephys_assembly in current["ephys_assemblies"]:
        try:
            serial_number = config[ephys_assembly["ephys_assembly_name"]]
        except KeyError:
            raise NeuropixelsRigException(
                "No manipulator found for: %s in open-ephys-probe.json" %
                ephys_assembly["ephys_assembly_name"]
            )
        ephys_assembly["manipulator"] = {
            **ephys_assembly["manipulator"],
            "serial_number": serial_number,
        }