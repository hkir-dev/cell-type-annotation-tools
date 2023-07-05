import unittest
import os
from ctat.cell_type_annotation import format_data

RAW_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/AIT115_annotation_sheet.tsv")
TEST_CONFIG = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/test_config.yaml")


class CellTypeAnnotationTests(unittest.TestCase):

    def test_data_formatting(self):
        format_data(RAW_DATA, TEST_CONFIG)
