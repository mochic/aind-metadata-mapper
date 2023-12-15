import datetime
# from aind_data_schema import device, rig

from . import NeuropixelsRigException

"""Volume level as a percent, measured sound pressure level in decibels
"""


def transform(content: str, current: dict, device_name: str) -> None:
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
    for _ in range(len(lines)):
        value = lines.pop(0)
        if value == "":
            break
        parsed = value.strip().split("\t")
        measurements.append(
            (
                float(parsed[0]),
                float(parsed[1]),
            )
        )
    
    curve = lines.pop(0).split("Fit params: ")[1]
    curve_parameters = []
    for parameter_name in ("a", "b", "c"):
        curve_parameters.append({
            "name": parameter_name,
            "value": float(lines.pop(0)),
        })
    # replace it if it exists
    current.calibrations = [
        calibration if current_calibration.device_name == \
            calibration.device_name
        else current_calibration
        for current_calibration in current.calibrations
    ]

    # append if not already present
    filtered = list(filter(
        lambda current_calibration: current_calibration.device_name == \
            calibration.device_name,
        current.calibrations,
    ))

    if len(filtered) < 1:
         current.calibrations.append(calibration)