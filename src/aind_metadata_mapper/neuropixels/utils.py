"""Shared utilities"""
import typing
import pathlib
import configparser
from xml.etree import ElementTree

from . import NeuropixelsRigException


def find_elements(et: ElementTree, name: str) -> \
    typing.Generator[ElementTree.Element, None, None]:
    """
    
    Notes
    -----
    - Name matches on tags are case insensitive match on tags for
     convenience
    """
    for element in et.iter():
        if element.tag.lower() == name.lower():
            yield element


def load_config(config_path: pathlib.Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


# def find_update(
#     items: typing.Iterable[dict],
#     filters: typing.Iterable[typing.Tuple[str, any]],  # property name, property value
#     **updates: any,
# ) -> None:
#     for idx, item in enumerate(items):
#         if all([
#             item.get(prop_name, None) == prop_value
#             for prop_name, prop_value in filters
#         ]):
#             items[idx] = {
#                 **item,
#                 **updates,
#             }
#             break
#     else:
#         raise NeuropixelsRigException("Failed to find matching item. filters: %s" % filters)
    

def find_update(
    items: typing.Iterable[typing.Any],
    filters: typing.Iterable[typing.Tuple[str, any]],  # property name, property value
    setter = lambda item, name, value: setattr(item, name, value),
    **updates: any,
) -> None:
    for idx, item in enumerate(items):
        if all([
            getattr(item, prop_name, None) == prop_value
            for prop_name, prop_value in filters
        ]):
            for prop_name, prop_value in updates.items():
                setter(item, prop_name, prop_value)
            break
    else:
        raise NeuropixelsRigException("Failed to find matching item. filters: %s" % filters)
    