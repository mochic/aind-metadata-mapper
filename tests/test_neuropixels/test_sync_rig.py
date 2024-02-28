import unittest
import pathlib
import yaml  # type: ignore

from aind_metadata_mapper.neuropixels import sync_rig  # type: ignore

from . import utils


class SyncRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = sync_rig.SyncRigEtl(
            self.input_source,
            self.output_dir,
            yaml.safe_load(
                pathlib.Path(
                    "./tests/resources/neuropixels/sync.yml",
                ).read_text()
            ),
            modification_date=self.expected.modification_date,
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
                    "./tests/resources/neuropixels/rig.partial.json"
                ),
                pathlib.Path(
                    "./tests/resources/neuropixels/sync_rig.expected.json"
                ),
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()
