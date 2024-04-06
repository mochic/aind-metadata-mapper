"""Tests for neuropixels dynamic routing task rig ETL."""

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


class TestDynamicRoutingTaskRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl_supported(self):
        """Test ETL with supported dynamic routing task rig file.
        Notes
        -----
        - Sound calibration or reward calibration date not provided is expected
        to make this test fail.
        """
        # get expected calibration dates for tests
        for calibration in self.expected.calibrations:
            if calibration.device_name == "Speaker":
                expected_sound_calibration_date = calibration.calibration_date
                break
        else:  # pragma: no cover
            raise Exception("Sound calibration not found")  # pragma: no cover
        for calibration in self.expected.calibrations:
            if calibration.device_name == "Reward delivery":
                expected_water_calibration_date = calibration.calibration_date
                break
        else:  # pragma: no cover
            raise Exception("Water calibration not found")  # pragma: no cover

        etl = DynamicRoutingTaskRigEtl(
            self.input_source,
            self.output_dir,
            task_source=Path(
                RESOURCES_DIR / "DynamicRouting1_690706_20231130_131725.hdf5"
            ),
            sound_calibration_date=expected_sound_calibration_date,
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
            Path(RESOURCES_DIR / "dynamic-routing-task-rig.json"),
        )

    def tearDown(self):
        """Removes test resources and directory."""
        self._cleanup()


if __name__ == "__main__":
    unittest.main()
