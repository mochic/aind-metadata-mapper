import yaml
import pathlib
from aind_data_schema.core import rig
from aind_data_schema.models import devices
from . import NeuropixelsRigException, neuropixels_rig


class SyncRigContext(neuropixels_rig.RigContext):

    current: rig.Rig
    config: dict


class SyncRigEtl(neuropixels_rig.NeuropixelsRigEtl):

    def __init__(self, 
            *args,
            sync_config_source: pathlib.Path,
            sync_daq_name: str = "Sync",
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.sync_config_source = sync_config_source
        self.sync_daq_name = sync_daq_name

    def _extract(self) -> SyncRigContext:
        return SyncRigContext(
            current=super()._extract().current,
            config=yaml.safe_load(
                self.sync_config_source.read_text()
            )
        )

    def _transform(
            self,
            extracted_source: SyncRigContext) -> rig.Rig:
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

        # return super()._transform(extracted_source.current)
        return super()._transform(extracted_source)
