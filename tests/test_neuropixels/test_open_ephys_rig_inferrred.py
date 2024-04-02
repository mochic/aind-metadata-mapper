import unittest
import pathlib
from aind_data_schema.core import rig  # type: ignore
from aind_metadata_mapper.neuropixels import open_ephys_rig  # type: ignore

from . import utils as test_utils


class TestOpenEphysRigEtlInferred(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = open_ephys_rig.OpenEphysRigEtl(
            self.input_source,
            self.output_dir,
            open_ephys_settings_sources=[
                pathlib.Path(
                    "./tests/resources/neuropixels/"
                    "settings.mislabeled-probes-0.xml"
                ),
                pathlib.Path(
                    "./tests/resources/neuropixels/"
                    "settings.mislabeled-probes-1.xml"
                ),
            ],
            probe_manipulator_serial_numbers=[
                ('Ephys Assembly A', 'SN45356', ),
                ('Ephys Assembly B', 'SN45484', ),
                ('Ephys Assembly C', 'SN45485', ),
                ('Ephys Assembly D', 'SN45359', ),
                ('Ephys Assembly E', 'SN45482', ),
                ('Ephys Assembly F', 'SN45361', ),
            ],
        )
        etl.run_job()

        assert self.load_updated() == self.expected

    def test_etl_mismatched_probe_count(self):
        base_rig = rig.Rig.model_validate_json(self.input_source.read_text())
        base_rig.ephys_assemblies.pop()
        base_rig.write_standard_file(
            self.input_source.parent, prefix='mismatched')
        etl = open_ephys_rig.OpenEphysRigEtl(
            self.input_source.parent / "mismatched_rig.json",
            self.output_dir,
            open_ephys_settings_sources=[
                pathlib.Path(
                    "./tests/resources/neuropixels/"
                    "settings.mislabeled-probes-0.xml"
                ),
                pathlib.Path(
                    "./tests/resources/neuropixels/"
                    "settings.mislabeled-probes-1.xml"
                ),
            ],
            probe_manipulator_serial_numbers=[
                ('Ephys Assembly A', 'SN45356', ),
                ('Ephys Assembly B', 'SN45484', ),
                ('Ephys Assembly C', 'SN45485', ),
                ('Ephys Assembly D', 'SN45359', ),
                ('Ephys Assembly E', 'SN45482', ),
                ('Ephys Assembly F', 'SN45361', ),
            ],
        )
        etl.run_job()

    def setUp(self):
        """Moves required test resources to testing directory.
        """
        # test directory
        self.input_source, self.output_dir, self.expected, \
                self.load_updated, self._cleanup = \
            test_utils.setup_neuropixels_etl_dirs(
                pathlib.Path(
                    "./tests/resources/neuropixels/"
                    "open-ephys-rig-inferred.json"
                ),
            )

    def tearDown(self):
        """Removes test resources and directory.
        """
        self._cleanup()