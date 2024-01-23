import unittest
import pathlib
import json

from aind_data_schema.core import rig
from aind_metadata_mapper.neuropixels import sync_rig

from . import utils


class SyncRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = sync_rig.SyncRigEtl(
            pathlib.Path(
                "./tests/resources/neuropixels/rig.partial.json"
            ),
            self.output_dir,
            sync_config_source=pathlib.Path(
                "./tests/resources/neuropixels/sync.yml"
            ),
        )
        etl.run_job()

        updated_json = json.loads((self.output_dir / "rig.json").read_text())
        expected_json = json.loads(
            pathlib.Path(
                "./tests/resources/neuropixels/sync_rig.expected.json"
            ).read_text()
        )
        expected_json["modification_date"] = updated_json["modification_date"]
        assert rig.Rig.model_validate(updated_json) == \
            rig.Rig.model_validate(expected_json)

    def setUp(self):
        """Moves required test resources to testing directory.
        """
        # test directory
        self.input_dir, self.output_dir, self._cleanup = \
            utils.setup_neuropixels_etl_dirs()

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()
