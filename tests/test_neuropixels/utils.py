"""Utilities for neuropixels etl tests."""
import datetime
import pathlib
import shutil
import typing
import tempfile

from aind_data_schema.core import rig  # type: ignore
from aind_data_schema.models import (  # type: ignore
    coordinates, devices, organizations)


COPA_NOTES = (
    "The rotation matrix is represented as: a,b,c,d,e,f,g,h,i. Wherein a, b, "
    "c correspond to the first row of the matrix. The translation matrix is "
    "represented as: x,y,z."
)

FORWARD_CAMERA_ASSEMBLY_NAME = "Forward"
FORWARD_CAMERA_NAME = f"{FORWARD_CAMERA_ASSEMBLY_NAME} camera"
EYE_CAMERA_ASSEMBLY_NAME = "Eye"
EYE_CAMERA_NAME = f"{EYE_CAMERA_ASSEMBLY_NAME} camera"
SIDE_CAMERA_ASSEMBLY_NAME = "Side"
SIDE_CAMERA_NAME = f"{SIDE_CAMERA_ASSEMBLY_NAME} camera"


def init_rig() -> rig.Rig:
    """Initializes a rig model for the dynamic routing project.

    Notes
    -----
    - embedded as code to avoid mismatched aind-data-schema versions
    """
    computer_name = "127.0.0.1"
    shared_camera_props = {
        "detector_type": "Camera",
        "model": "G-032",
        "max_frame_rate": 102,
        "sensor_width": 7400,
        "sensor_height": 7400,
        "size_unit": devices.SizeUnit.NM,
        "notes": "Max frame rate is at maximum resolution.",
        "cooling": devices.Cooling.NONE,
        "computer_name": computer_name,
    }

    shared_camera_assembly_relative_position_props = {
        "device_origin": (
            "Located on face of the lens mounting surface in its center"
        ),
        "device_axes": [
            coordinates.Axis(
                name=coordinates.AxisName.X,
                direction=(
                    "Oriented so that it is parallel to the bottom edge of "
                    "the sensor."
                ),
            ),
            coordinates.Axis(
                name=coordinates.AxisName.Y,
                direction=(
                    "Pointing to the bottom edge of the sensor."
                ),
            ),
            coordinates.Axis(
                name=coordinates.AxisName.Z,
                direction=(
                    "Positive moving away from the sensor towards the object."
                )
            )
        ],
        "notes": COPA_NOTES,
    }

    model = rig.Rig(
        rig_id="327_NP2_240401",
        modification_date=datetime.date(2024, 4, 1),
        modalities=[
            rig.Modality.BEHAVIOR_VIDEOS,
            rig.Modality.BEHAVIOR,
            rig.Modality.ECEPHYS,
        ],
        mouse_platform=devices.Disc(
            name="Mouse Platform",
            radius="4.69",
            radius_unit="centimeter",
            notes=(
                "Radius is the distance from the center of the wheel to the "
                "mouse."
            ),
        ),
        stimulus_devices=[
            devices.Monitor(
                name="Stim",
                model="PA248",
                manufacturer=organizations.Organization.ASUS,
                width=1920,
                height=1200,
                size_unit="pixel",
                viewing_distance=15.3,
                viewing_distance_unit="centimeter",
                refresh_rate=60,
                brightness=43,
                contrast=50,
                position=coordinates.RelativePosition(
                    device_position_transformations=[
                        coordinates.Rotation3dTransform(
                            rotation=[
                                -0.80914, -0.58761, 0,
                                -0.12391, 0.17063, 0.97751,
                                0.08751, -0.12079, 0.02298,
                            ],
                        ),
                        coordinates.Translation3dTransform(
                            translation=[0.08751, -0.12079, 0.02298]
                        ),
                    ],
                    device_origin=(
                        "Located at the center of the screen. Right and left "
                        "conventions are relative to the screen side of "
                        "the monitor."
                    ),
                    device_axes=[
                        coordinates.Axis(
                            name=coordinates.AxisName.X,
                            direction=(
                                "Oriented so that it is parallel to the long "
                                "edge of the screen. Positive pointing right."
                            ),
                        ),
                        coordinates.Axis(
                            name=coordinates.AxisName.Y,
                            direction=(
                                "Positive pointing to the top of the screen."
                            ),
                        ),
                        coordinates.Axis(
                            name=coordinates.AxisName.Z,
                            direction=(
                                "Positive moving away from the screen."
                            )
                        )
                    ],
                    notes=COPA_NOTES,
                )
            ),
            devices.Speaker(
                name="Speaker",
                manufacturer=organizations.Organization.ISL,
                model="SPK-I-81345",
                position=coordinates.RelativePosition(
                    device_position_transformations=[
                        coordinates.Rotation3dTransform(
                            rotation=[
                                -0.82783, -0.4837, -0.28412,
                                -0.55894, 0.75426, 0.34449,
                                0.04767, 0.44399, -0.89476
                            ],
                        ),
                        coordinates.Translation3dTransform(
                            translation=[-0.00838, -0.09787, 0.18228]
                        ),
                    ],
                    device_origin=(
                        "Located on front mounting flange face. Right and left"
                        " conventions are relative to the front side of the "
                        "speaker."
                    ),
                    device_axes=[
                        coordinates.Axis(
                            name=coordinates.AxisName.X,
                            direction=(
                                "Oriented so it will intersect the center of "
                                "a bolt hole on the mounting flange."
                            ),
                        ),
                        coordinates.Axis(
                            name=coordinates.AxisName.Y,
                            direction=(
                                "Positive pointing to the top of the speaker."
                            ),
                        ),
                        coordinates.Axis(
                            name=coordinates.AxisName.Z,
                            direction=(
                                "Positive moving away from the speaker."
                            )
                        )
                    ],
                    notes=COPA_NOTES + (
                        " Speaker to be mounted with the X axis pointing to "
                        "the right when viewing the speaker along the Z axis"),
                )
            ),
            devices.RewardDelivery(
                reward_spouts=[
                    devices.RewardSpout(
                        name="Reward Spout",
                        manufacturer=organizations.Organization.HAMILTON,
                        model="8649-01 Custom",
                        spout_diameter=0.672,
                        spout_diameter_unit="millimeter",
                        side=devices.SpoutSide.CENTER,
                        solenoid_valve=devices.Device(
                            name="Solenoid Valve",
                            device_type="Solenoid Valve",
                            manufacturer=organizations.Organization.NRESEARCH,
                            model="161K011",
                            notes="Model number is product number.",
                        ),
                        lick_sensor=devices.Device(
                            name="Lick Sensor",
                            device_type="Lick Sensor",
                            manufacturer=organizations.Organization.OTHER,
                        ),
                        lick_sensor_type=devices.LickSensorType.PIEZOELECTIC,
                        notes=(
                            "Spout diameter is for inner diameter. "
                            "Outer diameter is 1.575mm. "
                        ),
                    ),
                ]
            ),
        ],
        ephys_assemblies=[
            rig.EphysAssembly(
                name=f"Ephys Assembly {assembly_letter}",
                manipulator=devices.Manipulator(
                    name=f"Ephys Assembly {assembly_letter} Manipulator",
                    manufacturer=(
                        organizations.Organization.NEW_SCALE_TECHNOLOGIES),
                    model="06591-M-0004",
                ),
                probes=[
                    devices.EphysProbe(
                        name=f"Probe{assembly_letter}",
                        probe_model="Neuropixels 1.0",
                        manufacturer=organizations.Organization.IMEC,
                    )
                ]
            )
            for assembly_letter in ["A", "B", "C", "D", "E", "F"]
        ],
        light_sources=[
            devices.LightEmittingDiode(
                manufacturer=organizations.Organization.OTHER,
                name="Face forward LED",
                model="LZ4-40R308-0000",
                wavelength=740,
                wavelength_unit=devices.SizeUnit.NM,
            ),
            devices.LightEmittingDiode(
                manufacturer=organizations.Organization.OTHER,
                name="Body LED",
                model="LZ4-40R308-0000",
                wavelength=740,
                wavelength_unit=devices.SizeUnit.NM,
            ),
            devices.LightEmittingDiode(
                manufacturer=organizations.Organization.OSRAM,
                name="Eye LED",
                model="LZ4-40R608-0000",
                wavelength=850,
                wavelength_unit=devices.SizeUnit.NM,
            ),
            devices.Laser(
                name="Laser #0",
                manufacturer=organizations.Organization.VORTRAN,
                wavelength=488.0,
                model="Stradus 488-50",
                wavelength_unit="nanometer",
            ),
            devices.Laser(
                name="Laser #1",
                manufacturer=organizations.Organization.VORTRAN,
                wavelength=633.0,
                model="Stradus 633-80",
                wavelength_unit="nanometer",
            ),
        ],
        cameras=[
            devices.CameraAssembly(
                name=FORWARD_CAMERA_ASSEMBLY_NAME,
                camera_target="Face forward",
                camera=devices.Camera(
                    name=FORWARD_CAMERA_NAME,
                    manufacturer=organizations.Organization.ALLIED,
                    chroma="Monochrome",
                    data_interface="Ethernet",
                    **shared_camera_props,
                ),
                filter=devices.Filter(
                    name="Forward filter",
                    manufacturer=organizations.Organization.SEMROCK,
                    model="FF01-715_LP-25",
                    filter_type=devices.FilterType.LONGPASS,
                ),
                lens=devices.Lens(
                    name="Forward lens",
                    manufacturer=organizations.Organization.EDMUND_OPTICS,
                    focal_length=8.5,
                    focal_length_unit="millimeter",
                    model="86604",
                ),
                position=coordinates.RelativePosition(
                    device_position_transformations=[
                        coordinates.Rotation3dTransform(
                            rotation=[
                                -0.17365, 0.98481, 0,
                                0.44709, 0.07883, -0.89101,
                                -0.87747, -0.15472, -0.45399,
                            ]
                        ),
                        coordinates.Translation3dTransform(
                            translation=[0.154, 0.03078, 0.06346],
                        )
                    ],
                    **shared_camera_assembly_relative_position_props
                )
            ),
            devices.CameraAssembly(
                name=SIDE_CAMERA_ASSEMBLY_NAME,
                camera_target="Body",
                camera=devices.Camera(
                    name=SIDE_CAMERA_NAME,
                    manufacturer=organizations.Organization.ALLIED,
                    chroma="Monochrome",
                    data_interface="Ethernet",
                    **shared_camera_props,
                ),
                filter=devices.Filter(
                    name="Side filter",
                    manufacturer=organizations.Organization.SEMROCK,
                    model="FF01-747/33-25",
                    filter_type=devices.FilterType.BANDPASS,
                ),
                lens=devices.Lens(
                    name="Side lens",
                    manufacturer=organizations.Organization.NAVITAR,
                    focal_length=6.0,
                    focal_length_unit="millimeter",
                ),
                position=coordinates.RelativePosition(
                    device_position_transformations=[
                        coordinates.Rotation3dTransform(
                            rotation=[-1, 0, 0, 0, 0, -1, 0, -1, 0]
                        ),
                        coordinates.Translation3dTransform(
                            translation=[-0.03617, 0.23887, -0.02535],
                        )
                    ],
                    **shared_camera_assembly_relative_position_props
                )
            ),
            devices.CameraAssembly(
                name=EYE_CAMERA_ASSEMBLY_NAME,
                camera_target="Eye",
                camera=devices.Camera(
                    name=EYE_CAMERA_NAME,
                    manufacturer=organizations.Organization.ALLIED,
                    chroma="Monochrome",
                    data_interface="Ethernet",
                    **shared_camera_props,
                ),
                filter=devices.Filter(
                    name="Eye filter",
                    manufacturer=organizations.Organization.SEMROCK,
                    model="FF01-850/10-25",
                    filter_type=devices.FilterType.BANDPASS,
                ),
                lens=devices.Lens(
                    name="Eye lens",
                    manufacturer=(
                        organizations.Organization.INFINITY_PHOTO_OPTICAL),
                    focal_length=6.0,
                    focal_length_unit="millimeter",
                    model="213073",
                    notes="Model number is SKU.",
                ),
                position=coordinates.RelativePosition(
                    device_position_transformations=[
                        coordinates.Rotation3dTransform(
                            rotation=[
                                -0.5, -0.86603, 0,
                                -0.366, 0.21131, -0.90631,
                                0.78489, -0.45315, -0.42262,
                            ]
                        ),
                        coordinates.Translation3dTransform(
                            translation=[-0.14259, 0.06209, 0.09576],
                        )
                    ],
                    **shared_camera_assembly_relative_position_props
                )
            )
        ],
        daqs=[
            devices.DAQDevice(
                manufacturer=organizations.Organization.NATIONAL_INSTRUMENTS,
                name="Sync",
                computer_name=computer_name,
                model="NI-6612",
                data_interface=devices.DataInterface.PCIE,
            ),
            devices.DAQDevice(
                manufacturer=organizations.Organization.NATIONAL_INSTRUMENTS,
                name="Behavior",
                computer_name=computer_name,
                model="NI-6323",
                data_interface=devices.DataInterface.USB,
            ),
            devices.DAQDevice(
                manufacturer=organizations.Organization.NATIONAL_INSTRUMENTS,
                name="BehaviorSync",
                computer_name=computer_name,
                model="NI-6001",
                data_interface=devices.DataInterface.PCIE,
            ),
            devices.DAQDevice(
                manufacturer=organizations.Organization.NATIONAL_INSTRUMENTS,
                name="Opto",
                computer_name=computer_name,
                model="NI-9264",
                data_interface=devices.DataInterface.ETH,
            ),
        ],
        detectors=[
            devices.Detector(
                name="vsync photodiode",
                model="PDA25K",
                manufacturer=organizations.Organization.THORLABS,
                data_interface=devices.DataInterface.OTHER,
                notes="Data interface is unknown.",
                detector_type=devices.DetectorType.OTHER,
                cooling=devices.Cooling.AIR,
            ),
        ],
        calibrations=[],
        additional_devices=[
            devices.Detector(
                name="microphone",
                manufacturer=organizations.Organization.DODOTRONIC,
                model="MOM",
                data_interface=devices.DataInterface.OTHER,
                notes="Data interface is unknown.",
                detector_type=devices.DetectorType.OTHER,
                cooling=devices.Cooling.AIR,
            ),
            devices.AdditionalImagingDevice(
                name="Galvo x",
                type=devices.ImagingDeviceType.GALVO,
            ),
            devices.AdditionalImagingDevice(
                name="Galvo y",
                type=devices.ImagingDeviceType.GALVO,
            ),
        ],
        rig_axes=[
            coordinates.Axis(
                name=coordinates.AxisName.X,
                direction=(
                    "The world horizontal. Lays on the Mouse Sagittal Plane. "
                    "Positive direction is towards the nose of the mouse. "
                ),
            ),
            coordinates.Axis(
                name=coordinates.AxisName.Y,
                direction=(
                    "Perpendicular to Y. Positive direction is "
                    "away from the nose of the mouse. "
                ),
            ),
            coordinates.Axis(
                name=coordinates.AxisName.Z,
                direction="Positive pointing up.",
            )
        ],
        origin=coordinates.Origin.BREGMA,
        patch_cords=[
            devices.Patch(
                name="Patch Cord #1",
                manufacturer=organizations.Organization.THORLABS,
                model="SM450 Custom Length, FC/PC Ends",
                core_diameter=125.0,
                numerical_aperture=0.10,
                notes=(
                    "Numerical aperture is approximately between 0.10 and "
                    "0.14."
                ),
            ),
        ],
    )

    return rig.Rig.model_validate(model)


