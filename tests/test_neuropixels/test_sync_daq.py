import unittest
import pathlib

from aind_metadata_mapper.neuropixels import sync_daq
from aind_data_schema import device, rig


class TestSync(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    # def test_extract_transform(self):
    #     content = pathlib.Path(
    #         "./tests/resources/neuropixels/good/sync.yml"
    #     ).read_text()
    #     extracted = sync.extract(content)
    #     transformed = sync.transform(
    #         extracted,
    #     )
    #     assert transformed[0].device_name == "Dev1"

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/good/sync.yml"
        ).read_text()
        extracted = sync_daq.extract(content)
        current_rig = rig.Rig.parse_raw(
            pathlib.Path(
                "./tests/resources/neuropixels/current-rig.json"
            ).read_text()
        )
        sync_name = "Sync"
        sync_daq.transform(
            extracted,
            current_rig,
            sync_name,
        )
        for daq in current_rig.daqs:
            if daq.name == sync_name:
                assert len(daq.channels) > 0
