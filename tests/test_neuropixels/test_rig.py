import unittest
import pathlib
import json
import shutil
import typing
import tempfile

from aind_data_schema import rig
from aind_metadata_mapper.neuropixels import NeuropixelsRigException, \
    rig as neuropixels_rig

# from . import get_current_rig


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
            self.good_input_dir,
            self.good_output_dir,
            current=self.good_input_dir / "rig.json",
        )
        etl.run_job()

        updated = rig.Rig.parse_json(
            (self.good_output_dir / "rig.json").read_text()
        )

        expected = rig.Rig.parse_file(
            (self.good_output_dir / "expected-rig.json")
        )

        assert updated == expected

    # def test_extract_bad_mapping(self):
    #     content = pathlib.Path(
    #         "./tests/resources/neuropixels/good/mvr.ini"
    #     ).read_text()
    #     mapping = json.loads(pathlib.Path(
    #         "./tests/resources/neuropixels/bad/mvr.mapping.json"
    #     ).read_text())
    #     with self.assertRaises(NeuropixelsRigException):
    #         mvr_camera.extract(content, mapping)

    def setUp(self):
        """Moves required test resources to testing directory.
        """
        good_rig_partial_path = pathlib.Path(
            "./tests/resources/neuropixels/current-rig.json"
        )
        good_mvr_path = pathlib.Path(
            "./tests/resources/neuropixels/good/mvr.ini"
        )
        good_mvr_mapping_path = pathlib.Path(
            "./tests/resources/neuropixels/good/mvr.mapping.json"
        )
        good_sync_path = pathlib.Path(
            "./tests/resources/neuropixels/good/sync.yml"
        )
        good_dxdiag_path = pathlib.Path(
            "./tests/resources/neuropixels/dxdiag.yml"
        )
        camstim_path = pathlib.Path(
            "./tests/resources/neuropixels/camstim.yml"
        )

        # setup good directory
        self.good_input_dir, self.good_output_dir, self._cleanup_good = \
            setup_neuropixels_etl_dirs(
                good_rig_partial_path,
                good_mvr_path,
                good_mvr_mapping_path,
                good_sync_path,
                good_dxdiag_path,
                camstim_path,
            )

        # setup bad mvr directory
        # bad_mvr_path = pathlib.Path(
        #     "./tests/resources/neuropixels/bad/mvr.ini"
        # )
        # self.bad_mvr_input_dir, \
        #     self.bad_mvr_output_dir, self._cleanup_bad_mvr = \
        #     setup_neuropixels_etl_dirs(
        #         good_rig_partial_path,
        #         bad_mvr_path,
        #         good_mvr_mapping_path,
        #         good_sync_path,
        #     )

        # setup bad mvr mapping directory
        # bad_mvr_mapping_path = pathlib.Path(
        #     "./tests/resources/neuropixels/bad/mvr.mapping.json"
        # )
        # self.bad_mvr_mapping_input_dir, \
        #     self.bad_mvr_mapping_output_dir, self._cleanup_bad_mvr_mapping = \
        #     setup_neuropixels_etl_dirs(
        #         good_rig_partial_path,
        #         good_mvr_path,
        #         bad_mvr_mapping_path,
        #         good_sync_path,
        #     )

        # setup bad rig partial camera directory
        # bad_rig_partial_camera_path = pathlib.Path(
        #     "./tests/resources/neuropixels/bad/rig-camera/rig.partial.json"
        # )
        # self.bad_rig_partial_camera_input_dir, \
        #     self.bad_rig_partial_camera_output_dir, \
        #     self._cleanup_bad_rig_partial_camera = \
        #     setup_neuropixels_etl_dirs(
        #         bad_rig_partial_camera_path,
        #         good_mvr_path,
        #         good_mvr_mapping_path,
        #         good_sync_path,
        #     )

        # setup bad rig partial sync directory
        # bad_rig_partial_sync_path = pathlib.Path(
        #     "./tests/resources/neuropixels/bad/rig-sync/rig.partial.json"
        # )
        # self.bad_rig_partial_sync_input_dir, \
        #     self.bad_rig_partial_sync_output_dir, \
        #     self._cleanup_bad_rig_partial_sync = \
        #     setup_neuropixels_etl_dirs(
        #         bad_rig_partial_sync_path,
        #         good_mvr_path,
        #         good_mvr_mapping_path,
        #         good_sync_path,
        #     )

        # setup bad rig directory missing required files
        # self.missing_sync_input_dir, \
        #     self.missing_sync_output_dir, \
        #     self._cleanup_missing_sync = \
        #     setup_neuropixels_etl_dirs(
        #         good_rig_partial_path,
        #         good_mvr_path,
        #         good_mvr_mapping_path,
        #     )

    def tearDown(self):
        """Removes test resources and directory.
        """
        # self._cleanup_good()