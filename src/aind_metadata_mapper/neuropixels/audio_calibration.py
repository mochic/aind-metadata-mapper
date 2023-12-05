from aind_data_schema import device, rig

"""Volume level as a percent, measured sound pressure level in decibels
"""

def extract(content: str, ) -> device.Calibration:
    pass


def transform(calibration: device.Calibration, current: rig.Rig) -> None:
    current.calibrations = [
        calibration if current_calibration.device_name == \
            calibration.device_name
        else current_calibration
        for current_calibration in current.calibrations
    ]