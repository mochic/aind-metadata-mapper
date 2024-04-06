"""Tests for the MVR rig ETL."""

import os
import unittest
from pathlib import Path

from aind_metadata_mapper.neuropixels.mvr_rig import MvrRigEtl
from tests.test_neuropixels import utils as test_utils

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "neuropixels"
)


class TestMvrRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        """Test basic MVR etl workflow."""
        etl = MvrRigEtl(
            self.input_source,
            self.output_dir,
            RESOURCES_DIR / "mvr.ini",
            mvr_mapping={
                "Camera 1": test_utils.SIDE_CAMERA_ASSEMBLY_NAME,
                "Camera 2": test_utils.EYE_CAMERA_ASSEMBLY_NAME,
                "Camera 3": test_utils.FORWARD_CAMERA_ASSEMBLY_NAME,
            },
        )
        etl.run_job()

        assert self.load_updated() == self.expected

    def test_etl_bad_mapping(self):
        """Test MVR etl workflow with bad mapping."""
        etl = MvrRigEtl(
            self.input_source,
            self.output_dir,
            RESOURCES_DIR / "mvr.ini",
            mvr_mapping={
                "Camera 1": test_utils.SIDE_CAMERA_ASSEMBLY_NAME,
                "Camera 2": test_utils.EYE_CAMERA_ASSEMBLY_NAME,
                "Not a camera name": test_utils.FORWARD_CAMERA_ASSEMBLY_NAME,
            },
        )
        etl.run_job()

    def setUp(self):
        """Moves required test resources to testing directory."""
        # test directory
        (
            self.input_source,
            self.output_dir,
            self.expected,
            self.load_updated,
            self._cleanup,
        ) = test_utils.setup_neuropixels_etl_dirs(
            RESOURCES_DIR / "mvr-rig.json",
        )

    def tearDown(self):
        """Removes test resources and directory."""
        self._cleanup()


if __name__ == "__main__":
    unittest.main()
