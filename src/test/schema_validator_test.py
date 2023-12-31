import unittest
import os
from ctat.schema_validator import validate, validate_json_str, validate_file

VALID_TEST_DATA_1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/test_config.yaml")
INVALID_TEST_DATA_1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/test_config_invalid.yaml")


class SchemaValidationTests(unittest.TestCase):

    def test_validator_yaml(self):
        self.assertTrue(validate_file(VALID_TEST_DATA_1))
        self.assertFalse(validate_file(INVALID_TEST_DATA_1))

