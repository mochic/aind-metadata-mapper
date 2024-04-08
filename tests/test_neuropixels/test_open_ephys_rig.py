"""Tests for the neuropixels open ephys rig ETL."""

import os
import unittest
from pathlib import Path

from aind_metadata_mapper.neuropixels.open_ephys_rig import (  # type: ignore
    OpenEphysRigEtl
)
from tests.test_neuropixels import utils as test_utils

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "neuropixels"
)


class TestOpenEphysRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        """Test ETL workflow."""
        etl = OpenEphysRigEtl(
            self.input_source,
            self.output_dir,
            open_ephys_settings_sources=[
                RESOURCES_DIR / "settings.xml",
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
            modification_date=self.expected.modification_date,
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
            RESOURCES_DIR / "open-ephys-rig.json",
        )


if __name__ == "__main__":
    unittest.main()
