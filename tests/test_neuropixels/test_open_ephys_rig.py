import unittest
import pathlib
import json

from aind_data_schema.core import rig
from aind_metadata_mapper.neuropixels import open_ephys_rig

from . import utils


class TestMvrRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = open_ephys_rig.OpenEphysRigEtl(
            self.input_dir,
            self.output_dir,
            rig_resource_name="rig.partial.json",
            open_ephys_settings_resource_name="settings.xml",
        )
        etl.run_job()

        updated_json = json.loads((self.output_dir / "rig.json").read_text())
        expected_json = json.loads(
            pathlib.Path(
                "./tests/resources/neuropixels/open_ephys_rig.expected.json"
            ).read_text()
        )
        expected_json["modification_date"] = updated_json["modification_date"]
        assert rig.Rig.model_validate(updated_json) == \
            rig.Rig.model_validate(expected_json)

    def setUp(self):
        """Moves required test resources to testing directory.
        """
        rig_partial_path = pathlib.Path(
            "./tests/resources/neuropixels/rig.partial.json"
        )
        settings_path = pathlib.Path(
            "./tests/resources/neuropixels/settings.xml"
        )

        # test directory
        self.input_dir, self.output_dir, self._cleanup = \
            utils.setup_neuropixels_etl_dirs(
                rig_partial_path,
                settings_path,
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()