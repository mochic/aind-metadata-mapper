"""Tests for neuropixels dynamic routing task rig ETL."""

import pathlib
import unittest

from aind_metadata_mapper.neuropixels import (  # type: ignore
    dynamic_routing_task,
)

from . import utils as test_utils


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

        etl = dynamic_routing_task.DynamicRoutingTaskRigEtl(
            self.input_source,
            self.output_dir,
            task_source=pathlib.Path(
                "./tests/resources/neuropixels/"
                "DynamicRouting1_690706_20231130_131725.hdf5"
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
            pathlib.Path(
                "./tests/resources/neuropixels/"
                "dynamic-routing-task-rig.json"
            ),
        )

    def tearDown(self):
        """Removes test resources and directory."""
        self._cleanup()
