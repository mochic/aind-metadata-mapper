"""Extracts information from microsoft executable Set-Volume.exe."""
import pydantic
import re

from aind_data_schema import device

"""This code is just here as a placeholder until a soundcard.
"""


class SetVolumeInfo(pydantic.BaseModel):

    model: str
    master_volume: int


def extract(set_volume_content: str, dxdiag_content: str) -> SetVolumeInfo:
    # model = re.find(r"Report for Speakers \((.*)\)", content)
    # master_volume = re.find(r"Master volume level = (\d*)")
    return SetVolumeInfo(
        model=re.find(r"Report for Speakers \((.*)\)", content),
        master_volume=re.find(r"Master volume level = (\d*)", content),
    )


def transform(
        info: SetVolumeInfo, **overloads):
    """Will eventually output a soundcard"""
    return device.Speaker(
        model=info.model,
        **overloads
    )
