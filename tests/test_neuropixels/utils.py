import pathlib
import shutil
import typing
import tempfile

from aind_data_schema.core import rig  # type: ignore


def setup_neuropixels_etl_dirs(
    input_source: pathlib.Path,
    expected_json: pathlib.Path,
) -> tuple[
        pathlib.Path,
        pathlib.Path,
        rig.Rig,
        typing.Callable[[], rig.Rig],
        typing.Callable[[], None]
    ]:
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
    shutil.copy2(input_source, input_dir)

    output_dir = pathlib.Path(tempfile.mkdtemp())

    def load_updated():
        """Load updated rig.json."""
        return rig.Rig.model_validate_json(
            (output_dir / "rig.json").read_text()
        )

    def clean_up():
        """Clean up callback for temporary directories and their contents."""
        shutil.rmtree(input_dir)
        shutil.rmtree(output_dir)

    return (
        input_dir / input_source.name,
        output_dir,
        rig.Rig.model_validate_json(expected_json.read_text()),
        load_updated,
        clean_up,
    )
