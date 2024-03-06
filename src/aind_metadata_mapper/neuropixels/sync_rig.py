import typing
import pathlib
import yaml  # type: ignore
from aind_data_schema.core import rig  # type: ignore
from aind_data_schema.models import devices  # type: ignore

from . import neuropixels_rig, NeuropixelsRigException


class ExtractContext(neuropixels_rig.NeuropixelsRigContext):

    config: typing.Any


class SyncRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    def __init__(self, 
            input_source: pathlib.Path,
            output_directory: pathlib.Path,
            config_source: pathlib.Path,
            sync_daq_name: str = "Sync",
            **kwargs
    ):
        super().__init__(input_source, output_directory, **kwargs)
        self.config_source = config_source
        self.sync_daq_name = sync_daq_name

    def _extract(self) -> ExtractContext:
        return ExtractContext(
            current=super()._extract(),
            config=yaml.safe_load(self.config_source.read_text()),
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
