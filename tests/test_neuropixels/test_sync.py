import unittest
import pathlib

from aind_metadata_mapper.neuropixels import sync
from aind_data_schema import device


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

    def test_extract_merge(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/good/sync.yml"
        ).read_text()
        extracted = sync.extract(content)
        # target = device.DAQDevice(
        #     computer_name="w10dtsm18307",
        #     data_interface="USB",
        #     device_type="DAQ Device",
        #     manufacturer="NATIONAL_INSTRUMENTS",
        #     name="Sync",
        # )