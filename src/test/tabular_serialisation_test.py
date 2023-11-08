import unittest
import os
from ctat.cell_type_annotation import ingest_user_data, CellTypeAnnotation
from ctat.tabular_serializer import serialize_to_tables
from ctat.file_utils import read_csv_to_dict

RAW_DATA = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/AIT115_annotation_sheet.tsv")
TEST_CONFIG = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/test_config.yaml")

OUT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./test_data/table_out/")


class TabularSerialisationTests(unittest.TestCase):
    def setUp(self):
        test_folder = os.listdir(OUT_FOLDER)
        for item in test_folder:
            if item.endswith(".tsv"):
                os.remove(os.path.join(OUT_FOLDER, item))

    def test_annotation_table(self):
        cta = ingest_user_data(RAW_DATA, TEST_CONFIG)
        serialize_to_tables(cta, "Test_table", OUT_FOLDER, "TST_")

        annotation_table_path = os.path.join(OUT_FOLDER, "Test_table_annotation.tsv")
        self.assertTrue(os.path.isfile(annotation_table_path))

        headers, records = read_csv_to_dict(annotation_table_path, id_column_name="cell_set_accession", delimiter="\t")
        self.assertEqual(354, len(records))

        cluster_1 = records['TST_1']
        self.assertEqual("1_MSN", cluster_1["cell_label"])
        self.assertEqual("TST_300", cluster_1["parent_cell_set_accession"])
        self.assertEqual("D1-Matrix", cluster_1["parent_cell_set_name"])
        self.assertEqual("cluster", cluster_1["labelset"])
        self.assertEqual("['EPYC', 'RELN', 'GULP1']", cluster_1["marker_gene_evidence"])
        self.assertEqual("PuR(0.52) | CaH(0.39)", cluster_1["region.info _Frequency_"])
        self.assertEqual("", cluster_1["cell_ids"])

        cluster_300 = records['TST_300']
        self.assertEqual("D1-Matrix", cluster_300["cell_label"])
        self.assertEqual("TST_339", cluster_300["parent_cell_set_accession"])
        self.assertEqual("D1-MSN", cluster_300["parent_cell_set_name"])
        self.assertEqual("level 3 (subclass)", cluster_300["labelset"])

        cluster_339 = records['TST_339']
        self.assertEqual("D1-MSN", cluster_339["cell_label"])
        self.assertEqual("TST_365", cluster_339["parent_cell_set_accession"])
        self.assertEqual("MSN", cluster_339["parent_cell_set_name"])
        self.assertEqual("level 2 (neighborhood)", cluster_339["labelset"])

        cluster_365 = records['TST_365']
        self.assertEqual("MSN", cluster_365["cell_label"])
        self.assertEqual("", cluster_365["parent_cell_set_accession"])
        self.assertEqual("", cluster_365["parent_cell_set_name"])
        self.assertEqual("level1 (class)", cluster_365["labelset"])
