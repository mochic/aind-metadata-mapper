import os
import json
import shutil
import unittest
import tempfile
import pathlib
import datetime

from aind_data_schema import __version__, rig
from aind_metadata_mapper.neuropixels import rig as neuropixels_rig


class TestNeuropixelsEtl(unittest.TestCase):

    def test_rig_etl(self):
        etl = neuropixels_rig.NeuropixelsRigEtl(
            self.input_dir,
            self.output_dir
        )
        etl.run_job()
        output = rig.Rig.parse_raw(
            (self.output_dir / "rig.json").read_text()
        )
        expected = rig.Rig.parse_raw(
            pathlib.Path("./tests/resources/neuropixels/expected-rig.json")
                .read_text()
        )
        # patch over expected property values that won't stay static over time
        expected.schema_version = output.schema_version
        expected.modification_date = output.modification_date,
        shutil.copy2(
            (self.output_dir / "rig.json"),
            pathlib.Path("./tests/resources/neuropixels/"),
        )
        assert output == expected

    def setUp(self):
        self.input_dir = pathlib.Path(
            tempfile.mkdtemp(),
        )
        shutil.copy2(
            pathlib.Path("./tests/resources/neuropixels/rig.partial.json"),
            self.input_dir,
        )
        shutil.copy2(
            pathlib.Path("./tests/resources/neuropixels/mvr.ini"),
            self.input_dir,
        )
        shutil.copy2(
            pathlib.Path("./tests/resources/neuropixels/mvr.mapping.json"),
            self.input_dir,
        )
        shutil.copy2(
            pathlib.Path("./tests/resources/neuropixels/sync.yml"),
            self.input_dir,
        )
        self.output_dir = pathlib.Path(
            tempfile.mkdtemp(),
        )

    def tearDown(self):
        shutil.rmtree(self.input_dir)
        shutil.rmtree(self.output_dir)
