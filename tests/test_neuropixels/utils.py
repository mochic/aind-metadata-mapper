"""Utilities for neuropixels etl tests."""
import os
from datetime import date
from pathlib import Path
from typing import Tuple

from aind_data_schema.core.rig import Rig  # type: ignore
from aind_data_schema.models.coordinates import (  # type: ignore
    Axis,
    AxisName,
    Origin,
    RelativePosition,
    Rotation3dTransform,
    Translation3dTransform,
)
from aind_data_schema.models.devices import (  # type: ignore
    AdditionalImagingDevice,
    Camera,
    CameraAssembly,
    Cooling,
    DAQDevice,
    DataInterface,
    Detector,
    DetectorType,
    Device,
    Disc,
    EphysAssembly,
    EphysProbe,
    Filter,
    FilterType,
    ImagingDeviceType,
    Laser,
    Lens,
    LickSensorType,
    LightEmittingDiode,
    Manipulator,
    Monitor,
    Patch,
    RewardDelivery,
    RewardSpout,
    Speaker,
    SpoutSide,
)
from aind_data_schema.models.modalities import Modality  # type: ignore
from aind_data_schema.models.organizations import Organization  # type: ignore
from aind_data_schema.models.units import SizeUnit  # type: ignore

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "neuropixels"
)

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


