import os
import json
import shutil
import unittest
import tempfile
import pathlib

from aind_metadata_mapper import neuropixels


class TestNeuropixelsEtl(unittest.TestCase):

    def test_mvr_etl(self):
        etl = neuropixels.mvr.MVREtl(
            self.input_dir,
            self.output_dir
        )
        etl.run_job()
        output = json.loads(
            (self.output_dir / "cameras.json").read_text()
        )
        expected = json.loads(
            pathlib.Path("./tests/resources/neuropixels/mvr-expected.json")
                .read_text()
        )

        print(output)
        print(expected)
        assert output == expected

    # def test_rig_etl(self):
    #     etl = rig.NeuropixelsRigEtl(
    #         self.input_dir,
    #         self.output_dir
    #     )
    #     etl.run_job()
    #     output = json.loads(
    #         (self.output_dir / "rig.json").read_text()
    #     )
    #     expected = json.loads(
    #         pathlib.Path("./tests/resources/neuropixels/expected.json")
    #             .read_text()
    #     )

    #     print(output)
    #     print(expected)
    #     assert output == expected

    def setUp(self):
        self.input_dir = pathlib.Path(
            tempfile.mkdtemp(),
        )
        shutil.copy2(
            pathlib.Path("./tests/resources/neuropixels/mvr.ini"),
            self.input_dir,
        )
        shutil.copy2(
            pathlib.Path("./tests/resources/neuropixels/mvr-meta.json"),
            self.input_dir,
        )
        self.output_dir = pathlib.Path(
            tempfile.mkdtemp(),
        )

    def tearDown(self):
        shutil.rmtree(self.input_dir)
        shutil.rmtree(self.output_dir)
