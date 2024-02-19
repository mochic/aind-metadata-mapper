"""Core abstract class that can be used as a template for etl jobs."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, TypeVar, Generic

from aind_data_schema.base import AindCoreModel
from pydantic import ValidationError, BaseModel


_T = TypeVar('_T', bound=BaseModel)
_V = TypeVar('_V', bound=Union[Optional[Dict[str, str]], Optional[Dict[str, Path]], Optional[Dict[str, List[Path]]]])


class BaseEtl(ABC, Generic[_T, _V]):
    """Base etl class. Defines interface for extracting, transforming, and
    loading input sources into a json file saved locally."""

    def __init__(
            self,
            input_sources: _V = None,
            output_directory: Optional[Path] = None,
            specific_model: Optional[_T] = None
    ):
        """
        Class constructor for Base etl class.
        Parameters
        ----------
        input_sources : _V
          Locations of any directories that contain information that needs to
          be parsed. Default is None
        output_directory : Optional[Path]
          Optional save the metadata file to this directory. Default is to
          return the AindModel as a json string if None is supplied.
        specific_model : _T
          A BaseModel that is missing required information.
          Default is None
        """
        self.input_sources = input_sources
        self.output_directory = output_directory
        self.specific_model = specific_model

    @abstractmethod
    def _extract(self) -> Any:
        """
        Extract the data from self.input_source.
        Returns
        -------
        Any
          It's not clear yet whether we'll be processing binary data, dicts,
          API Responses, etc.

        """

    @abstractmethod
    def _transform(self, extracted_source: Any) -> AindCoreModel:
        """
        Transform the data extracted from the extract method.
        Parameters
        ----------
        extracted_source : Any
          Output from _extract method.

        Returns
        -------
        AindCoreModel

        """

    def _load(self, transformed_data: AindCoreModel) -> str:
        """
        Save the AindCoreModel from the transform method.
        Parameters
        ----------
        transformed_data : AindCoreModel

        Returns
        -------
        str

        """
        if self.output_directory is not None:
            try:
                transformed_data.write_standard_file(
                    output_directory=self.output_directory
                )
                return f"Successfully wrote file to {self.output_directory}"
            except Exception as e:
                logging.error(f"Error writing file: {e}")
                return f"Error writing file to: {self.output_directory}"
        else:
            return transformed_data.model_dump_json()

    @staticmethod
    def _run_validation_check(model_instance: AindCoreModel) -> None:
        """
        Check the response contents against either
        aind_data_schema.subject or aind_data_schema.procedures.
        Parameters
        ----------
        model_instance : AindCoreModel
          Contents from the service response.
        """
        try:
            model_instance.model_validate(model_instance.__dict__)
            logging.debug("No validation errors detected.")
        except ValidationError:
            logging.warning(
                "Validation errors were found. This may be due to "
                "mismatched versions or data not found in the "
                "databases.",
                exc_info=True,
            )

    def run_job(self) -> str:
        """
        Run the etl job
        Returns
        -------
        None

        """
        extracted = self._extract()
        transformed = self._transform(extracted_source=extracted)
        self._run_validation_check(transformed)
        response_message = self._load(transformed)
        return response_message
