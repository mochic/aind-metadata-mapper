"""Tests parsing of session information from ephys rig."""

import json
import os
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from aind_data_schema.core.session import DomeModule, EphysProbeConfig
from aind_data_schema.models.coordinates import CcfCoords, Coordinates3d

from aind_metadata_mapper.ephys.session import (
    EphysEtl,
    OpenEphysModule,
    OpenEphysSession,
    OpenEphysStream,
    ParsedInformation,
    StageLogParsedInfo,
    StageLogProbeInfo,
    StageLogRow,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__))) / "resources" / "ephys"
)
EXAMPLE_STAGE_LOGS = [
    RESOURCES_DIR / "newscale_main.csv",
    RESOURCES_DIR / "newscale_surface_finding.csv",
]
EXAMPLE_OPENEPHYS_LOGS = [
    RESOURCES_DIR / "settings_main.xml",
    RESOURCES_DIR / "settings_surface_finding.xml",
]

EXPECTED_SESSION = RESOURCES_DIR / "ephys_session.json"


class TestOpenEphysSession(unittest.TestCase):
    """Test methods in OpenEphysSession class."""

    @classmethod
    def setUpClass(cls):
        """Load record object and user settings before running tests."""
        # TODO: Add visual stimulus

        # stick microscopes are the same in each stream of this example
        common_stick_microscopes = [
            DomeModule(
                assembly_name="20516338",
                arc_angle=Decimal("-180.0"),
                module_angle=Decimal("-180.0"),
                notes=(
                    "Did not record arc or module angles, did not " "calibrate"
                ),
            ),
            DomeModule(
                assembly_name="22437106",
                arc_angle=Decimal("-180.0"),
                module_angle=Decimal("-180.0"),
                notes=(
                    "Did not record arc or module angles, did not " "calibrate"
                ),
            ),
            DomeModule(
                assembly_name="22437107",
                arc_angle=Decimal("-180.0"),
                module_angle=Decimal("-180.0"),
                notes=(
                    "Did not record arc or module angles, did not " "calibrate"
                ),
            ),
            DomeModule(
                assembly_name="22438379",
                arc_angle=Decimal("-180.0"),
                module_angle=Decimal("-180.0"),
                notes=(
                    "Did not record arc or module angles, did not " "calibrate"
                ),
            ),
        ]
        common_ephys_modules = [
            OpenEphysModule(
                ephys_probes=[EphysProbeConfig(name="46121")],
                primary_targeted_structure="AntComMid",
                targeted_ccf_coordinates=[
                    CcfCoords(
                        ml=Decimal("5700.0"),
                        ap=Decimal("5160.0"),
                        dv=Decimal("5260.0"),
                    )
                ],
                assembly_name="46121",
                arc_angle=Decimal("5.3"),
                module_angle=Decimal("-27.1"),
                coordinate_transform="behavior/calibration_info_np2_2024_01_17T15_04_00.npy",
                calibration_date=datetime(
                    2024, 1, 17, 15, 4, 0, tzinfo=timezone.utc
                ),
                notes="Easy insertion. Recorded 8 minutes, serially, so separate from prior insertion.",
            ),
            OpenEphysModule(
                ephys_probes=[EphysProbeConfig(name="46118")],
                primary_targeted_structure="VISp",
                targeted_ccf_coordinates=[
                    CcfCoords(
                        ml=Decimal("5700.0"),
                        ap=Decimal("5160.0"),
                        dv=Decimal("5260.0"),
                    )
                ],
                assembly_name="46118",
                arc_angle=Decimal("14"),
                module_angle=Decimal("20"),
                coordinate_transform="behavior/calibration_info_np2_2024_01_17T15_04_00.npy",
                calibration_date=datetime(
                    2024, 1, 17, 15, 4, 0, tzinfo=timezone.utc
                ),
                notes="Easy insertion. Recorded 8 minutes, serially, so separate from prior insertion.",
            ),
        ]

        cls.specified_model = OpenEphysSession(
            experimenter_full_name=["Al Dente"],
            session_type="Receptive field mapping",
            iacuc_protocol="2109",
            rig_id="323_EPHYS2-RF_2024-01-18_01",
            subject_id="699889",
            data_streams=[
                OpenEphysStream(
                    daq_names=["Basestation"],
                    stick_microscopes=common_stick_microscopes,
                    ephys_modules=common_ephys_modules,
                    mouse_platform_name="Running Wheel",
                    active_mouse_platform=False,
                ),
                OpenEphysStream(
                    daq_names=["Basestation"],
                    stick_microscopes=common_stick_microscopes,
                    ephys_modules=common_ephys_modules,
                    mouse_platform_name="Running Wheel",
                    active_mouse_platform=False,
                ),
            ],
        )

        with open(EXPECTED_SESSION, "r") as f:
            expected_session_contents = json.load(f)

        cls.expected_session_contents = expected_session_contents

    def test_extract(self):
        """Tests that the stage and openophys logs and experiment
        data is extracted correctly"""

        expected_stage_log_row0 = StageLogRow(
            log_timestamp=datetime(2023, 4, 4, 10, 37, 28, 815000),
            probe_name="SN46121",
            coordinate1=Decimal("7520.0"),
            coordinate2=Decimal("7505.0"),
            coordinate3=Decimal("7493.0"),
            coordinate4=Decimal("7520.0"),
            coordinate5=Decimal("7505.0"),
            coordinate6=Decimal("7493.0"),
        )
        expected_stage_log_row1 = StageLogRow(
            log_timestamp=datetime(2023, 4, 6, 11, 47, 57, 558000),
            probe_name="SN46118",
            coordinate1=Decimal("7500.0"),
            coordinate2=Decimal("7500.0"),
            coordinate3=Decimal("7900.5"),
            coordinate4=Decimal("7500.0"),
            coordinate5=Decimal("7500.0"),
            coordinate6=Decimal("7900.5"),
        )
        expected_stage_log_row2 = StageLogRow(
            log_timestamp=datetime(2023, 4, 4, 12, 37, 28, 815000),
            probe_name="SN46121",
            coordinate1=Decimal("7520.0"),
            coordinate2=Decimal("7505.0"),
            coordinate3=Decimal("7493.0"),
            coordinate4=Decimal("7520.0"),
            coordinate5=Decimal("7505.0"),
            coordinate6=Decimal("7493.0"),
        )
        expected_stage_log_row3 = StageLogRow(
            log_timestamp=datetime(2023, 4, 6, 13, 47, 57, 558000),
            probe_name="SN46118",
            coordinate1=Decimal("7500.0"),
            coordinate2=Decimal("7500.0"),
            coordinate3=Decimal("7900.5"),
            coordinate4=Decimal("7500.0"),
            coordinate5=Decimal("7500.0"),
            coordinate6=Decimal("7900.5"),
        )

        etl_job1 = EphysEtl(
            output_directory=RESOURCES_DIR,
            specific_model=self.specified_model,
            input_sources=(
                {
                    "stage_logs": EXAMPLE_STAGE_LOGS,
                    "settings_xml": EXAMPLE_OPENEPHYS_LOGS,
                }
            ),
        )
        raw_info = etl_job1._extract()
        self.assertEqual("newscale_main.csv", raw_info.stage_logs[0].filename)
        self.assertEqual(
            expected_stage_log_row0, raw_info.stage_logs[0].contents[0]
        )
        self.assertEqual(
            expected_stage_log_row1, raw_info.stage_logs[0].contents[-1]
        )
        self.assertEqual(
            "newscale_surface_finding.csv", raw_info.stage_logs[1].filename
        )
        self.assertEqual(
            expected_stage_log_row2, raw_info.stage_logs[1].contents[0]
        )
        self.assertEqual(
            expected_stage_log_row3, raw_info.stage_logs[1].contents[-1]
        )

    def test_parse(self):
        """Tests that the raw logs get parsed to intermediate data models"""

        expected_parsed_info = ParsedInformation(
            parsed_stage_logs=[
                StageLogParsedInfo(
                    filename="newscale_main.csv",
                    stream_start_time=datetime(2023, 4, 4, 10, 37, 28, 815000),
                    stream_end_time=datetime(2023, 4, 6, 11, 47, 57, 558000),
                    probe_map={
                        "46121": StageLogProbeInfo(
                            probe_stream_start_time=datetime(
                                2023, 4, 4, 10, 37, 28, 815000
                            ),
                            probe_stream_end_time=datetime(
                                2023, 4, 4, 10, 45, 38, 580000
                            ),
                            manipulator_coordinates=Coordinates3d(
                                x=Decimal("7520.0"),
                                y=Decimal("7505.0"),
                                z=Decimal("7493.0"),
                            ),
                        ),
                        "46118": StageLogProbeInfo(
                            probe_stream_start_time=datetime(
                                2023, 4, 6, 11, 47, 55, 990000
                            ),
                            probe_stream_end_time=datetime(
                                2023, 4, 6, 11, 47, 57, 558000
                            ),
                            manipulator_coordinates=Coordinates3d(
                                x=Decimal("7500.0"),
                                y=Decimal("7499.5"),
                                z=Decimal("7600.0"),
                            ),
                        ),
                    },
                ),
                StageLogParsedInfo(
                    filename="newscale_surface_finding.csv",
                    stream_start_time=datetime(2023, 4, 4, 12, 37, 28, 815000),
                    stream_end_time=datetime(2023, 4, 6, 13, 47, 57, 558000),
                    probe_map={
                        "46121": StageLogProbeInfo(
                            probe_stream_start_time=datetime(
                                2023, 4, 4, 12, 37, 28, 815000
                            ),
                            probe_stream_end_time=datetime(
                                2023, 4, 4, 12, 45, 38, 580000
                            ),
                            manipulator_coordinates=Coordinates3d(
                                x=Decimal("7520.0"),
                                y=Decimal("7505.0"),
                                z=Decimal("7493.0"),
                            ),
                        ),
                        "46118": StageLogProbeInfo(
                            probe_stream_start_time=datetime(
                                2023, 4, 6, 13, 47, 55, 990000
                            ),
                            probe_stream_end_time=datetime(
                                2023, 4, 6, 13, 47, 57, 558000
                            ),
                            manipulator_coordinates=Coordinates3d(
                                x=Decimal("7500.0"),
                                y=Decimal("7499.5"),
                                z=Decimal("7600.0"),
                            ),
                        ),
                    },
                ),
            ],
            session_start_time=datetime(2023, 4, 4, 10, 37, 28),
        )

        etl_job1 = EphysEtl(
            output_directory=RESOURCES_DIR,
            specific_model=self.specified_model,
            input_sources=(
                {
                    "stage_logs": EXAMPLE_STAGE_LOGS,
                    "settings_xml": EXAMPLE_OPENEPHYS_LOGS,
                }
            ),
        )
        raw_info = etl_job1._extract()
        parsed_info = etl_job1._parse_stage_logs(raw_info=raw_info)
        self.assertEqual(expected_parsed_info, parsed_info)

    def test_transform(self):
        etl_job1 = EphysEtl(
            output_directory=RESOURCES_DIR,
            specific_model=self.specified_model,
            input_sources=(
                {
                    "stage_logs": EXAMPLE_STAGE_LOGS,
                    "settings_xml": EXAMPLE_OPENEPHYS_LOGS,
                }
            ),
        )
        raw_info = etl_job1._extract()
        actual_session = etl_job1._transform(raw_info)
        self.assertEqual(
            self.expected_session_contents,
            json.loads(actual_session.model_dump_json()),
        )


if __name__ == "__main__":
    unittest.main()
