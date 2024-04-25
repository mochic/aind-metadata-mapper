"""Tests for the neuropixels open ephys rig ETL modification date updates."""

import os
import unittest
from pathlib import Path

from aind_data_schema.core.rig import Rig  # type: ignore
from aind_metadata_mapper.neuropixels.open_ephys_rig import (  # type: ignore
    OpenEphysRigEtl,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "neuropixels"
)


class TestOpenEphysRigEtlModificationDateUpdate(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_transform_no_update(self):
        """Tests etl transform when probe serial numbers dont change."""
        initial_rig_path = RESOURCES_DIR / "open-ephys_rig.json"
        initial_rig_model = Rig.model_validate_json(
            initial_rig_path.read_text(),
        )
        etl = OpenEphysRigEtl(
            initial_rig_path,
            Path("."),
            open_ephys_settings_sources=[
                RESOURCES_DIR / "settings.xml",
            ],
        )
        extracted = etl._extract()
        transformed = etl._transform(extracted)
        self.assertEqual(initial_rig_model.rig_id, transformed.rig_id)

    def test_transform_update_manipulators(self):
        """Tests etl transform when manipulator serial numbers change."""
        initial_rig_path = RESOURCES_DIR / "open-ephys_rig.json"
        initial_rig_model = Rig.model_validate_json(
            initial_rig_path.read_text(),
        )
        etl = OpenEphysRigEtl(
            initial_rig_path,
            Path("."),
            open_ephys_settings_sources=[],
            probe_manipulator_serial_numbers=[
                (
                    "Ephys Assembly A",
                    "SN45358",
                ),
            ],
        )
        extracted = etl._extract()
        transformed = etl._transform(extracted)
        self.assertNotEqual(initial_rig_model.rig_id, transformed.rig_id)


if __name__ == "__main__":
    unittest.main()
