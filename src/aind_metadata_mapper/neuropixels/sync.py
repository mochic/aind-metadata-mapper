from . import NeuropixelsRigException


def transform(
    config: dict,
    current: dict,
    sync_name: str,
    sync_hostname: str = None,
) -> None:
    for daq in current["daqs"]:
        if daq["name"] == sync_name:
            if sync_hostname:
                daq["computer_name"] = sync_hostname

            daq["channels"] = [
                {
                    "channel_name": name,
                    "channel_type": "Digital Input",
                    "device_name": sync_name,
                    "event_based_sampling": False,
                    "channel_index": line,
                    "sample_rate": config["freq"],
                    "sample_rate_unit": "hertz"
                }
                for line, name in config["line_labels"].items()
            ]
            break
    else:
        raise NeuropixelsRigException(
            "Sync daq not found on current rig. name=%s" % sync_name
        )
