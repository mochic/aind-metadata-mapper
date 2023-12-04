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
    
    # open_ephys_probes = []
    # for element in utils.find_elements(loaded, "np_probe"):
    #     open_ephys_probes.append(OpenEphysProbe(
    #         name=_get_probe_element_property(
    #             element,
    #             "custom_probe_name",
    #         ),
    #         model=_get_probe_element_property(
    #             element,
    #             "probe_name",
    #         ),
    #         serial_number=_get_probe_element_property(
    #             element,
    #             "probe_serial_number",
    #         ),
    #     ))
    
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


# def transform(
#         open_ephys_probes: list[OpenEphysProbe],
#         current: rig.Rig,
#         maximum_match_log_count: int = 20
#         ) -> None:
#     """Transforms OpenEphysProbe into aind-data-schema probe.

#     Parameters
#     ----------
#     probe: OpenEphysProbe
#         open ephys probe
#     overloads:
#         argument overloads for EphysProbe

#     Returns
#     -------
#     probe: EphysProbe
#         transformed ephys probe
#     """
#     for open_ephys_probe in open_ephys_probes:
#         # matching_assemblies = filter(
#         #     lambda ephys_assembly: 0,
#         #     current.ephys_assemblies,
#         # )
#         print("open ephys probe name")
#         print(open_ephys_probe.name)
        
#         def filter_probe(probe):
#             print("filtering")
#             print(probe)
#             print(open_ephys_probe.name)
#             print(type(open_ephys_probe.name))
#             print(type(probe.name))
#             print(probe.name == open_ephys_probe.name)
#             return probe.name == open_ephys_probe.name
        
#         print("assemblies")
#         print(current.ephys_assemblies)
#         def filter_assembly(probe):
#             print("filtering assemblies")
#             # print(probe)
#             # print(open_ephys_probe.name)
#             result = len(list(filter(filter_probe, list(probe.probes)))) > 1
#             print(result)
#             return result
#         #     lambda ephys_assembly: filter(
#         #         # lambda probe: probe.name == open_ephys_probe.name,
#         #         filter_probe,
#         #         ephys_assembly.probes,
#         #     ),
#         #     current.ephys_assemblies,
#         # )
#         matching_assemblies = list(filter(filter_assembly, current.ephys_assemblies))
#         print("matching assemblies")
#         print(matching_assemblies)
#         if len(matching_assemblies) > 1:
#             raise Exception()
        
#         # print(len(list(matches)))
#         print("matching")
#         print(len(list(matching_assemblies)))
#         try:
#             # matching_assembly = next(matches)
#             # print("assembly")
#             # print(matching_assembly)
#             matching_probes = filter(
#                 lambda probe: probe.name == open_ephys_probe.name,
#                 matching_assembly.probes,
#             )
#             print("probe")
#             matching = next(matching_probes)
#             print(matching)
#             utils.merge_devices(
#                 matching,
#                 open_ephys_probe,
#             )
#         except StopIteration:
#             raise NeuropixelsRigException(
#                 (
#                     "No matching rig probe for Open Ephys Probe. Appending a"
#                     " fresh one. name=%s"
#                 ) % open_ephys_probe.name
#             )

#         # try:
#         #     count = 0 
#         #     while count < maximum_match_log_count:
#         #         serialized = json.dumps(next(matches).dict())
#         #         logger.debug(
#         #             "More than one matching ephys_assembly for Open Ephys Probe"
#         #             % serialized
#         #         )
#         #     else:
#         #         logger.debug(
#         #             (
#         #                 "Reached maximum_match_log_count. Stopping match logs."
#         #                 " maximum_match_log_count=%s"
#         #             ) % maximum_match_log_count
#         #         )
#         # except StopIteration:
#         #     pass

#     return current

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
