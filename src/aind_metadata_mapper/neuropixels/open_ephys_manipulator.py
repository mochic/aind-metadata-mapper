import json
from aind_data_schema import device, rig

from . import utils


class OpenEphysManipulator(
    device.Manipulator,
    metaclass=utils.AllOptionalMeta,
    required_fields=[
        "name",
        "serial_number",
    ]
):
    """
    """



def extract(content: str) -> list[OpenEphysManipulator]:
    """Extracts probe meta data from the contents of a settings file produced at
     the end of each experiment.

    Parameters
    ----------
    content: str
        Serialized json mapping probe serial_number to manipulator serial number

    Returns
    -------
    manipulators
        Extracted open ephys probes
    """
    mapping = json.loads(content)
    return [
        OpenEphysManipulator(name=name, serial_number=serial_number)
        for name, serial_number in mapping.items()
    ]


def transform(manipulators: list[OpenEphysManipulator], current: rig.Rig) \
    -> None:
    for ephys_assembly in current.ephys_assemblies:
        for manipulator in manipulators:
            if manipulator.name == ephys_assembly.ephys_assembly_name:
                utils.merge_devices(
                    ephys_assembly.manipulator,
                    manipulator,
                )