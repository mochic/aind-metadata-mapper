import pathlib
import shutil
import typing
import tempfile


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
