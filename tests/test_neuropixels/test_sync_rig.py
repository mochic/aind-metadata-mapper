"""Tests for Sync rig ETL."""

import os
import unittest
from pathlib import Path

from aind_metadata_mapper.neuropixels.sync_rig import SyncRigEtl
from tests.test_neuropixels import utils as test_utils

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "neuropixels"
)


class TestSyncRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        """Test ETL workflow."""
        etl = SyncRigEtl(
            self.input_source,
            self.output_dir,
            RESOURCES_DIR / "sync.yml",
        )
        etl.run_job()

        assert self.load_updated() == self.expected

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
            RESOURCES_DIR / "sync-rig.json"
        )

    def tearDown(self):
        """Removes test resources and directory."""
        self._cleanup()


if __name__ == "__main__":
    unittest.main()
