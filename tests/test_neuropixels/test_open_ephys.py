import unittest
import pathlib

from aind_data_schema import device

from aind_metadata_mapper.neuropixels import open_ephys


class TestOpenEphys(unittest.TestCase):
    """Tests Open Ephys utilities in for the neuropixels project."""

    def test_extract_transform_probes(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/settings.open_ephys.xml"
        ).read_text()
        extracted = open_ephys.extract(content)
        transformed = open_ephys.transform(
            extracted[0],
        )
        assert transformed.probe_model == device.ProbeModel.NP1