def init_rig() -> Rig:
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
        "size_unit": SizeUnit.NM,
        "notes": "Max frame rate is at maximum resolution.",
        "cooling": Cooling.NONE,
        "computer_name": computer_name,
    }

    shared_camera_assembly_relative_position_props = {
        "device_origin": (
            "Located on face of the lens mounting surface in its center"
        ),
        "device_axes": [
            Axis(
                name=AxisName.X,
                direction=(
                    "Oriented so that it is parallel to the bottom edge of "
                    "the sensor."
                ),
            ),
            Axis(
                name=AxisName.Y,
                direction=("Pointing to the bottom edge of the sensor."),
            ),
            Axis(
                name=AxisName.Z,
                direction=(
                    "Positive moving away from the sensor towards the object."
                ),
            ),
        ],
        "notes": COPA_NOTES,
    }

    model = Rig(
        rig_id="327_NP2_240401",
        modification_date=date(2024, 4, 1),
        modalities=[
            Modality.BEHAVIOR_VIDEOS,
            Modality.BEHAVIOR,
            Modality.ECEPHYS,
        ],
        mouse_platform=Disc(
            name="Mouse Platform",
            radius="4.69",
            radius_unit="centimeter",
            notes=(
                "Radius is the distance from the center of the wheel to the "
                "mouse."
            ),
        ),
        stimulus_devices=[
            Monitor(
                name="Stim",
                model="PA248",
                manufacturer=Organization.ASUS,
                width=1920,
                height=1200,
                size_unit="pixel",
                viewing_distance=15.3,
                viewing_distance_unit="centimeter",
                refresh_rate=60,
                brightness=43,
                contrast=50,
                position=RelativePosition(
                    device_position_transformations=[
                        Rotation3dTransform(
                            rotation=[
                                -0.80914,
                                -0.58761,
                                0,
                                -0.12391,
                                0.17063,
                                0.97751,
                                0.08751,
                                -0.12079,
                                0.02298,
                            ],
                        ),
                        Translation3dTransform(
                            translation=[0.08751, -0.12079, 0.02298]
                        ),
                    ],
                    device_origin=(
                        "Located at the center of the screen. Right and left "
                        "conventions are relative to the screen side of "
                        "the monitor."
                    ),
                    device_axes=[
                        Axis(
                            name=AxisName.X,
                            direction=(
                                "Oriented so that it is parallel to the long "
                                "edge of the screen. Positive pointing right."
                            ),
                        ),
                        Axis(
                            name=AxisName.Y,
                            direction=(
                                "Positive pointing to the top of the screen."
                            ),
                        ),
                        Axis(
                            name=AxisName.Z,
                            direction=(
                                "Positive moving away from the screen."
                            ),
                        ),
                    ],
                    notes=COPA_NOTES,
                ),
            ),
            Speaker(
                name="Speaker",
                manufacturer=Organization.ISL,
                model="SPK-I-81345",
                position=RelativePosition(
                    device_position_transformations=[
                        Rotation3dTransform(
                            rotation=[
                                -0.82783,
                                -0.4837,
                                -0.28412,
                                -0.55894,
                                0.75426,
                                0.34449,
                                0.04767,
                                0.44399,
                                -0.89476,
                            ],
                        ),
                        Translation3dTransform(
                            translation=[-0.00838, -0.09787, 0.18228]
                        ),
                    ],
                    device_origin=(
                        "Located on front mounting flange face. Right and left"
                        " conventions are relative to the front side of the "
                        "speaker."
                    ),
                    device_axes=[
                        Axis(
                            name=AxisName.X,
                            direction=(
                                "Oriented so it will intersect the center of "
                                "a bolt hole on the mounting flange."
                            ),
                        ),
                        Axis(
                            name=AxisName.Y,
                            direction=(
                                "Positive pointing to the top of the speaker."
                            ),
                        ),
                        Axis(
                            name=AxisName.Z,
                            direction=(
                                "Positive moving away from the speaker."
                            ),
                        ),
                    ],
                    notes=COPA_NOTES
                    + (
                        " Speaker to be mounted with the X axis pointing to "
                        "the right when viewing the speaker along the Z axis"
                    ),
                ),
            ),
            RewardDelivery(
                reward_spouts=[
                    RewardSpout(
                        name="Reward Spout",
                        manufacturer=Organization.HAMILTON,
                        model="8649-01 Custom",
                        spout_diameter=0.672,
                        spout_diameter_unit="millimeter",
                        side=SpoutSide.CENTER,
                        solenoid_valve=Device(
                            name="Solenoid Valve",
                            device_type="Solenoid Valve",
                            manufacturer=Organization.NRESEARCH,
                            model="161K011",
                            notes="Model number is product number.",
                        ),
                        lick_sensor=Device(
                            name="Lick Sensor",
                            device_type="Lick Sensor",
                            manufacturer=Organization.OTHER,
                        ),
                        lick_sensor_type=LickSensorType.PIEZOELECTIC,
                        notes=(
                            "Spout diameter is for inner diameter. "
                            "Outer diameter is 1.575mm. "
                        ),
                    ),
                ]
            ),
        ],
        ephys_assemblies=[
            EphysAssembly(
                name=f"Ephys Assembly {assembly_letter}",
                manipulator=Manipulator(
                    name=f"Ephys Assembly {assembly_letter} Manipulator",
                    manufacturer=(Organization.NEW_SCALE_TECHNOLOGIES),
                    model="06591-M-0004",
                ),
                probes=[
                    EphysProbe(
                        name=f"Probe{assembly_letter}",
                        probe_model="Neuropixels 1.0",
                        manufacturer=Organization.IMEC,
                    )
                ],
            )
            for assembly_letter in ["A", "B", "C", "D", "E", "F"]
        ],
        light_sources=[
            LightEmittingDiode(
                manufacturer=Organization.OTHER,
                name="Face forward LED",
                model="LZ4-40R308-0000",
                wavelength=740,
                wavelength_unit=SizeUnit.NM,
            ),
            LightEmittingDiode(
                manufacturer=Organization.OTHER,
                name="Body LED",
                model="LZ4-40R308-0000",
                wavelength=740,
                wavelength_unit=SizeUnit.NM,
            ),
            LightEmittingDiode(
                manufacturer=Organization.OSRAM,
                name="Eye LED",
                model="LZ4-40R608-0000",
                wavelength=850,
                wavelength_unit=SizeUnit.NM,
            ),
            Laser(
                name="Laser #0",
                manufacturer=Organization.VORTRAN,
                wavelength=488.0,
                model="Stradus 488-50",
                wavelength_unit="nanometer",
            ),
            Laser(
                name="Laser #1",
                manufacturer=Organization.VORTRAN,
                wavelength=633.0,
                model="Stradus 633-80",
                wavelength_unit="nanometer",
            ),
        ],
        cameras=[
            CameraAssembly(
                name=FORWARD_CAMERA_ASSEMBLY_NAME,
                camera_target="Face forward",
                camera=Camera(
                    name=FORWARD_CAMERA_NAME,
                    manufacturer=Organization.ALLIED,
                    chroma="Monochrome",
                    data_interface="Ethernet",
                    **shared_camera_props,
                ),
                filter=Filter(
                    name="Forward filter",
                    manufacturer=Organization.SEMROCK,
                    model="FF01-715_LP-25",
                    filter_type=FilterType.LONGPASS,
                ),
                lens=Lens(
                    name="Forward lens",
                    manufacturer=Organization.EDMUND_OPTICS,
                    focal_length=8.5,
                    focal_length_unit="millimeter",
                    model="86604",
                ),
                position=RelativePosition(
                    device_position_transformations=[
                        Rotation3dTransform(
                            rotation=[
                                -0.17365,
                                0.98481,
                                0,
                                0.44709,
                                0.07883,
                                -0.89101,
                                -0.87747,
                                -0.15472,
                                -0.45399,
                            ]
                        ),
                        Translation3dTransform(
                            translation=[0.154, 0.03078, 0.06346],
                        ),
                    ],
                    **shared_camera_assembly_relative_position_props,
                ),
            ),
            CameraAssembly(
                name=SIDE_CAMERA_ASSEMBLY_NAME,
                camera_target="Body",
                camera=Camera(
                    name=SIDE_CAMERA_NAME,
                    manufacturer=Organization.ALLIED,
                    chroma="Monochrome",
                    data_interface="Ethernet",
                    **shared_camera_props,
                ),
                filter=Filter(
                    name="Side filter",
                    manufacturer=Organization.SEMROCK,
                    model="FF01-747/33-25",
                    filter_type=FilterType.BANDPASS,
                ),
                lens=Lens(
                    name="Side lens",
                    manufacturer=Organization.NAVITAR,
                    focal_length=6.0,
                    focal_length_unit="millimeter",
                ),
                position=RelativePosition(
                    device_position_transformations=[
                        Rotation3dTransform(
                            rotation=[-1, 0, 0, 0, 0, -1, 0, -1, 0]
                        ),
                        Translation3dTransform(
                            translation=[-0.03617, 0.23887, -0.02535],
                        ),
                    ],
                    **shared_camera_assembly_relative_position_props,
                ),
            ),
            CameraAssembly(
                name=EYE_CAMERA_ASSEMBLY_NAME,
                camera_target="Eye",
                camera=Camera(
                    name=EYE_CAMERA_NAME,
                    manufacturer=Organization.ALLIED,
                    chroma="Monochrome",
                    data_interface="Ethernet",
                    **shared_camera_props,
                ),
                filter=Filter(
                    name="Eye filter",
                    manufacturer=Organization.SEMROCK,
                    model="FF01-850/10-25",
                    filter_type=FilterType.BANDPASS,
                ),
                lens=Lens(
                    name="Eye lens",
                    manufacturer=(Organization.INFINITY_PHOTO_OPTICAL),
                    focal_length=6.0,
                    focal_length_unit="millimeter",
                    model="213073",
                    notes="Model number is SKU.",
                ),
                position=RelativePosition(
                    device_position_transformations=[
                        Rotation3dTransform(
                            rotation=[
                                -0.5,
                                -0.86603,
                                0,
                                -0.366,
                                0.21131,
                                -0.90631,
                                0.78489,
                                -0.45315,
                                -0.42262,
                            ]
                        ),
                        Translation3dTransform(
                            translation=[-0.14259, 0.06209, 0.09576],
                        ),
                    ],
                    **shared_camera_assembly_relative_position_props,
                ),
            ),
        ],
        daqs=[
            DAQDevice(
                manufacturer=Organization.NATIONAL_INSTRUMENTS,
                name="Sync",
                computer_name=computer_name,
                model="NI-6612",
                data_interface=DataInterface.PCIE,
            ),
            DAQDevice(
                manufacturer=Organization.NATIONAL_INSTRUMENTS,
                name="Behavior",
                computer_name=computer_name,
                model="NI-6323",
                data_interface=DataInterface.USB,
            ),
            DAQDevice(
                manufacturer=Organization.NATIONAL_INSTRUMENTS,
                name="BehaviorSync",
                computer_name=computer_name,
                model="NI-6001",
                data_interface=DataInterface.PCIE,
            ),
            DAQDevice(
                manufacturer=Organization.NATIONAL_INSTRUMENTS,
                name="Opto",
                computer_name=computer_name,
                model="NI-9264",
                data_interface=DataInterface.ETH,
            ),
        ],
        detectors=[
            Detector(
                name="vsync photodiode",
                model="PDA25K",
                manufacturer=Organization.THORLABS,
                data_interface=DataInterface.OTHER,
                notes="Data interface is unknown.",
                detector_type=DetectorType.OTHER,
                cooling=Cooling.AIR,
            ),
        ],
        calibrations=[],
        additional_devices=[
            Detector(
                name="microphone",
                manufacturer=Organization.DODOTRONIC,
                model="MOM",
                data_interface=DataInterface.OTHER,
                notes="Data interface is unknown.",
                detector_type=DetectorType.OTHER,
                cooling=Cooling.AIR,
            ),
            AdditionalImagingDevice(
                name="Galvo x",
                imaging_device_type=ImagingDeviceType.GALVO,
            ),
            AdditionalImagingDevice(
                name="Galvo y",
                imaging_device_type=ImagingDeviceType.GALVO,
            ),
        ],
        rig_axes=[
            Axis(
                name=AxisName.X,
                direction=(
                    "The world horizontal. Lays on the Mouse Sagittal Plane. "
                    "Positive direction is towards the nose of the mouse. "
                ),
            ),
            Axis(
                name=AxisName.Y,
                direction=(
                    "Perpendicular to Y. Positive direction is "
                    "away from the nose of the mouse. "
                ),
            ),
            Axis(
                name=AxisName.Z,
                direction="Positive pointing up.",
            ),
        ],
        origin=Origin.BREGMA,
        patch_cords=[
            Patch(
                name="Patch Cord #1",
                manufacturer=Organization.THORLABS,
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

    return Rig.model_validate(model)


def setup_neuropixels_etl_resources(
    expected_json: Path,
) -> Tuple[Path, Path, Rig]:
    """Sets test resources neuropixels etl.

    Parameters
    ----------
    expected_json: Path
      paths to etl resources to move to input dir

    Returns
    -------
    Tuple[Path, Path, Rig]
      input_source: path to etl base rig input source
      output_dir: path to etl output directory
      expected_rig: rig model to compare to output
    """
    init_rig().write_standard_file()
    return (
        RESOURCES_DIR / "base_rig.json",
        Path("./"),  # hopefully file writes are mocked
        Rig.model_validate_json(expected_json.read_text()),
    )
