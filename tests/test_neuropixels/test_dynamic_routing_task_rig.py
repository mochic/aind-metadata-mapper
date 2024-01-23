import unittest
import pathlib
import json

from aind_data_schema.core import rig
from aind_metadata_mapper.neuropixels import dynamic_routing_task

from . import utils


class TestDynamicRoutingTaskRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = dynamic_routing_task.DynamicRoutingTaskRigEtl(
            pathlib.Path(
                "./tests/resources/neuropixels/rig.partial.json"
            ),
            self.output_dir,
            task_source=pathlib.Path(
                "./tests/resources/neuropixels/",
                "DynamicRouting1_690706_20231130_131725.hdf5"
            ),
        )
        etl.run_job()

        updated_json = json.loads((self.output_dir / "rig.json").read_text())
        expected_json = json.loads(
            pathlib.Path(
                "./tests/resources/neuropixels/",
                "dynamic_routing_task_rig.expected.json"
            ).read_text()
        )
        expected_json["modification_date"] = updated_json["modification_date"]
        expected_json["calibrations"][0]["calibration_date"] = \
            updated_json["calibrations"][0]["calibration_date"]
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
