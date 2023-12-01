import unittest

from aind_metadata_mapper.neuropixels import utils, NeuropixelsRigException


class TestUtils(unittest.TestCase):
    """Tests dxdiag utilities in for the neuropixels project."""

    items = [
        {"name": "wow", },
        {"name": "bur", },
        {"name": "kek", },
    ]

    def test_find_transform_replace_success(self):
        transformed_key_name = "face"
        transformed_key_value = "test"
        result = utils.find_transform_replace(
            TestUtils.items,
            lambda item: item["name"] == "bur",
            lambda item: {**item, transformed_key_name: transformed_key_value}
        )
        assert result[1].get(transformed_key_name) == transformed_key_value, \
            (
                "Result should have a transformed item and be in the same order"
                " as the input list."
            )

    def test_find_transform_replace_failure(self):
        with self.assertRaises(NeuropixelsRigException):
            utils.find_transform_replace(
                TestUtils.items,
                lambda item: item["name"] == "murgle",
                lambda item: {**item, "face": "test"},
            )
    
    def test_merge_models(self):
        pass