def setup_neuropixels_etl_dirs(
    expected_json: pathlib.Path,
) -> tuple[
        pathlib.Path,
        pathlib.Path,
        rig.Rig,
        typing.Callable[[], rig.Rig],
        typing.Callable[[], None]
]:
    """Sets up a temporary input/output directory context for neuropixels etl.

    Parameters
    ----------
    resources: paths to etl resources to move to input dir

    Returns
    -------
    input_dir: path to etl input dir
    output_dir: path to etl output dir
    clean_up: cleanup function for input/output dirs
    """
    input_dir = pathlib.Path(tempfile.mkdtemp())
    base_rig = init_rig()
    base_rig.write_standard_file(input_dir)

    _output_dir = pathlib.Path(tempfile.mkdtemp())

    def load_updated(output_dir: pathlib.Path = _output_dir):
        """Load updated rig.json."""
        return rig.Rig.model_validate_json(
            (output_dir / "rig.json").read_text()
        )

    def clean_up():
        """Clean up callback for temporary directories and their contents."""
        shutil.rmtree(input_dir)
        shutil.rmtree(_output_dir)

    return (
        input_dir / "rig.json",
        _output_dir,
        rig.Rig.model_validate_json(expected_json.read_text()),
        # base_rig,
        load_updated,
        clean_up,
    )
