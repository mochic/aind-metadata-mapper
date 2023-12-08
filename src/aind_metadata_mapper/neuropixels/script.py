import json
import typing
import pathlib
from aind_data_schema import rig




def init(
        path: pathlib.Path = pathlib.Path("rig.json"),
        input_dir: pathlib.Path = pathlib.Path("./"),
        rig_id: str = None,
) -> rig.Rig:
    if not path.exists():
        if not rig_id:
            raise ValueError("rig_id must be provided if rig.json does not exist")
        
        template_path = pathlib.Path("rig.template.json")
        with open(template_path, "r") as f:
            template = json.load(f)
        template["rig_id"] = rig_id
        current = rig.Rig.from_object(template)
    else:
        current = rig.Rig.from_json(path)

    sync_settings = input_dir / "sync_settings.json"
    if sync_settings.exists():
        with open(sync_settings, "r") as f:
            sync_settings = json.load(f)
        current.sync_settings = rig.SyncSettings.from_object(sync_settings)