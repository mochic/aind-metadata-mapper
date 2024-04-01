import unittest
import pathlib

from aind_metadata_mapper.neuropixels import dynamic_routing_task  # type: ignore

from . import utils as test_utils


class TestDynamicRoutingTaskRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl_supported(self):
        # get expected calibration dates for tests
        for calibration in self.expected.calibrations:
            if calibration.device_name == "Speaker":
                expected_sound_calibration_date = calibration.calibration_date
                break
        else:
            raise Exception("Sound calibration not found")
        for calibration in self.expected.calibrations:
            if calibration.device_name == "Reward delivery":
                expected_water_calibration_date = calibration.calibration_date
                break
        else:
            raise Exception("Water calibration not found")

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
        """Moves required test resources to testing directory.
        """
        # test directory
        self.input_source, self.output_dir, self.expected, self.load_updated, \
                self._cleanup = \
            test_utils.setup_neuropixels_etl_dirs(
                pathlib.Path(
                    "./tests/resources/neuropixels/"
                    "dynamic-routing-task-rig.json"
                ),
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()
