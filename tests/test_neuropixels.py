import json
import shutil
import unittest
import tempfile
import pathlib

from aind_data_schema import rig
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
        expected_template = json.loads(
            pathlib.Path("./tests/resources/neuropixels/expected-rig.json")
            .read_text()
        )
        # patch over expected property values that won't stay static over time
        expected = rig.Rig.parse_obj({
            **expected_template,
            "schema_version": output.schema_version,
            "modification_date": output.modification_date,
        })

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
