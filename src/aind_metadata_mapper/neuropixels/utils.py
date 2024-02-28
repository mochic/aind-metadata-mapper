"""Shared utilities"""
import logging
import typing
import pathlib
import datetime
import configparser
from xml.etree import ElementTree

from . import NeuropixelsRigException


logger = logging.getLogger(__name__)


def find_elements(et: ElementTree.ElementTree, name: str) -> \
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


def load_xml(xml_path: pathlib.Path) -> ElementTree.Element:
    return ElementTree.fromstring(xml_path.read_text())


def load_config(config_path: pathlib.Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(config_path)
    return config
    

def find_update(
    items: list[typing.Any],
    filters: list[typing.Tuple[str, typing.Any]],  # property name, property value
    setter = lambda item, name, value: setattr(item, name, value),
    **updates: typing.Any,
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


def find_replace_or_append(
    iterable: list[typing.Any],
    filters: list[typing.Tuple[str, typing.Any]],
    update: typing.Any):
    for idx, obj in enumerate(iterable):
        if all([
            getattr(obj, prop_name, None) == prop_value 
            for prop_name, prop_value in filters
        ]):
            iterable[idx] = update
            break
    else:
        iterable.append(update)


def update_rig_id(
    rig_id: str,
    modification_date: datetime.date,
) -> str:
    """Rig id is expected to a string of the of the format:
        <ROOM ID>_<RIG ID>_<MODIFICATION DATE (YYMMDD)>
    
    Notes
    -----
    - This function supports rig_id that are not postfixed with a room id
    """
    parts = rig_id.split("_")
    logger.debug("Parsed rig_id parts: %s" % parts)
    return "_".join([
        *parts[:-1],
        modification_date.strftime("%y%m%d"),
    ])
    
