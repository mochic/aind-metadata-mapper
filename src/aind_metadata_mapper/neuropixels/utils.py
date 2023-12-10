"""Shared utilities"""
import typing
import copy
import pydantic
import pathlib
import configparser
from xml.etree import ElementTree
from aind_data_schema import device, rig, base

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


def find_transform_replace(
    items: list[any],
    filter_function: typing.Callable,
    transform: typing.Callable
):
    items = copy.deepcopy(items)  # to avoid mutating input list
    indices = [
        idx
        for idx, item in enumerate(items)
        if filter_function(item)
    ]
    if len(indices) < 1:
        raise NeuropixelsRigException(
            "Found multiple matches for filter function."
        )
    
    target = items.pop(indices[0])
    items.insert(
        indices[0],
        transform(target),
    )

    return items


# def merge_models(
#         model_target: dict,
#         model_update: dict,
#         merge_path: list[str],
# ):
#     head
#     for key in merge_path:


class AllOptionalMeta(pydantic.main.ModelMetaclass):
    
    def __new__(cls, name, bases, namespaces, required_fields=[], **kwargs):
        annotations = namespaces.get('__annotations__', {})
        print(required_fields)
        for base in bases:
            annotations.update(getattr(base, '__annotations__', {}))
        for field, field_type in annotations.items():
            if not field.startswith('__'):  # ignore special methods
                # if it is an Optional field and one of it's defaults is
                #  NoneType
                if field in required_fields \
                    and typing.get_origin(field_type) == typing.Union and \
                    type(None) in field_type.__args__:
                    print("Required field")
                    print(field)
                    # If the field is Optional, remove None to make it required
                    non_none_types = [t for t in field_type.__args__ if t != type(None)]
                    annotations[field] = typing.Union[tuple(non_none_types)]
                else:
                    # Otherwise, make it optional
                    annotations[field] = typing.Optional[field_type]

        namespaces['__annotations__'] = annotations
        return super().__new__(cls, name, bases, namespaces, **kwargs)
    

# def merge_devices(device_a: device.Device, device_b: device.Device) -> \
#     device.Device:
#     updates = {}
#     all_annotations = {}
#     for c in device_a.__class__.mro():
#         if hasattr(c, '__annotations__'):
#             all_annotations.update(c.__annotations__)
#     for prop_name in all_annotations.keys():
#         value = getattr(device_b, prop_name)
#         if value is not None:
#             updates[prop_name] = value
#     return device_a.copy(update=updates)


def merge_devices(device_a: base.AindModel, device_b: device.Device) -> \
    None:
    """
    ---
    - Mutates device_a in-place
    """
    # updates = {}
    all_annotations = {}
    # get annotations for all classes in hierarchy
    for c in device_a.__class__.mro():
        if hasattr(c, '__annotations__'):
            all_annotations.update(c.__annotations__)
    
    for prop_name in all_annotations.keys():
        value = getattr(device_b, prop_name)
        if value is not None:
            setattr(device_a, prop_name, value)


def merge_models(device_a: device.Device, device_b: device.Device) -> \
    None:
    """
    ---
    - Mutates device_a in-place
    """
    # updates = {}
    all_annotations = {}
    # get annotations for all classes in hierarchy
    for c in device_a.__class__.mro():
        if hasattr(c, '__annotations__'):
            all_annotations.update(c.__annotations__)
    
    for prop_name in all_annotations.keys():
        value = getattr(device_b, prop_name)
        if value is not None:
            setattr(device_a, prop_name, value)


def recurse_aind_model(model: base.AindModel) -> None:
    for field_name, field_value in model.__fields__.items():
        if isinstance(field_value, base.AindModel):
            return (field_name, recurse_aind_model(field_value), )
        elif isinstance(field_value, list):
            return (field_name, list(map(
                recurse_aind_model,
                field_value,
            ), ))
        else:
            return (field_name, field_value, )


def update_rig(*updates: base.AindModel, rig: rig.Rig) -> None:
    updated = {}
    for update in updates:
        for device_name, device in update.devices.items():
            if device_name not in rig.devices:
                raise NeuropixelsRigException(
                    f"Device {device_name} not found in rig."
                )
            merge_devices(rig.devices[device_name], device)


def update_rig(
        *resources: pathlib.Path,
        rig_resource: pathlib.Path,
        output_dir: pathlib.Path,
        transformer: typing.Callable,

    ):
    output_path = output_dir / "rig.json"
    return 
    current = rig.Rig.parse_file(rig_resource)


def find_matching_objects(data: typing.Mapping, property_name: str, property_value: str) -> typing.Iterable:
    matching_objects = []

    def search(obj):
        if isinstance(obj, typing.Mapping):  # Check if it's a dictionary
            if property_name in obj and obj[property_name] == property_value:
                matching_objects.append(obj)

            for value in obj.values():
                search(value)
        elif isinstance(obj, typing.Iterable) and not isinstance(obj, (str, bytes)):
            for item in obj:
                search(item)

    search(data)
    if len(matching_objects) > 1:
        raise ValueError(f"Found multiple matches for {property_name}={property_value}")

    yield from matching_objects


def update_nested_model(
        model: pydantic.BaseModel,
        partial_model: pydantic.BaseModel,
        prop_map: dict,
):
    if isinstance(model, pydantic.BaseModel):
        updated_fields = {}
        for field, value in model.dict().items():
            if isinstance(value, pydantic.BaseModel):
                updated_fields[field] = update_nested_model(
                    value,
                    partial_model,
                )
            elif isinstance(value, list):
                updated_fields[field] = update_nested_model(
                    value,
                    partial_model,
                )
            else:
                updated_fields[field] = updated_values.get(field, value)
        return model.__class__(**updated_fields)
    else:
        return model


def load_config(config_path: pathlib.Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read_file(config_path)
    return config


def find_update(
    items: typing.Iterable[dict],
    filters: typing.Iterable[typing.Tuple[str, any]],  # property name, property value
    *updates: any,
) -> None:
    for idx, item in enumerate(items):
        if all([
            item.get(prop_name, None) == prop_value
            for prop_name, prop_value in filters
        ]):
            items[idx] = {
                **item,
                **updates,
            }
            break
    else:
        raise NeuropixelsRigException("Failed to find matching item.")
