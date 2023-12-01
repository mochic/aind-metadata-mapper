import yaml
import pydantic
import typing 

from aind_data_schema import device

from . import utils


class SyncSettings(pydantic.BaseModel):

    name: str
    freq: float
    line_labels: list[tuple[int, str]]


class SyncDAQChannel(
    device.DAQChannel,
    metaclass=utils.AllOptionalMeta,
    required_fields=[
        "device_name",
        "channel_name",
        "channel_index",
        "sample_rate",
    ]
):
    """
    """


def extract(content: str) -> list[SyncDAQChannel]:
    """Extracts DAQ-related information from MPE sync config.
    """
    config = yaml.safe_load(content)
    return [
        SyncDAQChannel(
            channel_name=name,
            channel_type="Digital Input",
            device_name=config["device"],
            event_based_sampling=False,
            channel_index=line,
            sample_rate=config["freq"],
            sample_rate_unit="hertz",
        )
        for line, name in config["line_labels"].items()
    ]


def transform(settings: SyncSettings, **overloads) -> list[device.DAQChannel]:
    return [
        device.DAQChannel(
            channel_name=name,
            channel_type="Digital Input",
            device_name=settings.name,
            event_based_sampling=False,
            channel_index=line,
            sample_rate=settings.freq,
            sample_rate_unit="hertz",
            **overloads
        )
        for line, name in settings.line_labels
    ]
