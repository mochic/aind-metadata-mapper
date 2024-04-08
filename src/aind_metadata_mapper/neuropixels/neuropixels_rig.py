"""Base ETL class for neuropixels rigs."""

import logging
from pathlib import Path

from aind_data_schema.core.rig import Rig
from pydantic import BaseModel

from aind_metadata_mapper.core import BaseEtl

logger = logging.getLogger(__name__)


class NeuropixelsRigContext(BaseModel):
    """Base context for neuropixels rig etl."""

    current: Rig


class NeuropixelsRigEtl(BaseEtl):
    """Neuropixels rig ETL class. Extracts information from rig-related files
    and transforms them into an aind-data-schema rig.Rig instance.
    """

    def __init__(
        self,
        input_source: Path,
        output_directory: Path,
    ):
        """Class constructor for Neuropixels rig etl class.

        Parameters
        ----------
        input_source : Path
          Can be a string or a Path
        output_directory : Path
          The directory where to save the json files.
        """
        self.input_source: Path = input_source
        self.output_directory = output_directory

    def _extract(self) -> Rig:
        """Extracts rig-related information from config files."""
        return Rig.model_validate_json(
            self.input_source.read_text(),
        )

    def _transform(self, extracted_source: Rig) -> Rig:
        """Transforms extracted rig context into aind-data-schema rig.Rig
        instance.
        """
        return extracted_source
