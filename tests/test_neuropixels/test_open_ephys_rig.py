import unittest
import pathlib

from aind_metadata_mapper.neuropixels import open_ephys_rig  # type: ignore

from . import utils as test_utils


class TestOpenEphysRigEtl(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = open_ephys_rig.OpenEphysRigEtl(
            self.input_source,
            self.output_dir,
            open_ephys_settings_sources=[
                pathlib.Path("./tests/resources/neuropixels/settings.xml"),
            ],
            probe_manipulator_serial_numbers={
                'Ephys Assembly A': 'SN45356',
                'Ephys Assembly B': 'SN45484',
                'Ephys Assembly C': 'SN45485',
                'Ephys Assembly D': 'SN45359',
                'Ephys Assembly E': 'SN45482',
                'Ephys Assembly F': 'SN45361',
            },
            modification_date=self.expected.modification_date,
        )
        etl.run_job()
        
        assert self.load_updated() == self.expected

    def setUp(self):
        """Moves required test resources to testing directory.
        """
        # test directory
        self.input_source, self.output_dir, self.expected, \
                self.load_updated, self._cleanup = \
            test_utils.setup_neuropixels_etl_dirs(
                pathlib.Path(
                    "./tests/resources/neuropixels/rig.partial.json",
                ),
                pathlib.Path(
                    "./tests/resources/neuropixels/open_ephys_rig.expected.json"
                ),
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()