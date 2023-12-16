import datetime

from . import NeuropixelsRigException

"""Volume level as a percent, measured sound pressure level in decibels
"""


def transform(
        content: str,
        calibration_date: datetime.date,
        device_name: str,
        current: dict,
) -> None:
    lines = content.split("\n")
    measurements_header = lines.pop(0)
    expected_measurements_header = "Volume	SPL (dB)"
    if measurements_header != expected_measurements_header:
        raise NeuropixelsRigException(
            "Invalid measurements header: %s. Expected: %s"
            % (
                measurements_header,
                expected_measurements_header,
            )
        )

    measurements = []
    for idx, line in enumerate(lines):
        if line == "":
            break

        parsed = line.strip().split("\t")
        measurements.append(
            (
                float(parsed[0]),
                float(parsed[1]),
            )
        )
    curve = lines[idx + 1].split("Fit params: ")[1]
    curve_parameters = []
    for param_idx, parameter_name in enumerate(["a", "b", "c"]):
        curve_parameters.append({
            "name": parameter_name,
            "value": float(lines[idx + param_idx + 2]),
        })

    audio_calibration = {
        "device_name": device_name,
        "calibration_date": calibration_date,
        "input": {
            "raw": content,
            "measurements": measurements,
        },
        "output": {
            "curve": curve,
            "parameters": curve_parameters,
        },
        "description": (
            "Volume calibration. Standardizes sound "
            "pressure to system sound level."
        ),
    }

    for calibration in current["calibrations"]:
        if calibration["device_name"] == device_name:
            calibration.update(audio_calibration)
            break
    else:
        current["calibrations"].append(audio_calibration)