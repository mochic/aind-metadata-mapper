"""ETL class for neuropixels rigs."""

import pathlib
import pydantic
import datetime
import logging
from aind_data_schema.core import rig

from ..core import BaseEtl


logger = logging.getLogger(__name__)


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
        
        return extracted_source.current
