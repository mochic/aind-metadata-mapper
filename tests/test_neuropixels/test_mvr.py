import unittest
import pathlib
import json

from aind_metadata_mapper.neuropixels import mvr, NeuropixelsRigException


class TestMvr(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""
    
    overloads = {
        "chroma": "Monochrome",
        "computer_name": "W10DT714046",
        "data_interface": "Ethernet",
        "manufacturer": "ALLIED",
    }

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/good/mvr.ini"
        ).read_text()
        mapping = json.loads(pathlib.Path(
            "./tests/resources/neuropixels/good/mvr.mapping.json"
        ).read_text())
        extracted = mvr.extract(content, mapping)
        transformed = mvr.transform(
            extracted[0],
            **TestMvr.overloads,
        )
        assert transformed.pixel_width == 658


    def test_extract_bad_mapping(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/good/mvr.ini"
        ).read_text()
        mapping = json.loads(pathlib.Path(
            "./tests/resources/neuropixels/bad/mvr.mapping.json"
        ).read_text())
        with self.assertRaises(NeuropixelsRigException):
            mvr.extract(content, mapping)
