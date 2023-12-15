import unittest
import pathlib
import json
import shutil
import typing
import tempfile

from aind_data_schema.core import rig
from aind_metadata_mapper.neuropixels import NeuropixelsRigException
from aind_metadata_mapper.neuropixels import neuropixels_rig as neuropixels_rig


def setup_neuropixels_etl_dirs(
    *resources: pathlib.Path
) -> tuple[pathlib.Path, pathlib.Path, typing.Callable[[], None]]:
    """Sets up a temporary input/output directory context for neuropixels etl.

    Parameters
    ----------
    resources: paths to etl resources to move to input dir

    Returns
    -------
    input_dir: path to etl input dir
    output_dir: path to etl output dir
    clean_up: cleanup function for input/output dirs
    """
    input_dir = pathlib.Path(tempfile.mkdtemp())
    for resource in resources:
        shutil.copy2(resource, input_dir)

    output_dir = pathlib.Path(tempfile.mkdtemp())

    def clean_up():
        """Clean up callback for temporary directories and their contents."""
        shutil.rmtree(input_dir)
        shutil.rmtree(output_dir)

    return (
        input_dir,
        output_dir,
        clean_up,
    )


class TestRig(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    def test_etl(self):
        etl = neuropixels_rig.NeuropixelsRigEtl(
            self.input_dir_good,
            self.output_dir_good,
            self.input_dir_good / "rig.partial.json",
            "Sync",
            "Stim",
            "Reward Delivery: 0",
        )
        etl.run_job()

        updated = rig.Rig.model_validate_json(
            (self.output_dir_good / "rig.json").read_text()
        )

        expected = rig.Rig.model_validate_json(
            pathlib.Path(
                "./tests/resources/neuropixels/rig.expected.json"
            ).read_text()
        )
        print(updated.stimulus_devices)
        print(expected.stimulus_devices)
        print(self.output_dir_good / "rig.json")
        updated_json = json.loads((self.output_dir_good / "rig.json").read_text())
        expected_json = json.loads(
            pathlib.Path(
                "./tests/resources/neuropixels/rig.expected.json"
            ).read_text()
        )
        print(self.output_dir_good / "rig.json")
        expected_json["modification_date"] = updated_json["modification_date"]
        assert updated_json == expected_json

    def test_etl_missing_sync(self):
        etl = neuropixels_rig.NeuropixelsRigEtl(
            self.input_dir_missing_camstim,
            self.output_dir_missing_camstim,
            self.input_dir_missing_camstim / "rig.partial.json",
            "Sync",
            "Stim",
            "Reward Delivery: 0",
        )
        etl.run_job()

        updated = rig.Rig.model_validate_json(
            (self.output_dir_missing_camstim / "rig.json").read_text()
        )
        # print(self.output_dir_missing_camstim / "rig.json")
        expected = rig.Rig.model_validate_json(
            pathlib.Path(
                "./tests/resources/neuropixels/rig.expected-missing-camstim.json"
            ).read_text()
        )
        expected_json["modification_date"] = updated_json["modification_date"]
        assert updated == expected

    def setUp(self):
        """Moves required test resources to testing directory.
        """
        rig_partial_path = pathlib.Path(
            "./tests/resources/neuropixels/rig.partial.json"
        )
        mvr_path = pathlib.Path(
            "./tests/resources/neuropixels/mvr.ini"
        )
        mvr_mapping_path = pathlib.Path(
            "./tests/resources/neuropixels/mvr.mapping.json"
        )
        sync_path = pathlib.Path(
            "./tests/resources/neuropixels/sync.yml"
        )
        dxdiag_path = pathlib.Path(
            "./tests/resources/neuropixels/dxdiag.xml"
        )
        camstim_path = pathlib.Path(
            "./tests/resources/neuropixels/camstim.yml"
        )
        open_ephys_path = pathlib.Path(
            "./tests/resources/neuropixels/open_ephys.settings.xml"
        )
        sound_measure_path = pathlib.Path(
            "./tests/resources/neuropixels/soundMeasure_NP2_20230817_150735_sound_level.txt"
        )

        # setup good directory
        self.input_dir_good, self.output_dir_good, self._cleanup_good = \
            setup_neuropixels_etl_dirs(
                rig_partial_path,
                mvr_path,
                mvr_mapping_path,
                sync_path,
                dxdiag_path,
                camstim_path,
                open_ephys_path,
                sound_measure_path,
            )
        
        self.input_dir_missing_camstim, self.output_dir_missing_camstim, \
            self._cleanup_missing_camstim = \
            setup_neuropixels_etl_dirs(
                rig_partial_path,
                mvr_path,
                mvr_mapping_path,
                sync_path,
                dxdiag_path,
            )


    def tearDown(self):
        """Removes test resources and directory.
        """
        # self._cleanup_good()