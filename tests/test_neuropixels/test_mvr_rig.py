import unittest
import pathlib

from aind_metadata_mapper.neuropixels import mvr_rig  # type: ignore

from . import utils as test_utils


class TestMvrRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = mvr_rig.MvrRigEtl(
            self.input_source,
            self.output_dir,
            pathlib.Path(
                "./tests/resources/neuropixels/mvr.ini",
            ),
            mvr_mapping={
                "Camera 1": "Behavior",
                "Camera 2": "Eye",
                "Camera 3": "Face forward",
            },
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
            test_utils.setup_neuropixels_etl_dirs(
                pathlib.Path(
                    "./tests/resources/neuropixels/rig.partial.json",
                ),
                pathlib.Path(
                    "./tests/resources/neuropixels/mvr_rig.expected.json"
                ),
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()