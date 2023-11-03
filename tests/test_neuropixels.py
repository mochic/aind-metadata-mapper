import os
import json
import shutil
import unittest
import tempfile
import pathlib

from aind_metadata_mapper.neuropixels import rig


class TestNeuropixelsEtl(unittest.TestCase):
    
    def setUp(self):
        self.input_dir = pathlib.Path(
            tempfile.mkdtemp(),
        )
        shutil.copy2(
            pathlib.Path("./tests/resources/neuropixels/base.json"),
            self.input_dir,
        )
        shutil.copy2(
            pathlib.Path("./tests/resources/neuropixels/camera-meta.json"),
            self.input_dir,
        )
        self.output_dir = pathlib.Path(
            tempfile.mkdtemp(),
        )

    def tearDown(self):
        shutil.rmtree(self.input_dir)
        shutil.rmtree(self.output_dir)

    def test_rig_etl(self):
        etl = rig.NeuropixelsRigEtl(
            self.input_dir,
            self.output_dir
        )
        etl.run_job()
        output = json.loads(
            (self.output_dir / "rig.json").read_text()
        )
        expected = json.loads(
            pathlib.Path("./tests/resources/neuropixels/expected.json")
                .read_text()
        )

        assert output == expected
