"""Tests parsing of session information from fib rig."""

import json
import os
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from aind_data_schema.core.session import (
    DetectorConfig,
    FiberConnectionConfig,
    LightEmittingDiodeConfig,
    TriggerType,
)

from aind_metadata_mapper.fib.session import FIBEtl, FibSession, FibStream

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__))) / "resources" / "fib"
)
EXAMPLE_MD_PATH = RESOURCES_DIR / "example_from_teensy.txt"
EXPECTED_SESSION = RESOURCES_DIR / "000000_ophys_session.json"


class TestSchemaWriter(unittest.TestCase):
    """Test methods in SchemaWriter class."""

    @classmethod
    def setUpClass(cls):
        """Load record object and user settings before running tests."""

        cls.example_input_session = FibSession(
            session_start_time=datetime(1999, 10, 4),
            experimenter_full_name=["john doe"],
            session_type="Foraging_Photometry",
            iacuc_protocol="2115",
            rig_id="ophys_rig",
            subject_id="000000",
            data_streams=[
                FibStream(
                    mouse_platform_name="Disc",
                    active_mouse_platform=False,
                    light_sources=[
                        LightEmittingDiodeConfig(
                            name="470nm LED", excitation_power=Decimal("0.020")
                        ),
                        LightEmittingDiodeConfig(
                            name="415nm LED", excitation_power=Decimal("0.020")
                        ),
                        LightEmittingDiodeConfig(
                            name="565nm LED", excitation_power=Decimal("0.020")
                        ),
                    ],
                    detectors=[
                        DetectorConfig(
                            name="Hamamatsu Camera",
                            exposure_time=Decimal("10"),
                            trigger_type=TriggerType.INTERNAL,
                        )
                    ],
                    fiber_connections=[
                        FiberConnectionConfig(
                            patch_cord_name="Patch Cord A",
                            patch_cord_output_power=Decimal("40"),
                            fiber_name="Fiber A",
                        )
                    ],
                )
            ],
            notes="brabrabrabra....",
        )

        with open(EXAMPLE_MD_PATH, "r") as f:
            raw_md_contents = f.read()
        with open(EXPECTED_SESSION, "r") as f:
            expected_session_contents = json.load(f)

        cls.expected_session_contents = expected_session_contents
        cls.example_metadata = raw_md_contents

    def test_extract(self):
        """Tests that the teensy response and experiment
        data is extracted correctly"""

        etl_job1 = FIBEtl(
            output_directory=RESOURCES_DIR,
            teensy_str=self.example_metadata,
            specific_model=self.example_input_session,
        )
        self.assertEqual(
            self.example_metadata, etl_job1.input_sources["teensy_str"]
        )

    def test_transform(self):
        """Tests that the teensy response maps correctly to ophys session."""

        etl_job1 = FIBEtl(
            output_directory=RESOURCES_DIR,
            teensy_str=self.example_metadata,
            specific_model=self.example_input_session,
        )
        actual_session = etl_job1._transform()
        self.assertEqual(
            self.expected_session_contents,
            json.loads(actual_session.model_dump_json()),
        )


if __name__ == "__main__":
    unittest.main()
