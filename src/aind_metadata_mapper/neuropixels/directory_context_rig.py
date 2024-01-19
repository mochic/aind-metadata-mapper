"""ETL class for neuropixels rigs."""

import json
import pathlib
import pydantic
import datetime
import logging
from aind_data_schema.core import rig

from ..core import BaseEtl

from . import NeuropixelsRigException


logger = logging.getLogger(__name__)


class RigContext(pydantic.BaseModel):
    
    current: rig.Rig


class DirectoryContextRigEtl(BaseEtl):
    """Neuropixels rig ETL class. Extracts information from rig-related files
    and transforms them into an aind-data-schema rig.Rig instance.
    """

    def __init__(
        self,
        input_source: pathlib.Path,
        output_directory: pathlib.Path,
        rig_resource_name: str = "rig.json",
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
        self.rig_resource_name = rig_resource_name
        self.modification_date = modification_date

    def _extract(self) -> rig.Rig:
        """Extracts rig-related information from config files.
        """
        if not self.input_source.is_dir():
            raise NeuropixelsRigException(
                "Input source is not a directory. %s" % self.input_source
            )
    
        # return rig.Rig.model_validate_json(
        #     self.input_source.read_text()
        # )
        return rig.Rig.model_validate_json(
            (self.input_source / self.rig_resource_name).read_text()
        )

    def _transform(self, extracted_source: rig.Rig) -> rig.Rig:
        """Transforms extracted rig context into aind-data-schema rig.Rig
        instance.
        """
        if self.modification_date is not None:
            extracted_source.modification_date = \
                self.modification_date
        else:
            extracted_source.modification_date = \
                datetime.date.today()
        
        return extracted_source
