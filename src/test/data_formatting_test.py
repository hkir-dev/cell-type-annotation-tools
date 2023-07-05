import unittest
import os
from ctat.cell_type_annotation import format_data

RAW_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/AIT115_annotation_sheet.tsv")
VALID_TEST_DATA_1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/hierarchy.json")


class SchemaValidationTests(unittest.TestCase):

    def test_validator(self):
        pass