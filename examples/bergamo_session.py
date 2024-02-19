"""Example of how to use the bergamo session module"""
from datetime import datetime
from pathlib import Path

from aind_metadata_mapper.bergamo.session import (
    BergamoEtl,
    BergamoSession,
    BergamoStimulusEpoch,
    BergamoStream,
    RawImageInfo,
)

# Create a BergamoSession. The BergamoSession inherits all the fields
# from aind_data_schema.core.session.Session class, but marks a few required
# fields as Optional. Those fields will be set by parsing files.

example_bergamo_session = BergamoSession(
            experimenter_full_name=["John Smith"],
            subject_id="12345",
            session_start_time=datetime(2020, 10, 10, 12, 5, 00),
            session_end_time=datetime(2020, 10, 10, 13, 5, 00),
            data_streams=[
                BergamoStream(
                    mouse_platform_name="Platform A",
                    active_mouse_platform=False,
                    stream_start_time=datetime(2020, 10, 10, 12, 6, 00),
                    stream_end_time=datetime(2020, 10, 10, 13, 4, 00),
                )
            ],
            stimulus_epochs=[
                BergamoStimulusEpoch(
                    stimulus_start_time=datetime(2020, 10, 10, 12, 7, 00),
                    stimulus_end_time=datetime(2020, 10, 10, 13, 1, 00),
                )
            ],
        )

etl_job = BergamoEtl(
    input_source=Path("/directory/of/tiff/files/"),
    output_directory=Path("/location/to/save/to/"),
    specific_model=example_bergamo_session,
)

# To crawl through the tiff directory and parse the headers, simply run:

etl_job.run_job()

# Below is not normally necessary, but shows how to parse ScanImage header
# strings manually.

raw_image_info = RawImageInfo(
    # Truncated metadata for readability
    metadata=(
        "I.PREMIUM = true\n"
        "SI.TIFF_FORMAT_VERSION = 4\n"
        "SI.VERSION_COMMIT = '6538675fb9c3276754f7078940dcc5cc2b9688b5'\n"
        "SI.VERSION_MAJOR = 2022\n"
        "SI.VERSION_MINOR = 1\n"
        "SI.VERSION_UPDATE = 0\n"
        "SI.acqState = 'loop'\n"
        "SI.acqsPerLoop = 10000"
    ),
    description0=(
        "frameNumbers = 1\n"
        "acquisitionNumbers = 1\n"
        "frameNumberAcquisition = 1\n"
        "frameTimestamps_sec = 0.000000000\n"
        "acqTriggerTimestamps_sec = -0.000021560\n"
        "nextFileMarkerTimestamps_sec = -1.000000000\n"
        "endOfAcquisition = 0\n"
        "endOfAcquisitionMode = 0\n"
        "dcOverVoltage = 0\n"
        "epoch = [2023  7 24 14 14 17.854]\n"
        "auxTrigger0 = []\n"
        "auxTrigger1 = []\n"
        "auxTrigger2 = []\n"
        "auxTrigger3 = []\n"
        "I2CData = {}"
    ),
    shape=[347, 512, 512],
)

# Transform the raw image info and user settings into a Session model
session = etl_job._transform(raw_image_info)

# Write the session json file to the output directory
etl_job._load(session)
