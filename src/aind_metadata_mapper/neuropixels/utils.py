"""Shared utilities"""
import logging
import typing
import pathlib
import datetime
import configparser
import h5py  # type: ignore
from xml.etree import ElementTree


logger = logging.getLogger(__name__)


def find_elements(et: ElementTree.Element, name: str) -> \
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
    

def load_hdf5(h5_path: pathlib.Path) -> h5py.File:
    return h5py.File(h5_path, "r")


def extract_hdf5_value(h5_file: h5py.File, path: list[str]) -> \
        typing.Union[typing.Any, None]:
    try:
        value = None
        for part in path:
            value = h5_file[part]
    except KeyError:
        logger.warning(f"Key not found: {part}")
        return None
        
    if isinstance(value, h5py.Dataset):
        return value[()]
    else:
        return value


def find_update(
    items: list[typing.Any],
    filters: list[typing.Tuple[str, typing.Any]],  # property name, property value
    setter = lambda item, name, value: setattr(item, name, value),
    **updates: typing.Any,
) -> typing.Union[typing.Any, None]:
    for item in items:
        if all([
            getattr(item, prop_name, None) == prop_value
            for prop_name, prop_value in filters
        ]):
            for prop_name, prop_value in updates.items():
                setter(item, prop_name, prop_value)
            return item
    else:
        logger.debug("Failed to find matching item. filters: %s" % filters)
        return None


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
