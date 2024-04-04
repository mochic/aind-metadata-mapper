"""Tests for the neuropixels open ephys rig ETL."""

import pathlib
import unittest

from aind_metadata_mapper.neuropixels import open_ephys_rig  # type: ignore

from . import utils as test_utils


class TestOpenEphysRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        """Test ETL workflow."""
        etl = open_ephys_rig.OpenEphysRigEtl(
            self.input_source,
            self.output_dir,
            open_ephys_settings_sources=[
                pathlib.Path("./tests/resources/neuropixels/settings.xml"),
            ],
            probe_manipulator_serial_numbers=[
                (
                    "Ephys Assembly A",
                    "SN45356",
                ),
                (
                    "Ephys Assembly B",
                    "SN45484",
                ),
                (
                    "Ephys Assembly C",
                    "SN45485",
                ),
                (
                    "Ephys Assembly D",
                    "SN45359",
                ),
                (
                    "Ephys Assembly E",
                    "SN45482",
                ),
                (
                    "Ephys Assembly F",
                    "SN45361",
                ),
            ],
        )
        etl.run_job()
        print(self.output_dir / "rig.json")
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
            pathlib.Path("./tests/resources/neuropixels/open-ephys-rig.json"),
        )

    def tearDown(self):
        """Removes test resources and directory."""
        # self._cleanup()
