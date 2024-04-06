"""Tests for neuropixels dynamic routing task rig ETL. Uses an unsupported
 version of the dynamic routing task output file."""

import os
import unittest
from pathlib import Path

from aind_metadata_mapper.neuropixels.dynamic_routing_task import (
    DynamicRoutingTaskRigEtl,
)
from tests.test_neuropixels import utils as test_utils

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "neuropixels"
)


class TestDynamicRoutingTaskRigEtlUnsupported(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl_unsupported(self):
        """Test ETL with unsupported dynamic routing task rig file."""
        # get expected calibration dates for tests
        for calibration in self.expected.calibrations:
            if calibration.device_name == "Reward delivery":
                expected_water_calibration_date = calibration.calibration_date
                break
            else:  # pragma: no cover
                raise Exception(
                    "Water calibration not found"
                )  # pragma: no cover

        etl = DynamicRoutingTaskRigEtl(
            self.input_source,
            self.output_dir,  # TODO: separate output directory for unsupported
            task_source=RESOURCES_DIR
            / "DynamicRouting1_649943_20230213_114903.hdf5",
            reward_calibration_date=expected_water_calibration_date,
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
            RESOURCES_DIR / "dynamic-routing-task-rig-unsupported.json"
        )

    def tearDown(self):
        """Removes test resources and directory."""
        self._cleanup()


if __name__ == "__main__":
    unittest.main()
