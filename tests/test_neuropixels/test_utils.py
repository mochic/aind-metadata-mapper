"""Tests for the neuropixels rig utils."""
import unittest
import pydantic

from aind_metadata_mapper.neuropixels import utils  # type: ignore


class Child(pydantic.BaseModel):

    """Test model to be nested in parent."""

    name: str
    value: str


class Parent(pydantic.BaseModel):

    """Test model to be parent of child."""

    children: list[Child]


class Utils(unittest.TestCase):

    """Tests for the neuropixels rig utils."""

    def test_find_replace_append(self):
        """Test find_replace_or_append with existing value."""
        untoggled_value = "untoggled"
        target_child_name = "child1"
        parent = Parent(
            children=[
                Child(name=name, value=untoggled_value)
                for name in [
                    "child0", target_child_name, "child2", "child3"]
            ]
        )

        utils.find_replace_or_append(
            parent.children,
            [("name", target_child_name)],
            Child(name=target_child_name, value="toggled"),
        )

        self.assertEqual(
            len(
                list(
                    filter(
                        lambda child: child.value != untoggled_value,
                        parent.children,
                    )
                )
            ),
            1,
        )
