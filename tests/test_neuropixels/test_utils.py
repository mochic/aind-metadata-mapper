import unittest
import datetime

from aind_metadata_mapper.neuropixels import utils  # type: ignore


class Utils(unittest.TestCase):

    def test_update_rig_id_no_room_id(self):
        assert utils.update_rig_id(
            "NP.2_240227",
            datetime.date(2024, 2, 28)) == "NP.2_240228"
    
    def test_update_rig_id_with_room_id(self):
        assert utils.update_rig_id(
            "333_NP.2_240227",
            datetime.date(2024, 2, 28)) == "333_NP.2_240228"
