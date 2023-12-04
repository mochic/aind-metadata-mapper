import re
import xml
import typing
import pydantic
from aind_data_schema import device, rig

from . import utils


# class DxdiagSettings(pydantic.BaseModel):

#     model: typing.Optional[str] = None
#     height: typing.Optional[int] = None
#     width: typing.Optional[int] = None
#     refresh_rate: typing.Optional[float] = None


class DxdiagMonitor(
    device.Monitor,
    metaclass=utils.AllOptionalMeta,
    required_fields=[
        "height",
        "width",
        "size_unit",
        "model",
    ]
):
    """
    """


def extract(content: str) -> DxdiagMonitor:
    loaded = xml.etree.ElementTree.fromstring(content)
    modes = list(utils.find_elements(loaded, "currentmode"))
    height = None
    width = None
    if len(modes) > 0:
        parsed_mode = re.match(
            r"(\d*) x (\d*) (\(\d{2} bit\)) \((\d*)Hz\)",
            modes[0].text
        )
        if parsed_mode:
            height = int(parsed_mode[2])
            width = int(parsed_mode[1])

    models = list(utils.find_elements(loaded, "monitormodel"))
    if len(models) < 1:
        model = None
    else:
        model = models[0].text
    
    return DxdiagMonitor(
        model=model,
        height=height,
        width=width,
    )


def transform(dxdiag_monitor: DxdiagMonitor, current_rig: rig.Rig) -> \
    rig.Rig:
    """
    Notes
    -----
    modifies current_rig inplace.
    """
    copied = current_rig.copy()  # dont mutated original
    for idx, device in enumerate(copied.stimulus_devices):
        if device.device_type == "Monitor":
            break
    else:
        raise Exception
    monitor = copied.stimulus_devices[idx]
    utils.merge_devices(
        monitor,
        dxdiag_monitor,
    )
    # copied_dict = copied.dict()
    # print(copied.stimulus_devices)
    return copied
    # updated_monitor_dict = updated_monitor.dict()
    # print(updated_monitor_dict)
    # copied_dict["stimulus_devices"].pop(idx)
    # copied_dict["stimulus_devices"].insert(idx, updated_monitor)
    # # print(dxdiag_monitor.model)
    # # obj = copied.dict()
    # # print(obj["stimulus_devices"])
    # print(copied_dict["stimulus_devices"])
    # return rig.Rig.parse_obj(copied_dict)  # applies updates


    
