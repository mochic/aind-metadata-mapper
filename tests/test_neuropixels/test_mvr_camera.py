import unittest
import pathlib
import json

from aind_metadata_mapper.neuropixels import NeuropixelsRigException, \
    mvr_camera

from . import get_current_rig


class TestMvr(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/good/mvr.ini"
        ).read_text()
        mapping = json.loads(pathlib.Path(
            "./tests/resources/neuropixels/good/mvr.mapping.json"
        ).read_text())
        extracted = mvr_camera.extract(content, mapping)
        current = get_current_rig()
        mvr_camera.transform(
            extracted,
            current,
        )
        for camera_assembly in current.cameras:
            if camera_assembly.camera_assembly_name == "Behavior":
                assert camera_assembly.camera.pixel_width == 658

    # def test_extract_bad_mapping(self):
    #     content = pathlib.Path(
    #         "./tests/resources/neuropixels/good/mvr.ini"
    #     ).read_text()
    #     mapping = json.loads(pathlib.Path(
    #         "./tests/resources/neuropixels/bad/mvr.mapping.json"
    #     ).read_text())
    #     with self.assertRaises(NeuropixelsRigException):
    #         mvr_camera.extract(content, mapping)
