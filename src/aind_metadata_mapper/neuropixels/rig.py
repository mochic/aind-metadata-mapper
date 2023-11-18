import json
import yaml
import pathlib
import datetime
import configparser
from aind_data_schema import rig, device

from ..core import BaseEtl


class NeuropixelsRigException(Exception):
    """General error for MVR."""


MVRCamera = tuple[str, str, int, int, float]  # assembly name, serial number, height, width, frame rate
SyncChannel = tuple[int, str]  # di line index, name
SyncContext = tuple[str, float, list[SyncChannel]]  # device name, sample rate, channels
RigContext = tuple[dict, list[MVRCamera], SyncContext]


class NeuropixelsRigEtl(BaseEtl):

    def __init__(
        self,
        input_source: pathlib.Path,
        output_directory: pathlib.Path,
    ):
        """Class constructor for Neuropixels rig etl class.
        
        Parameters
        ----------
        input_source : Path
          Can be a string or a Path
        output_directory : Path
          The directory where to save the json files.
        """
        super().__init__(input_source, output_directory)

    def _load_resource(self, path: pathlib.Path) -> str:
        if not path.exists():
            raise NeuropixelsRigException("%s not found." % path)
        
        return path.read_text()

    def _extract(self) -> RigContext:
        if not self.input_source.is_dir():
            raise NeuropixelsRigException(
                "Input source is not a directory. %s" % self.input_source
            )

        return (
            json.loads(
                self._load_resource(
                    self.input_source / "rig.partial.json",
                )
            ),
            self._extract_mvr(
                self._load_resource(
                    self.input_source / "mvr.ini",
                ),
                json.loads(
                    self._load_resource(
                        self.input_source / "mvr.mapping.json",
                    )
                ),
            ),
            self._extract_sync(
                self._load_resource(
                    self.input_source / "sync.yml",
                )
            ),
        )

    def _extract_mvr(self, content: str, mapping: dict) -> list[MVRCamera]:
        config = configparser.ConfigParser()
        config.read_string(content)
        frame_rate = float(config["CAMERA_DEFAULT_CONFIG"]["frames_per_second"])
        height = int(config["CAMERA_DEFAULT_CONFIG"]["height"])
        width = int(config["CAMERA_DEFAULT_CONFIG"]["width"])

        extracted = []
        for mvr_name, assembly_name in mapping.items():
            try:
                extracted.append(
                    (
                        assembly_name,
                        "".join(config[mvr_name]["sn"]),
                        height,
                        width,
                        frame_rate,
                    )
                )
            except KeyError:
                raise NeuropixelsRigException(
                    "No camera found for: %s in mvr.ini" %
                    mvr_name
                )
        return extracted

    def _extract_sync(self, content: str) -> SyncContext:
        config = yaml.safe_load(content)
        return (
            config["device"],
            config["freq"],
            list(config["line_labels"].items()),
        )

    def _transform(self, extracted_source: RigContext) -> rig.Rig:
        partial, mvr_cameras, sync_context = extracted_source

        # search for partial sync daq
        sync_device_name, sync_sample_rate, sync_channels = sync_context
        sync_daq_name = "Sync"
        for idx, partial_daq in enumerate(partial["daqs"]):
            if partial_daq["name"] == sync_daq_name:
                partial_sync_daq = partial["daqs"].pop(idx)  # remove from daqs for later spread operation
                break
        else:
            raise NeuropixelsRigException(
                "Sync daq not found in partial rig. expected name=%s" % 
                sync_daq_name
            )

        sync_daq = {
            **partial_sync_daq,
            "channels": [
                {
                    "channel_name": name,
                    "channel_type": "Digital Input",
                    "device_name": sync_device_name,
                    "event_based_sampling": False,
                    "channel_index": line,
                    "sample_rate": sync_sample_rate,
                    "sample_rate_unit": "hertz"
                }
                for line, name in sync_channels
            ],
        }

        camera_assemblies = []
        for partial_camera_assembly in partial["cameras"]:
            name = partial_camera_assembly["camera_assembly_name"]

            found = list(filter(
                lambda camera: camera[0] == name,
                mvr_cameras,
            ))
            if len(found) < 1:
                raise NeuropixelsRigException(
                    "Camera assembly not found in partial rig. expected name=%s" %
                    name
                )
            
            assembly_name, serial_number, height, width, frame_rate = found[0]
            camera_assemblies.append({
                **partial_camera_assembly,
                "camera": {
                    **partial_camera_assembly["camera"],
                    "name": assembly_name,
                    "serial_number": serial_number,
                    "pixel_height": height,
                    "pixel_width": width,
                    "size_unit": "pixel",
                    "max_frame_rate": frame_rate,
                }
            })

        return rig.Rig.parse_obj({
            **partial,
            "daqs": [
                *partial["daqs"],
                sync_daq,
            ],
            "cameras": camera_assemblies,
        })


        cameras = []
        for camera_assembly in base["cameras"]:
            camera_kwargs = camera_assembly["camera"]
            camera_kwargs["computer_name"] = camera_meta["host"]
            cameras.append(
                rig.CameraAssembly(
                    camera_target=camera_assembly["camera_target"],
                    camera_assembly_name=camera_assembly["camera_assembly_name"],
                    camera=device.Camera(**camera_kwargs),
                    lens=rig.Lens(**camera_assembly["lens"])
                )
            )
        return rig.Rig(
            describedBy=base["describedBy"],
            rig_id=base["rig_id"],
            modification_date=base["modification_date"],
            modalities=base["modalities"],
            mouse_platform=device.Disc(**base["mouse_platform"]),
            cameras=cameras,
            ephys_assemblies=[
                rig.EphysAssembly(
                    ephys_assembly_name=ephys_assembly["ephys_assembly_name"],
                    manipulator=device.Manipulator(**ephys_assembly["manipulator"]),
                    probes=[
                        device.EphysProbe(**probe)
                        for probe in ephys_assembly["probes"]
                    ],
                )
                for ephys_assembly in base["ephys_assemblies"]
            ],
            laser_assemblies=[
                rig.LaserAssembly(
                    laser_assembly_name=laser_assembly["laser_assembly_name"],
                    manipulator=device.Manipulator(
                        **laser_assembly["manipulator"]
                    ),
                    lasers=[
                        rig.Laser(**laser)
                        for laser in laser_assembly["lasers"]
                    ],
                )
                for laser_assembly in base["laser_assemblies"]
            ],
            light_sources=[
                device.LightEmittingDiode(**led)
                for led in base["light_sources"]
            ],
            stimulus_devices=list(map(
                load_stimulus_device,
                base["stimulus_devices"],
            )),
            calibrations=[],
        )