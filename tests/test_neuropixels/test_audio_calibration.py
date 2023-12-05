import unittest
import pathlib
import datetime

from aind_metadata_mapper.neuropixels import audio_calibration

from . import get_current_rig


class TestAudioCalibration(unittest.TestCase):
    """Tests audio calibration utilities in for the neuropixels project."""

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/"
            "soundMeasure_NP2_20230817_150735_sound_level.txt"
        ).read_text()
        speaker_device_name = "speaker"
        extracted = audio_calibration.extract(
            content,
            speaker_device_name,
            datetime.datetime(year=2023, month=1, day=1)
        )
        
        current = get_current_rig()

        audio_calibration.transform(
            extracted,
            current,
        )

        for calibrations in current.calibrations:
            if calibrations.device_name == speaker_device_name:
                assert calibrations.input["measurements"][0] == \
                    (0.0, 54.73212135610404)
