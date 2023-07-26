import dataclasses_json
from typing import List, Optional, Any
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, DataClassJsonMixin

from ctat.schema_validator import load_config, validate
from ctat.file_utils import read_tsv_to_dict


class EncoderMixin(DataClassJsonMixin):
    dataclass_json_config = dataclasses_json.config(
        # letter_case=dataclasses_json.LetterCase.CAMEL,
        undefined=dataclasses_json.Undefined.EXCLUDE,
        exclude=lambda f: f is None
    )["dataclasses_json"]


@dataclass
class TaxonomyMetadata(EncoderMixin):

    taxonomy_id: Optional[str] = ""
    species_ids: Optional[str] = ""
    species_names: Optional[str] = ""
    brain_region_ids: Optional[str] = ""
    brain_region_names: Optional[str] = ""


@dataclass
class AnnotationTransfer(EncoderMixin):

    transferred_label: str
    source_taxonomy: TaxonomyMetadata
    source_taxonomy_cell_set_accession: str
    algorithm_name: Optional[str]
    """The name of the algorithm used."""


@dataclass
class UserAnnotation(EncoderMixin):
    """User defined custom annotations which are not part of the standard schema."""

    annotation_set: str
    """The unique name of the set of cell annotations associated with a single file."""

    cell_label: Any
    """This denotes any free-text term which the author uses to label cells."""


@dataclass
class Annotation(EncoderMixin):
    """
    A collection of fields recording a cell type/class/state annotation on some set os cells, supporting evidence and provenance.
    """

    annotation_set: str
    """The unique name of the set of cell annotations associated with a single file."""

    cell_label: str
    """This denotes any free-text term which the author uses to label cells."""

    rank: Optional[int] = 0

    cell_ontology_term_id: Optional[str] = None
    """This MUST be a term from either the Cell Ontology or from some ontology that extends it by classifying cell 
    types under terms from the Cell Ontology e.g. the Provisional Cell Ontology."""

    cell_ontology_term: Optional[str] = None
    """This MUST be the human-readable name assigned to the value of 'cell_ontology_term_id"""

    cell_set_accession: Optional[str] = None

    cell_ids: Optional[List[str]] = None  # mandatory for cell types
    """List of cell barcode sequences/UUIDs used to uniquely identify the cells"""

    parent_cell_set_name: Optional[str] = None

    synonyms: Optional[List[str]] = None
    """This field denotes any free-text term of a biological entity which the author associates as synonymous with the 
    biological entity listed in the field 'cell_label'."""

    annotation_transfer: Optional[AnnotationTransfer] = None

    marker_genes: Optional[List[str]] = None
    """List of gene names explicitly used as evidence for this cell annotation."""

    user_annotations: Optional[List[UserAnnotation]] = None

    def add_user_annotation(self, user_annotation_set, user_annotation_label):
        """
        Adds a user defined annotation which is not supported by the standard schema.
        :param user_annotation_set: name of the user annotation set
        :param user_annotation_label: label of the user annotation set
        """
        if not self.user_annotations:
            self.user_annotations = list()
        self.user_annotations.append(UserAnnotation(user_annotation_set, user_annotation_label))


@dataclass
class CellTypeAnnotation(EncoderMixin):

    data_url: str
    annotation_objects: List[Annotation]
    taxonomy: TaxonomyMetadata = None

    def add_annotation_object(self, obj):
        """
        Adds given object to annotation objects list
        :param obj: Annotation object to add
        """
        self.annotation_objects.append(obj)


def format_data(data_file: str, config_file: str, out_file: str) -> dict:
    """
    Formats given data into standard cell type annotation data structure using the given configuration.

    :param data_file: Unformatted user data in tsv/csv format.
    :param config_file: configuration file path.
    :param out_file: output file path.
    :return: output data as dict
    """
    config = load_config(config_file)
    is_config_valid = validate(config)
    if not is_config_valid:
        raise Exception("Configuration file is not valid!")

    cta = CellTypeAnnotation("my_data_url", list(), get_taxonomy_metadata(config))
    headers, records = read_tsv_to_dict(data_file, generated_ids=True)

    config_fields = config["fields"]

    ao_names = dict()
    utilized_columns = set()
    for record_index in records:
        record = records[record_index]
        ao = Annotation("", "")
        parents = [None] * 10
        for field in config_fields:
            # handle hierarchical columns
            if field["column_type"] == "cluster_name":
                ao.annotation_set = field["column_name"]
                ao.cell_label = str(record[field["column_name"]])
                utilized_columns.add(field["column_name"])
            if field["column_type"] == "cluster_id":
                ao.cell_set_accession = str(record[field["column_name"]])
                ao.rank = int(str(field["rank"]).strip())
                utilized_columns.add(field["column_name"])
            if field["column_type"] == "cell_set":
                parent_ao = Annotation(field["column_name"], record[field["column_name"]])
                parent_ao.rank = int(str(field["rank"]).strip())
                parents.insert(int(str(field["rank"]).strip()), parent_ao)
                utilized_columns.add(field["column_name"])
            else:
                # handle annotation columns
                setattr(ao, field["column_type"], record[field["column_name"]])
                utilized_columns.add(field["column_name"])

        add_user_annotations(ao, headers, record, utilized_columns)
        add_parent_node_names(ao, ao_names, cta, parents)

        ao_names[ao.cell_label] = ao
        cta.add_annotation_object(ao)

    output_data = cta.to_json(indent=2)
    with open(out_file, "w") as out_file:
        out_file.write(output_data)

    return cta.to_dict()


def add_user_annotations(ao, headers, record, utilized_columns):
    """
    Adds user annotations that are not supported by the standard schema.
    :param ao: current annotation object
    :param headers: all column names of the user data
    :param record: a record in the user data
    :param utilized_columns: list of processed columns
    """
    not_utilized_columns = [column_name for column_name in headers if column_name not in utilized_columns]
    for not_utilized_column in not_utilized_columns:
        if record[not_utilized_column]:
            ao.add_user_annotation(not_utilized_column, record[not_utilized_column])


def add_parent_node_names(ao, ao_names, cta, parents):
    """
    Creates parent nodes if necessary and creates a cluster hierarchy through assinging parent_node_names.
    :param ao: current annotation object
    :param ao_names: list of all created annotation objects
    :param cta: main object
    :param parents: list of current annotation object's parents
    """
    if parents:
        ao.parent_cell_set_name = parents[1].cell_label
        prev = None
        for parent in reversed(parents):
            if parent:
                if prev:
                    parent.parent_cell_set_name = prev.cell_label
                prev = parent
                if parent.cell_label not in ao_names:
                    cta.add_annotation_object(parent)
                    ao_names[parent.cell_label] = parent


def get_taxonomy_metadata(config):
    taxonomy_metadata = TaxonomyMetadata(config.get("taxonomy_id"),
                                         config.get("species_ids"),
                                         config.get("species_names"),
                                         config.get("brain_region_ids"),
                                         config.get("brain_region_names")
                                         )

    return taxonomy_metadata
