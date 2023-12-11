"""ETL class for neuropixels rigs."""

import json
import yaml
import pathlib
import pydantic
import datetime
import configparser
import typing
from xml.etree import ElementTree
from aind_data_schema.core import rig

from ..core import BaseEtl

from . import mvr, sync, dxdiag, camstim, open_ephys, utils, \
    NeuropixelsRigException

class NeuropixelsRigException(Exception):
    """General error for MVR."""


# assembly name, serial number, height, width, frame rate
MVRCamera = tuple[str, str, int, int, float]
SyncChannel = tuple[int, str]  # di line index, name
# device name, sample rate, channels
SyncContext = tuple[str, float, list[SyncChannel]]
RigContext = tuple[dict, list[MVRCamera], SyncContext]


class RigContext(pydantic.BaseModel):
    
    current: dict
    mvr_context: tuple[typing.Any, dict]
    sync: dict
    dxdiag: typing.Any
    camstim: dict


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
        
        return rig.Rig.parse_obj(extracted_source.current)

        # # search for partial sync daq
        # sync_device_name, sync_sample_rate, sync_channels = sync_context
        # sync_daq_name = "Sync"
        # for idx, partial_daq in enumerate(partial["daqs"]):
        #     if partial_daq["name"] == sync_daq_name:
        #         # remove from daqs for later spread operation
        #         partial_sync_daq = partial["daqs"].pop(idx)
        #         break
        # else:
        #     raise NeuropixelsRigException(
        #         "Sync daq not found in partial rig. expected=%s" %
        #         sync_daq_name
        #     )

        # sync_daq = {
        #     **partial_sync_daq,
        #     "channels": [
        #         {
        #             "channel_name": name,
        #             "channel_type": "Digital Input",
        #             "device_name": sync_device_name,
        #             "event_based_sampling": False,
        #             "channel_index": line,
        #             "sample_rate": sync_sample_rate,
        #             "sample_rate_unit": "hertz"
        #         }
        #         for line, name in sync_channels
        #     ],
        # }

        # camera_assemblies = []
        # for partial_camera_assembly in partial["cameras"]:
        #     name = partial_camera_assembly["camera_assembly_name"]

        #     found = list(filter(
        #         lambda camera: camera[0] == name,
        #         mvr_cameras,
        #     ))
        #     if len(found) < 1:
        #         raise NeuropixelsRigException(
        #             "Camera assembly not found in partial rig. expected=%s"
        #             % name
        #         )

        #     assembly_name, serial_number, height, width, frame_rate = found[0]
        #     camera_assemblies.append({
        #         **partial_camera_assembly,
        #         "camera": {
        #             **partial_camera_assembly["camera"],
        #             "name": assembly_name,
        #             "serial_number": serial_number,
        #             "pixel_height": height,
        #             "pixel_width": width,
        #             "size_unit": "pixel",
        #             "max_frame_rate": frame_rate,
        #         }
        #     })

        # return rig.Rig.parse_obj({
        #     **partial,
        #     "modification_date": datetime.date.today(),
        #     "daqs": [
        #         *partial["daqs"],
        #         sync_daq,
        #     ],
        #     "cameras": camera_assemblies,
        # })