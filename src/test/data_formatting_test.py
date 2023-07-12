import unittest
import os
from ctat.cell_type_annotation import format_data

RAW_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/AIT115_annotation_sheet.tsv")
TEST_CONFIG = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/test_config.yaml")
OUT_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/test_result.json")


class CellTypeAnnotationTests(unittest.TestCase):
    def setUp(self):
        if os.path.isfile(OUT_FILE):
            os.remove(OUT_FILE)

    def test_data_formatting(self):
        result = format_data(RAW_DATA, TEST_CONFIG, OUT_FILE)
        # print(result)
        print(type(result))
        self.assertTrue(result)
        self.assertTrue("dataUrl" in result)
        self.assertEqual("my_data_url", result["dataUrl"])


