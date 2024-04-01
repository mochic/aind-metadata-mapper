"""Shared utilities"""
import logging
import typing
import pathlib
import datetime
import configparser
import h5py  # type: ignore
import yaml  # type: ignore
from xml.etree import ElementTree


logger = logging.getLogger(__name__)


def find_elements(et: ElementTree.Element, name: str) -> \
    typing.Generator[ElementTree.Element, None, None]:
    """Find elements in an ElementTree.Element that match a name.
    
    Notes
    -----
    - Name matches on tags are case insensitive match on tags for
     convenience
    """
    for element in et.iter():
        if element.tag.lower() == name.lower():
            yield element


def load_xml(xml_path: pathlib.Path) -> ElementTree.Element:
    """Load xml file from path."""
    return ElementTree.fromstring(xml_path.read_text())


def load_config(config_path: pathlib.Path) -> configparser.ConfigParser:
    """Load .ini file from path."""
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def load_yaml(yaml_path: pathlib.Path) -> dict:
    """Load yaml file from path."""
    return yaml.safe_load(yaml_path.read_text())


def load_hdf5(h5_path: pathlib.Path) -> h5py.File:
    """Load hdf5 file from path."""
    return h5py.File(h5_path, "r")


def extract_hdf5_value(h5_file: h5py.File, path: list[str]) -> \
        typing.Union[typing.Any, None]:
    """Extract value from hdf5 file using a path. Path is a list of property 
    names that are used to traverse the hdf5 file. A path of length greater 
    than 1 is expected to point to a nested property.
    """
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
    """Find an item in a list of items that matches the filters and update it. 
    Only the first item that matches the filters is updated.
    """
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
    """Find an item in a list of items that matches the filters and replace it. 
    If no item is found, append.
    """
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
    """Updates a rig id with a modification date. Rig id is expected to a 
    string of the of the format:
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
