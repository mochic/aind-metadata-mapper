import unittest
import pathlib

from aind_metadata_mapper.neuropixels import open_ephys_manipulator

from . import get_current_rig


class TestOpenEphysManipulator(unittest.TestCase):
    """Tests Open Ephys utilities in for the neuropixels project."""

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/open_ephys-manipulator-mapping.json"
        ).read_text()
        extracted = open_ephys_manipulator.extract(content)
        current = get_current_rig()
        open_ephys_manipulator.transform(
            extracted,
            current,
        )
        filtered = filter(
            lambda ephys_assembly: ephys_assembly.ephys_assembly_name == "A",
            current.ephys_assemblies,
        )
        assert next(filtered).manipulator.serial_number == "SN40906"
