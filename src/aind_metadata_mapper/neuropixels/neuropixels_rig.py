"""Base ETL class for neuropixels rigs."""
import pathlib
import pydantic
import logging
from aind_data_schema.core import rig  # type: ignore

from ..core import BaseEtl


logger = logging.getLogger(__name__)


class NeuropixelsRigContext(pydantic.BaseModel):
    
    current: rig.Rig


class NeuropixelsRigEtl(BaseEtl):
    """Neuropixels rig ETL class. Extracts information from rig-related files
    and transforms them into an aind-data-schema rig.Rig instance.
    """

    def __init__(
        self,
        input_source: pathlib.Path,
        output_directory: pathlib.Path,
    ):
        """Class constructor for Neuropixels rig etl class.

        Parameters
        ----------
        input_source : Path
          Can be a string or a Path
        output_directory : Path
          The directory where to save the json files.
        """
        self.input_source: pathlib.Path = input_source
        self.output_directory = output_directory

    def _extract(self) -> rig.Rig:
        """Extracts rig-related information from config files.
        """
        return rig.Rig.model_validate_json(
            self.input_source.read_text(),
        )

    def _transform(self, extracted_source: rig.Rig) -> rig.Rig:
        """Transforms extracted rig context into aind-data-schema rig.Rig
        instance.
        """
        return extracted_source
