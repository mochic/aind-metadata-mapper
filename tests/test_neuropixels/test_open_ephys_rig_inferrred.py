"""Tests for the neuropixels open ephys rig ETL with inferred probe mapping."""

import os
import unittest
from pathlib import Path

# from aind_data_schema.core import rig  # type: ignore
from aind_data_schema.core.rig import Rig

from aind_metadata_mapper.neuropixels import open_ephys_rig  # type: ignore
from aind_metadata_mapper.neuropixels.open_ephys_rig import OpenEphysRigEtl
from tests.test_neuropixels import utils as test_utils

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "neuropixels"
)


class TestOpenEphysRigEtlInferred(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        """Test ETL workflow with inferred probe mapping."""
        etl = OpenEphysRigEtl(
            self.input_source,
            self.output_dir,
            open_ephys_settings_sources=[
                RESOURCES_DIR / "settings.mislabeled-probes-0.xml",
                RESOURCES_DIR / "settings.mislabeled-probes-1.xml",
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

    def test_etl_mismatched_probe_count(self):
        """Test ETL workflow with mismatched probe count."""
        base_rig = Rig.model_validate_json(self.input_source.read_text())
        base_rig.ephys_assemblies.pop()
        base_rig.write_standard_file(
            self.input_source.parent, prefix="mismatched"
        )
        etl = open_ephys_rig.OpenEphysRigEtl(
            self.input_source.parent / "mismatched_rig.json",
            self.output_dir,
            open_ephys_settings_sources=[
                RESOURCES_DIR / "settings.mislabeled-probes-0.xml",
                RESOURCES_DIR / "settings.mislabeled-probes-1.xml",
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
            RESOURCES_DIR / "open-ephys-rig-inferred.json"
        )

    def tearDown(self):
        """Removes test resources and directory."""
        self._cleanup()


if __name__ == "__main__":
    unittest.main()
