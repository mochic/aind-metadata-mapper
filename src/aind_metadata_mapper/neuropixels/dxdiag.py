import re
import xml
import typing
import pydantic
from aind_data_schema import device

from . import utils


class DxdiagSettings(pydantic.BaseModel):

    model: typing.Optional[str] = None
    height: typing.Optional[int] = None
    width: typing.Optional[int] = None
    refresh_rate: typing.Optional[float] = None


def extract(content: str) -> DxdiagSettings:
    loaded = xml.etree.ElementTree.fromstring(content)
    modes = list(utils.find_elements(loaded, "currentmode"))
    height = None
    width = None
    refresh_rate = None
    if len(modes) > 0:
        parsed_mode = re.match(
            r"(\d*) x (\d*) (\(\d{2} bit\)) \((\d*)Hz\)",
            modes[0].text
        )
        if parsed_mode:
            height = int(parsed_mode[2])
            width = int(parsed_mode[1])
            refresh_rate = float(parsed_mode[4])

    models = list(utils.find_elements(loaded, "monitormodel"))
    if len(models) < 1:
        model = None
    else:
        model = models[0].text
    
    return DxdiagSettings(
        model=model,
        height=height,
        width=width,
        refresh_rate=refresh_rate,
    )


def transform(settings, **overloads) -> device.Monitor:
    monitor_properties = {}
    
    if settings.height and settings.width:
        monitor_properties["height"] = settings.height
        monitor_properties["width"] = settings.width
        monitor_properties["size_unit"] = "pixel"
    
    if settings.model:
        monitor_properties["model"] = settings.model
    
    return device.Monitor(
        **monitor_properties,
        **overloads
    )
