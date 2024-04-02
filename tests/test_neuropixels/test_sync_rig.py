"""Tests for Sync rig ETL."""
import unittest
import pathlib

from aind_metadata_mapper.neuropixels import sync_rig  # type: ignore

from . import utils


class SyncRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        """Test ETL workflow."""
        etl = sync_rig.SyncRigEtl(
            self.input_source,
            self.output_dir,
            pathlib.Path("./tests/resources/neuropixels/sync.yml"),
        )
        etl.run_job()

        assert self.load_updated() == self.expected

    def setUp(self):
        """Moves required test resources to testing directory.
        """
        # test directory
        self.input_source, self.output_dir, self.expected, self.load_updated, \
            self._cleanup = \
            utils.setup_neuropixels_etl_dirs(
                pathlib.Path(
                    "./tests/resources/neuropixels/sync-rig.json"
                ),
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()
