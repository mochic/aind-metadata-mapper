"""Shared utilities"""

import logging
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Generator, List, Tuple, Union
from xml.etree import ElementTree

import yaml
from h5py import Dataset, File

logger = logging.getLogger(__name__)


def find_elements(
    et: ElementTree.Element, name: str
) -> Generator[ElementTree.Element, None, None]:
    """Find elements in an ElementTree.Element that match a name.

    Notes
    -----
    - Name matches on tags are case-insensitive match on tags for
     convenience
    """
    for element in et.iter():
        if element.tag.lower() == name.lower():
            yield element


def load_xml(xml_path: Path) -> ElementTree.Element:
    """Load xml file from path."""
    return ElementTree.fromstring(xml_path.read_text())


def load_config(config_path: Path) -> ConfigParser:
    """Load .ini file from path."""
    config = ConfigParser()
    config.read(config_path)
    return config


def load_yaml(yaml_path: Path) -> dict:
    """Load yaml file from path."""
    return yaml.safe_load(yaml_path.read_text())


def load_hdf5(h5_path: Path) -> File:
    """Load hdf5 file from path."""
    return File(h5_path, "r")


def extract_hdf5_value(h5_file: File, path: List[str]) -> Union[Any, None]:
    """Extract value from hdf5 file using a path. Path is a list of property
    names that are used to traverse the hdf5 file. A path of length greater
    than 1 is expected to point to a nested property.
    """
    try:
        value = None
        for part in path:
            value = h5_file[part]
    except KeyError as e:
        logger.warning(f"Key not found: {e}")
        return None

    if isinstance(value, Dataset):
        return value[()]
    else:
        return value


def find_update(
    items: List[Any],
    filters: List[Tuple[str, Any]],
    setter=lambda item, name, value: setattr(item, name, value),
    **updates: Any,
) -> Union[Any, None]:
    """Find an item in a list of items that matches the filters and update it.
     Only the first item that matches the filters is updated.

    Notes
    -----
    - Filters are property name, property value pairs.
    """
    for item in items:
        if all(
            [
                getattr(item, prop_name, None) == prop_value
                for prop_name, prop_value in filters
            ]
        ):
            for prop_name, prop_value in updates.items():
                setter(item, prop_name, prop_value)
            return item
    else:
        logger.debug("Failed to find matching item. filters: %s" % filters)
        return None


def find_replace_or_append(
    iterable: List[Any],
    filters: List[Tuple[str, Any]],
    update: Any,
):
    """Find an item in a list of items that matches the filters and replace it.
    If no item is found, append.
    """
    for idx, obj in enumerate(iterable):
        if all(
            [
                getattr(obj, prop_name, None) == prop_value
                for prop_name, prop_value in filters
            ]
        ):
            iterable[idx] = update
            break
    else:
        iterable.append(update)
