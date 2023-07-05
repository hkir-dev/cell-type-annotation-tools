from typing import List, Optional, Any
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

from ctat.schema_validator import load_config, validate
from ctat.file_utils import read_tsv_to_dict


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class TaxonomyMetadata:

    taxonomy_id: Optional[str] = ""
    species_ids: Optional[str] = ""
    species_names: Optional[str] = ""
    brain_region_ids: Optional[str] = ""
    brain_region_names: Optional[str] = ""


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
    cell_ontology_mapping: str
    accession_id: Optional[str] = ""
    cell_barcodes: Optional[List[str]] = None # mandatory for cell types
    parent_node_name: Optional[str] = ""
    synonyms: Optional[List[str]] = None
    label_transfer_object: Optional[LabelTransfer] = None
    evidence_markers: Optional[List[str]] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class CellTypeAnnotation:

    data_url: str
    annotation_objects: List[AnnotationObject]
    taxonomy: TaxonomyMetadata = None

    def add_annotation_object(self, obj):
        """
        Adds given object to annotation objects list
        :param obj: Annotation object to add
        """
        self.annotation_objects.append(obj)


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

    cta = CellTypeAnnotation("my_data_url", list(), get_taxonomy_metadata(config))
    headers, records = read_tsv_to_dict(data_file, generated_ids=True)

    # config_fields = config["fields"]
    # for record in records:
    #     ao = AnnotationObject("", "", "")
    #     cta.add_annotation_object(ao)

    print(cta.to_json())

    return ""


def get_taxonomy_metadata(config):
    taxonomy_metadata = TaxonomyMetadata(config.get("taxonomy_id"),
                                         config.get("species_ids"),
                                         config.get("species_names"),
                                         config.get("brain_region_ids"),
                                         config.get("brain_region_names")
                                         )

    return taxonomy_metadata
