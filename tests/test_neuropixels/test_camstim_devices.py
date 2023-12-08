import unittest
import pathlib

from aind_data_schema import rig

from aind_metadata_mapper.neuropixels import camstim_devices, utils, rig as neuropixels_rig

from . import get_current_rig


class TestCamstimDevices(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""
    
    # overloads = {
    #     "viewing_distance": 10.0,
    #     "viewing_distance_unit": "centimeter",
    #     "manufacturer": "ASUS",
    #     "contrast": 0,
    #     "brightness": 0,
    #     "refresh_rate": 60,
    #     "serial_number": "faux-serial-number",
    # }

    def test_extract_transform(self):
        content = pathlib.Path(
            "./tests/resources/neuropixels/camstim/camstim.yml"
        ).read_text()
        extracted = camstim_devices.extract(content)
        print(extracted)
        current = get_current_rig()

        neuropixels_rig.update_rig(
            *extracted,
            current,
        )
        
        # for device in current.stimulus_devices:
        #     if device.device_type == "Monitor":
        #         assert device.width == 1920 \
        #             and device.height == 1200 and \
        #                 device.model == "PA248"