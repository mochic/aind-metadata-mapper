"""ETL class for neuropixels rigs."""
import ast
import pathlib
import enum
import pydantic
import datetime
import logging
from aind_data_schema.core import rig

from ..core import BaseEtl


logger = logging.getLogger(__name__)


class UpdateType(enum.Enum):
    major = "major"
    minor = "minor"
    patch = "patch"


def update_rig_id(rig_id: str,
        update_type: UpdateType = UpdateType.patch,
) -> str:
    rig_name, version_str = rig_id.split("_")
    
    major_str, minor_str, patch_str = version_str.split(".")
    major = ast.literal_eval(major_str)
    minor = ast.literal_eval(minor_str)
    patch = ast.literal_eval(patch_str)

    if update_type == UpdateType.major:
        major += 1
        minor = 0
        patch = 0
    elif update_type == UpdateType.minor:
        minor += 1
        patch = 0
    else:
        patch += 1

    return f"{rig_name}_{major}.{minor}.{patch}"


class RigContext(pydantic.BaseModel):
    
    current: rig.Rig


class NeuropixelsRigEtl(BaseEtl):
    """Neuropixels rig ETL class. Extracts information from rig-related files
    and transforms them into an aind-data-schema rig.Rig instance.
    """

    def __init__(
        self,
        input_source: pathlib.Path,
        output_directory: pathlib.Path,
        modification_date: datetime.date = None,
        update_type: UpdateType = UpdateType.patch,
    ):
        """Class constructor for Neuropixels rig etl class.

        Parameters
        ----------
        input_source : Path
          Can be a string or a Path
        output_directory : Path
          The directory where to save the json files.
        """
        super().__init__(input_source, output_directory)
        self.modification_date = modification_date
        self.update_type = update_type

    def _extract(self) -> RigContext:
        """Extracts rig-related information from config files.
        """
        return RigContext(
            current=rig.Rig.model_validate_json(
                self.input_source.read_text()
            ),
        )

    def _transform(self, extracted_source: RigContext) -> rig.Rig:
        """Transforms extracted rig context into aind-data-schema rig.Rig
        instance.
        """
        if self.modification_date is not None:
            extracted_source.current.modification_date = \
                self.modification_date
        else:
            extracted_source.current.modification_date = \
                datetime.date.today()
        
        extracted_source.current.rig_id = update_rig_id(
            extracted_source.current.rig_id,
            self.update_type,
        )
        
        return extracted_source.current
