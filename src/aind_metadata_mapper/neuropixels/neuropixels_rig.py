"""ETL class for neuropixels rigs."""

import json
import yaml
import pathlib
import pydantic
import datetime
import typing
from xml.etree import ElementTree
from aind_data_schema.core import rig

from ..core import BaseEtl

from . import mvr, sync, dxdiag, camstim, utils, \
    NeuropixelsRigException


class RigContext(pydantic.BaseModel):
    
    current: typing.Optional[dict]
    mvr_context: typing.Optional[tuple[typing.Any, dict]]
    sync: typing.Optional[dict]
    dxdiag: typing.Optional[typing.Any]
    camstim: typing.Optional[dict]


class NeuropixelsRigEtl(BaseEtl):
    """Neuropixels rig ETL class. Extracts information from rig-related files
    and transforms them into an aind-data-schema rig.Rig instance.
    """

    def __init__(
        self,
        input_source: pathlib.Path,
        output_directory: pathlib.Path,
        current: pathlib.Path,
        sync_name: str,
        monitor_name: str,
        reward_delivery_name: str,
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
        self.current = current
        self.sync_name = sync_name
        self.monitor_name = monitor_name
        self.reward_delivery_name = reward_delivery_name
        self.modification_date = modification_date

    def _extract(self) -> RigContext:
        """Extracts rig-related information from config files.
        """
        if not self.input_source.is_dir():
            raise NeuropixelsRigException(
                "Input source is not a directory. %s" % self.input_source
            )
        # add logging?
        return RigContext(
            current=json.loads(self.current.read_text()),
            mvr_context=(
                utils.load_config(self.input_source / "mvr.ini"),
                json.loads(
                    (self.input_source / "mvr.mapping.json").read_text()
                ),
            ),
            sync=yaml.safe_load(
                (self.input_source / "sync.yml").read_text()
            ),
            dxdiag=ElementTree.fromstring(
                (self.input_source / "dxdiag.xml").read_text()
            ),
            camstim=yaml.safe_load(
                (self.input_source / "camstim.yml").read_text()
            ),
        )

    def _transform(self, extracted_source: RigContext) -> rig.Rig:
        """Transforms extracted rig context into aind-data-schema rig.Rig
        instance.
        """
        if extracted_source.mvr_context:
            mvr.transform(
                *extracted_source.mvr_context,
                extracted_source.current,
            )

        if extracted_source.sync:
           sync.transform(
               extracted_source.sync,
               extracted_source.current,
               self.sync_name,
           ) 

        if extracted_source.dxdiag:
            dxdiag.transform_monitor(
                extracted_source.dxdiag,
                extracted_source.current,
                self.monitor_name,
            )

        # for NP rigs, reward delivery is <rig_id>-Stim
        reward_delivery_name = f"{extracted_source.current['rig_id']}-Stim"
        if extracted_source.camstim:
            camstim.transform(
                extracted_source.camstim,
                extracted_source.current,
                self.monitor_name,
                reward_delivery_name,
            )
        
        if self.modification_date is not None:
            extracted_source.current["modification_date"] = \
                self.modification_date
        else:
            extracted_source.current["modification_date"] = \
                datetime.date.today()
        
        print(extracted_source.current["stimulus_devices"])
        
        # current = rig.Rig.model_validate(extracted_source.current)
        current = rig.Rig(**extracted_source.current)
        print(current.__dict__["stimulus_devices"])
        return current
