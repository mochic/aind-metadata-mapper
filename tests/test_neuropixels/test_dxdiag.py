import unittest
import pathlib

from aind_metadata_mapper.neuropixels import dxdiag


class TestDxdiag(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""
    
    overloads = {
        "viewing_distance": 10.0,
        "viewing_distance_unit": "centimeter",
        "manufacturer": "ASUS",
        "contrast": 0,
        "brightness": 0,
        "refresh_rate": 60,
        "serial_number": "faux-serial-number",
    }

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/dxdiag.xml"
        ).read_text()
        extracted = dxdiag.extract(content)
        transformed = dxdiag.transform(
            extracted,
            **TestDxdiag.overloads,
        )
        assert transformed.width == 1920

    def test_extract_transform_missing(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/dxdiag-missing.xml"
        ).read_text()
        extracted = dxdiag.extract(content)
        transformed = dxdiag.transform(
            extracted,
            width=1920,
            height=1200,
            size_unit="pixel",
            **TestDxdiag.overloads,
        )
        assert transformed.width == 1920
