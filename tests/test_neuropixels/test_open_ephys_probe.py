import unittest
import pathlib

from aind_data_schema import device

from aind_metadata_mapper.neuropixels import open_ephys_probe

from . import get_current_rig


class TestOpenEphys(unittest.TestCase):
    """Tests Open Ephys utilities in for the neuropixels project."""

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/settings.open_ephys.xml"
        ).read_text()
        extracted = open_ephys_probe.extract(content)
        current = get_current_rig()
        open_ephys_probe.transform(
            extracted,
            current,
        )
        assert current.ephys_assemblies[0].probes[0].serial_number == \
            "19192719051"
