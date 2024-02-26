import unittest
import pathlib
import h5py  # type: ignore

from aind_data_schema.core import rig  # type: ignore
from aind_metadata_mapper.neuropixels import dynamic_routing_task  # type: ignore

from . import utils as test_utils


class TestDynamicRoutingTaskRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        expected = rig.Rig.model_validate_json(
            pathlib.Path(
                "./tests/resources/neuropixels"
                "/dynamic_routing_task_rig.expected.json"
            ).read_text()
        )
        for calibration in expected.calibrations:
            if calibration.device_name == "Speaker":
                expected_sound_calibration_date = calibration.calibration_date
                break
        else:
            raise Exception("Sound calibration not found")
        # for calibration in expected.calibrations:
        #     if calibration.device_name == "water":
        #         expected_water_calibration_date = calibration.calibration_date
        #         break
        # else:
        #     raise Exception("Water calibration not found")
        
        task = h5py.File(
            pathlib.Path(
                "./tests/resources/neuropixels/"
                "/DynamicRouting1_690706_20231130_131725.hdf5"
            ),
            "r",
        )
        etl = dynamic_routing_task.DynamicRoutingTaskRigEtl(
            self.input_source,
            self.output_dir,
            task=task,
            modification_date=expected.modification_date,
            sound_calibration_date=expected_sound_calibration_date,
            # water_calibration_date=expected_water_calibration_date,
        )
        etl.run_job()

        assert self.load_updated() == expected

    def setUp(self):
        """Moves required test resources to testing directory.
        """
        # test directory
        self.input_source, self.output_dir, self.expected, self.load_updated, \
                self._cleanup = \
            test_utils.setup_neuropixels_etl_dirs(
                pathlib.Path(
                    "./tests/resources/neuropixels/rig.partial.json"
                ),
                pathlib.Path(
                    "./tests/resources/neuropixels"
                    "/dynamic_routing_task_rig.expected.json"
                ),
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()
