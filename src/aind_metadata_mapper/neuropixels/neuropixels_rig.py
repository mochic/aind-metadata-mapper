"""ETL class for neuropixels rigs."""

import json
import yaml
import pathlib
import pydantic
import datetime
import typing
import logging
from xml.etree import ElementTree
from aind_data_schema.core import rig
from aind_data_schema.models import devices

from ..core import BaseEtl

from . import mvr, sync, dxdiag, camstim, sound_measure, utils, open_ephys, \
    NeuropixelsRigException


logger = logging.getLogger(__name__)


class RigContext(pydantic.BaseModel):
    
    current: typing.Optional[dict]= pydantic.Field(..., )
    mvr_context: typing.Optional[tuple[typing.Any, dict]] = None
    sync: typing.Optional[dict] = None
    dxdiag: typing.Optional[typing.Any] = None
    camstim: typing.Optional[dict] = None
    open_ephys: typing.Optional[typing.Any] = None
    sound_measure: typing.Optional[str] = None


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
        mvr_map: dict[str, str],
        # hostname_map: dict[str, str],
        open_ephys_manipulator_serial_numbers: typing.Optional[dict[str, str]] = None,
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
        self.open_ephys_manipulator_serial_numbers = open_ephys_manipulator_serial_numbers

    def _extract(self) -> RigContext:
        """Extracts rig-related information from config files.
        """
        if not self.input_source.is_dir():
            raise NeuropixelsRigException(
                "Input source is not a directory. %s" % self.input_source
            )

        rig_context = {
            "current": json.loads(self.current.read_text()),
            "mvr_context": None,
            "sync": None,
            "dxdiag": None,
            "camstim": None,
        }
        
        mvr_ini_path = self.input_source / "mvr.ini"
        mvr_mapping_path = self.input_source / "mvr.mapping.json"
        if mvr_ini_path.exists() and mvr_mapping_path.exists():
            rig_context["mvr_context"] = (
                utils.load_config(mvr_ini_path),
                json.loads(mvr_mapping_path.read_text()),
            )
        
        sync_path = self.input_source / "sync.yml"
        if sync_path.exists():
            rig_context["sync"] = yaml.safe_load(sync_path.read_text())

        dxdiag_path = self.input_source / "dxdiag.xml"
        if dxdiag_path.exists():
            rig_context["dxdiag"] = ElementTree.fromstring(
                dxdiag_path.read_text()
            )
        
        camstim_path = self.input_source / "camstim.yml"
        if camstim_path.exists():
            rig_context["camstim"] = yaml.safe_load(camstim_path.read_text())

        open_ephys_path = self.input_source / "open_ephys.settings.xml"
        if open_ephys_path.exists():
            rig_context["open_ephys"] = open_ephys_path.read_text()

        sound_measure_paths = self.input_source.glob("soundMeasure*.txt")
        if len(sound_measure_paths) > 0:
            rig_context["sound_measure"] = sound_measure_paths[0].read_text()
        

        return RigContext(**rig_context)

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
               "Sync",
           ) 

        if extracted_source.dxdiag:
            dxdiag.transform_monitor(
                extracted_source.dxdiag,
                extracted_source.current,
                "Stim",
            )

        # for NP rigs, reward delivery is <rig_id>-Stim
        # reward_delivery_name = f"{extracted_source.current['rig_id']}-Stim"
        if extracted_source.camstim:
            camstim.transform(
                extracted_source.camstim,
                extracted_source.current,
                "Stim",
                f"{extracted_source.current['rig_id']}-Stim",
            )

        if extracted_source.open_ephys:
            open_ephys.transform(
                extracted_source.open_ephys,
                extracted_source.current,
                "Open Ephys",
                self.open_ephys_manipulator_serial_numbers,
            )
        
        if self.open_ephys_manipulator_serial_numbers is not None:
            open_ephys.transform_manipulators(
                self.open_ephys_manipulator_serial_numbers
            )

        if extracted_source.sound_measure:
            sound_measure.transform(
                extracted_source.sound_measure,
                extracted_source.current,
                'Speaker',
            )
        
        if self.modification_date is not None:
            extracted_source.current["modification_date"] = \
                self.modification_date
        else:
            extracted_source.current["modification_date"] = \
                datetime.date.today()
        
        return rig.Rig(**extracted_source.current)
