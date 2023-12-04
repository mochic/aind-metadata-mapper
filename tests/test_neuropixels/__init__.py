import pathlib
from aind_data_schema import rig


def rehydrate_raw_rig(path: pathlib.Path):
    """Deserializes Rig instance from text file.
    """
    return rig.Rig.parse_raw(path.read_text())


def get_current_rig():
    """Test utility to stop repeating myself. Gets "current" rig model used for
     testing.
    """
    return rehydrate_raw_rig(
        pathlib.Path(
            "./tests/resources/neuropixels/current-rig.json"
        )
    )