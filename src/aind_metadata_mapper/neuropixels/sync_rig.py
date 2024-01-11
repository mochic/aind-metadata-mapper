import pydantic
import typing
import yaml
from aind_data_schema.core import rig
from aind_data_schema.models import devices
from . import directory_context_rig, utils, NeuropixelsRigException


class ExtractContext(pydantic.BaseModel):

    current: typing.Any
    config: typing.Any


class SyncRigEtl(directory_context_rig.DirectoryContextRigEtl):

    def __init__(self, 
            *args,
            config_resource_name: str = "sync.yml",
            sync_daq_name: str = "Sync",
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config_resource_name = \
            config_resource_name
        self.sync_daq_name = sync_daq_name

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            config=yaml.safe_load(
                (self.input_source / self.config_resource_name)
                    .read_text()
            )
        )

    def _transform(
            self,
            extracted_source: ExtractContext) -> rig.Rig:
        for daq in extracted_source.current.daqs:
            if daq.name == self.sync_daq_name:
                daq.channels = [
                    devices.DAQChannel(
                        channel_name=name,
                        channel_type="Digital Input",
                        device_name=self.sync_daq_name,
                        event_based_sampling=False,
                        channel_index=line,
                        sample_rate=extracted_source.config["freq"],
                        sample_rate_unit="hertz",
                    )
                    for line, name in 
                    extracted_source.config["line_labels"].items()
                ]
                break
        else:
            raise NeuropixelsRigException(
                "Sync daq not found on current rig. name=%s" %
                self.sync_daq_name
            )

        return super()._transform(extracted_source.current)
