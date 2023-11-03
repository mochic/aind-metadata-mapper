import json
import pathlib
import dataclasses
import datetime
from aind_data_schema import rig, device

from ..core import BaseEtl


@dataclasses.dataclass
class CameraMeta:

    host: str


RigAssets = tuple[dict, CameraMeta]  # rig base, camera meta


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

    def _extract(self) -> RigAssets:
        if not self.input_source.is_dir():
            raise Exception("Input source is not a directory. %s" % self.input_source)
        
        base_path = self.input_source / "base.json"
        if not base_path.exists():
            raise Exception("Base not found.")

        camera_meta_path = self.input_source / "camera-meta.json"
        if not camera_meta_path.exists():
            raise Exception("Camera meta not found.")
        
        base = json.loads(base_path.read_text())
        camera_meta = json.loads(camera_meta_path.read_text())

        return (base, camera_meta)


    def _transform(self, extracted_source: RigAssets) -> rig.Rig:
        base, camera_meta = extracted_source

        def load_stimulus_device(d: dict):
            stimulus_device = d["device_type"].lower()
            if stimulus_device == "monitor":
                return device.Monitor(**d)
            elif stimulus_device == "speaker":
                return device.Speaker(**d)
            raise Exception(f"Unexpected device type: {stimulus_device}")

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