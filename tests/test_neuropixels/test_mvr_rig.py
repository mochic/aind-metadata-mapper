import unittest
import pathlib
import json

from aind_data_schema.core import rig
from aind_metadata_mapper.neuropixels import mvr_rig

from . import utils


class TestMvrRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = mvr_rig.MvrRigEtl(
            self.input_dir,
            self.output_dir,
            rig_resource_name="rig.partial.json",
            hostname="localhost",
            mvr_mapping={
                "Camera 1": "Behavior",
                "Camera 2": "Eye",
                "Camera 3": "Face forward",
            },
        )
        etl.run_job()

        updated_json = json.loads((self.output_dir / "rig.json").read_text())
        expected_json = json.loads(
            pathlib.Path(
                "./tests/resources/neuropixels/mvr_rig.expected.json"
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
        mvr_path = pathlib.Path(
            "./tests/resources/neuropixels/mvr.ini"
        )

        # test directory
        self.input_dir, self.output_dir, self._cleanup = \
            utils.setup_neuropixels_etl_dirs(
                rig_partial_path,
                mvr_path,
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()