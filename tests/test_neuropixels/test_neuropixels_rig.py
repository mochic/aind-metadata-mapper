"""Tests for the neuropixels open ephys rig ETL with inferred probe mapping."""

import os
import unittest
from pathlib import Path
from datetime import date

from aind_metadata_mapper.neuropixels.neuropixels_rig import (  # type: ignore
    NeuropixelsRigEtl
)
from tests.test_neuropixels import utils as test_utils

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "neuropixels"
)


class TestNeuropixelsRig(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_update_modification_date(self):
        """Test ETL workflow with inferred probe mapping."""
        etl = NeuropixelsRigEtl(
            self.input_source,
            self.output_dir,
        )
        extracted = etl._extract()
        transformed = etl._transform(extracted)
        NeuropixelsRigEtl.update_modification_date(transformed)
        assert transformed.modification_date == date.today()

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
