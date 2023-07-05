from typing import List, Optional, Any
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

from ctat.schema_validator import validate


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TaxonomyMetadata:

    taxonomy_id: Optional[str] = ""
    species_id: Optional[str] = ""
    species_name: Optional[str] = ""
    brain_region_id: Optional[str] = ""
    brain_region_name: Optional[str] = ""


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LabelTransfer:

    transferred_label: str
    source_taxonomy: TaxonomyMetadata
    source_taxonomy_cell_set_accession: str
    algorithm: Optional[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AnnotationObject:

    label_set_name: str
    author_node_name: str
    accession_id: Optional[str]
    cell_ontology_mapping: str
    cell_barcodes: Optional[List[str]]  # mandatory for cell types
    parent_node_name: Optional[str]
    synonyms: Optional[List[str]]
    label_transfer_object: Optional[LabelTransfer]
    evidence_markers: Optional[List[str]]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CellTypeAnnotation:

    data_url: str
    annotation_objects: List[AnnotationObject]
    taxonomy: TaxonomyMetadata = None


def format_data(data_file: str, config_file: str):
    """
    Formats given data into standard cell type annotation data structure using the given configuration.

    :param data_file: Unformatted user data in tsv/csv format.
    :param config_file: configuration file path.
    :return:
    """
    config = load_config(config_file)
    is_config_valid = validate(config)
    if not is_config_valid:
        raise Exception("Configuration file is not valid!")



    return ""
