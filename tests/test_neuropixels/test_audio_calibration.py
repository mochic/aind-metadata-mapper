import unittest
import pathlib

from aind_data_schema import rig

from aind_metadata_mapper.neuropixels import audio_calibration

from . import get_current_rig


class TestAudioCalibration(unittest.TestCase):
    """Tests audio calibration utilities in for the neuropixels project."""

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/"
            "soundMeasure_NP2_20230817_150735_sound_level.txt"
        ).read_text()
        extracted = audio_calibration.extract(content)
        
        current = get_current_rig()

        audio_calibration.transform(
            extracted,
            current,
        )
        
        # for device in current.stimulus_devices:
        #     if device.device_type == "Monitor":
        #         assert device.width == 1920 \
        #             and device.height == 1200 and \
        #                 device.model == "PA248"