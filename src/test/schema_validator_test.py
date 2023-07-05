import unittest
import os
from ctat.schema_validator import validate, validate_json_str, validate_json_file

SCHEMA = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                      "../../dosdp_schema.yaml")
VALID_TEST_DATA_1 = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/hierarchy.json")


class SchemaValidationTests(unittest.TestCase):

    def test_schema_validity1(self):
        test_data = """ [
            {
                "column_name": "cluster_id",
                "column_type": "cluster_id",
                "rank": 0
            },
            {
                "column_name": "cluster_name",
                "column_type": "cluster_name",
                "rank": 0
            }
        ]
        """
        self.assertTrue(validate_json_str(test_data))

        test_data = """ [
            {
                "column_name": "cluster_id",
                "column_type": "cluster_id",
                "rank": 0
            },
            {
                "column_name": "region.info (Frequency)",
                "column_type": "annotation_field"
            }
        ]
        """
        self.assertTrue(validate_json_str(test_data))

        test_data = """ [
            {
                "column_name": "cluster_id",
                "column_type": "cluster_id",
                "rank": 0
            },
            {
                "column_name": "region.info (Frequency)",
                "column_type": "annotation_field",
                "rank": 10
            }
        ]
        """
        # rank not allowed on grouping_field
        self.assertFalse(validate_json_str(test_data))

        self.assertTrue(validate_json_file(VALID_TEST_DATA_1))

