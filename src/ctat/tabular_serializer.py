import os
import pandas as pd
from dataclasses import asdict


class AccessionManager:
    """
    Accession ID generator.
    """

    def __init__(self, accession_prefix=None):
        """
        Initializer.
        Params:
            accession_prefix: accession_id prefix
        """
        self.accession_prefix = accession_prefix
        self.last_accession_id = 0
        self.accession_ids = list()

    def generate_accession_id(self, id_recommendation: str = None) -> str:
        """
        Generates an auto-increment based accession id. If the recommended accession_id is available, uses it.
        Params:
            id_recommendation: accession id recommendation. Function uses this id if it is available,
            provides an auto-incremented id otherwise.
        Return: accession_id
        """
        if (id_recommendation and id_recommendation not in self.accession_ids and
                int(id_recommendation) > self.last_accession_id):
            accession_id = id_recommendation
            self.last_accession_id = int(id_recommendation)
        else:
            id_candidate = self.last_accession_id + 1
            while str(id_candidate) in self.accession_ids:
                id_candidate += 1
            accession_id = str(id_candidate)
            self.last_accession_id = id_candidate

        self.accession_ids.append(accession_id)
        if self.accession_prefix:
            accession_id = self.accession_prefix + accession_id

        return accession_id


def serialize_to_tables(cta, file_name_prefix, out_folder, accession_prefix):
    """
    Writes cell type annotation object to a series of tsv files.
    Tables to generate:
        - Annotation table (main)
        - Labelset table
        - Metadata
        - Annotation transfer
    :param cta: cell type annotation object to serialize.
    :param file_name_prefix: Name prefix for table names
    :param out_folder: output folder path.
    :param accession_prefix: accession id prefix
    """
    annotation_table_path = generate_annotation_table(accession_prefix, cta, file_name_prefix, out_folder)
    return annotation_table_path


def generate_annotation_table(accession_prefix, cta, file_name_prefix, out_folder):
    """
    Generates annotation table.
    :param cta: cell type annotation object to serialize.
    :param file_name_prefix: Name prefix for table names
    :param out_folder: output folder path.
    :param accession_prefix: accession id prefix
    """
    std_data_path = os.path.join(out_folder, file_name_prefix + "_annotation.tsv")
    accession_manager = AccessionManager(accession_prefix)

    cta = asdict(cta)
    std_records = list()
    std_parent_records = list()
    std_parent_records_dict = dict()
    for annotation_object in cta["annotations"]:
        record = dict()
        if "cell_set_accession" in annotation_object and annotation_object["cell_set_accession"]:
            record["cell_set_accession"] = (accession_manager.generate_accession_id(
                annotation_object.get("cell_set_accession", "")))
            record["cell_label"] = annotation_object.get("cell_label", "")
            record["cell_fullname"] = annotation_object.get("cell_fullname", "")
            record["parent_cell_set_accession"] = ""
            record["parent_cell_set_name"] = ""
            record["labelset"] = str(annotation_object.get("labelset", "")).replace("_name", "")
            record["cell_ontology_term_id"] = annotation_object.get("cell_ontology_term_id", "")
            record["cell_ontology_term"] = annotation_object.get("cell_ontology_term", "")
            record["rationale"] = annotation_object.get("rationale", "")
            record["rationale_dois"] = annotation_object.get("rationale_dois", "")
            record["marker_gene_evidence"] = annotation_object.get("marker_gene_evidence", "")
            record["synonyms"] = annotation_object.get("synonyms", "")
            if "user_annotations" in annotation_object and annotation_object["user_annotations"]:
                for user_annot in annotation_object["user_annotations"]:
                    record[normalize_column_name(user_annot["annotation_set"])] = user_annot["cell_label"]
            record["cell_ids"] = annotation_object.get("cell_ids", "")
            std_records.append(record)
        else:
            # parent nodes
            parent_label = annotation_object["cell_label"]
            if parent_label not in [parent["cell_label"] for parent in std_parent_records]:
                record["cell_set_accession"] = ""
                record["cell_label"] = parent_label
                record["cell_fullname"] = ""
                record["parent_cell_set_accession"] = ""
                record["parent_cell_set_name"] = ""
                record["labelset"] = str(annotation_object.get("labelset", "")).replace("_name", "")
                std_parent_records.append(record)
        if "parent_cell_set_name" in annotation_object:
            record["parent_cell_set_name"] = annotation_object["parent_cell_set_name"]
            if annotation_object["parent_cell_set_name"] in std_parent_records_dict:
                std_parent_records_dict.get(annotation_object["parent_cell_set_name"]).append(record)
            else:
                children = list()
                children.append(record)
                std_parent_records_dict[annotation_object["parent_cell_set_name"]] = children
    assign_parent_accession_ids(accession_manager, std_parent_records, std_parent_records_dict, cta["labelsets"])
    std_records.extend(std_parent_records)
    std_records_df = pd.DataFrame.from_records(std_records)
    std_records_df.to_csv(std_data_path, sep="\t", index=False)
    return std_data_path


def assign_parent_accession_ids(accession_manager, std_parent_records, std_parent_records_dict, labelsets):
    """
    Assigns accession ids to parent clusters and updates their references from the child clusters.
    Params:
        accession_manager: accession ID generator
        std_parent_records: list of all parents to assign accession ids
        std_parent_records_dict: parent cluster - child clusters dictionary
        labelsets: labelsets list
    """
    label_set_ranks = dict([(label_set["name"].replace("_name", ""), label_set["rank"]) for label_set in labelsets])

    std_parent_records.sort(key=lambda x: int(label_set_ranks[x["labelset"]]))
    for std_parent_record in std_parent_records:
        accession_id = accession_manager.generate_accession_id()
        std_parent_record["cell_set_accession"] = accession_id

        children = std_parent_records_dict.get(std_parent_record["cell_label"], list())
        for child in children:
            child["parent_cell_set_accession"] = accession_id


def normalize_column_name(column_name: str) -> str:
    """
    Normalizes column name for nanobot compatibility.
    Nanobot column name requirement: All names must match: ^[\w_ ]+$' for to_url()

    Parameters:
        column_name: current column name
    Returns:
        normalized column_name
    """
    return column_name.strip().replace("(", "_").replace(")", "_")
