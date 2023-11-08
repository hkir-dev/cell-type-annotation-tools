import os
import dataclasses_json
from pathlib import Path
from typing import List, Optional, Any, get_type_hints
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, DataClassJsonMixin

from ctat.schema_validator import load_config, validate
from ctat.file_utils import read_tsv_to_dict
from ctat.tabular_serializer import serialize_to_tables


exclude_none_values = True


class EncoderMixin(DataClassJsonMixin):

    dataclass_json_config = dataclasses_json.config(
        # letter_case=dataclasses_json.LetterCase.CAMEL,
        undefined=dataclasses_json.Undefined.EXCLUDE,
        exclude=lambda f: exclude_none_values and f is None
    )["dataclasses_json"]


@dataclass
class AutomatedAnnotation(EncoderMixin):

    algorithm_name: str
    """The name of the algorithm used. It MUST be a string of the algorithm's name."""

    algorithm_version: str
    """The version of the algorithm used (if applicable). It MUST be a string of the algorithm's version, which is 
    typically in the format '[MAJOR].[MINOR]', but other versioning systems are permitted (based on the algorithm's 
    versioning)."""

    algorithm_repo_url: str
    """This field denotes the URL of the version control repository associated with the algorithm used (if applicable). 
    It MUST be a string of a valid URL."""

    reference_location: Optional[str]
    """This field denotes a valid URL of the annotated dataset that was the source of annotated reference data. 
    This MUST be a string of a valid URL. The concept of a 'reference' specifically refers to 'annotation transfer' 
    algorithms, whereby a 'reference' dataset is used to transfer cell annotations to the 'query' dataset."""


@dataclass
class Labelset(EncoderMixin):

    name: str
    """name of annotation key"""

    description: Optional[str] = None
    """Some text describing what types of cell annotation this annotation key is used to record"""

    annotation_method: Optional[str] = None
    """The method used for creating the cell annotations. This MUST be one of the following strings: `'algorithmic'`, 
    `'manual'`, or `'both'` """

    automated_annotation: Optional[AutomatedAnnotation] = None
    """A set of fields for recording the details of the automated annotation algorithm used. (Common 'automated 
    annotation methods' would include PopV, Azimuth, CellTypist, scArches, etc.)"""

    rank: Optional[str] = None
    """A number indicating relative granularity with 0 being the most specific.  Use this where a single dataset has 
    multiple keys that are used consistently to record annotations and different levels of granularity."""


@dataclass
class AnnotationTransfer(EncoderMixin):

    transferred_cell_label: Optional[str]
    """Transferred cell label"""

    source_taxonomy: Optional[str]
    """PURL of source taxonomy."""

    source_node_accession: Optional[str]
    """accession of node that label was transferred from"""

    algorithm_name: Optional[str]
    """The name of the algorithm used."""

    comment: Optional[str]
    """Free text comment on annotation transfer"""


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
    A collection of fields recording a cell type/class/state annotation on some set os cells, supporting evidence and
    provenance. As this is intended as a general schema, compulsory fields are kept to a minimum. However, tools using
    this schema are encouarged to specify a larger set of compulsory fields for publication.
    Note: This schema deliberately allows for additional fields in order to support ad hoc user fields, new formal
    schema extensions and project/tool specific metadata.
    """

    labelset: str
    """The unique name of the set of cell annotations. 
    Each cell within the AnnData/Seurat file MUST be associated with a 'cell_label' value in order for this to be a 
    valid 'cellannotation_setname'."""

    cell_label: str
    """This denotes any free-text term which the author uses to label cells."""

    cell_set_accession: Optional[str] = None
    """An identifier that can be used to consistently refer to the set of cells being annotated, even if the 
    cell_label changes."""

    cell_fullname: Optional[str] = None
    """This MUST be the full-length name for the biological entity listed in `cell_label` by the author. (If the value 
    in `cell_label` is the full-length term, this field will contain the same value.) \nNOTE: any reserved word used in 
    the field 'cell_label' MUST match the value of this field."""

    cell_ontology_term_id: Optional[str] = None
    """This MUST be a term from either the Cell Ontology or from some ontology that extends it by classifying cell 
    types under terms from the Cell Ontology e.g. the Provisional Cell Ontology."""

    cell_ontology_term: Optional[str] = None
    """This MUST be the human-readable name assigned to the value of 'cell_ontology_term_id"""

    cell_ids: Optional[List[str]] = None
    """List of cell barcode sequences/UUIDs used to uniquely identify the cells"""

    rationale: Optional[str] = None
    """The free-text rationale which users provide as justification/evidence for their cell annotations. 
    Researchers are encouraged to use this field to cite relevant publications in-line using standard academic 
    citations of the form `(Zheng et al., 2020)` This human-readable free-text MUST be encoded as a single string. 
    All references cited SHOULD be listed using DOIs under rationale_dois. There MUST be a 2000-character limit."""

    rationale_dois: Optional[List[str]] = None
    """A list of valid publication DOIs cited by the author to support or provide justification/evidence/context for 
    'cell_label'."""

    marker_gene_evidence: Optional[List[str]] = None
    """List of gene names explicitly used as evidence for this cell annotation."""

    synonyms: Optional[List[str]] = None
    """This field denotes any free-text term of a biological entity which the author associates as synonymous with the 
    biological entity listed in the field 'cell_label'."""

    # TODO modified: added
    parent_cell_set_name: Optional[str] = None

    # TODO modified: list -> str
    parent_cell_set_accession: Optional[str] = None
    """A list of accessions of cell sets that subsume this cell set. This can be used to compose hierarchies of 
    annotated cell sets, built from a fixed set of clusters."""

    # TODO modified: added
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

    # data_url: str
    # annotation_objects: List[Annotation]
    # taxonomy: TaxonomyMetadata = None

    author_name: str
    """This MUST be a string in the format `[FIRST NAME] [LAST NAME]`"""

    annotations: List[Annotation]
    """A collection of fields recording a cell type/class/state annotation on some set os cells, supporting evidence 
    and provenance. As this is intended as a general schema, compulsory fields are kept to a minimum. However, tools 
    using this schema are encouarged to specify a larger set of compulsory fields for publication."""

    labelsets: Optional[List[Labelset]] = None

    author_contact: Optional[str] = None
    """This MUST be a valid email address of the author"""

    orcid: Optional[str] = None
    """This MUST be a valid ORCID for the author"""

    cellannotation_schema_version: Optional[str] = None
    """The schema version, the cell annotation open standard. Current version MUST follow 0.1.0
    This versioning MUST follow the format `'[MAJOR].[MINOR].[PATCH]'` as defined by Semantic Versioning 2.0.0, 
    https://semver.org/"""

    cellannotation_version: Optional[str] = None
    """The version for all cell annotations published (per dataset). This MUST be a string. The recommended versioning 
    format is `'[MAJOR].[MINOR].[PATCH]'` as defined by Semantic Versioning 2.0.0, https://semver.org/"""

    cellannotation_url: Optional[str] = None
    """A persistent URL of all cell annotations published (per dataset)."""

    transferred_annotations: Optional[AnnotationTransfer] = None

    def add_annotation_object(self, obj):
        """
        Adds given object to annotation objects list
        :param obj: Annotation object to add
        """
        self.annotations.append(obj)


def format_data(data_file: str, config_file: str, out_file: str, format:str="json", print_undefined:bool=False) -> dict:
    """
    Formats given data into standard cell type annotation data structure using the given configuration.

    :param data_file: Unformatted user data in tsv/csv format.
    :param config_file: configuration file path.
    :param out_file: output file path.
    :param format: Data export format. Supported formats are 'json' and 'tsv'
    :param print_undefined: prints null values to the output json if true. Omits undefined values from the json output if
    false. False by default. Only effective in json serialization.
    :return: output data as dict
    """
    cta = ingest_user_data(data_file, config_file)

    if format == "json":
        serialize_to_json(cta, out_file, print_undefined)
    elif format == "tsv":
        table_name_prefix = os.path.splitext(os.path.basename(data_file))[0]
        if os.path.isfile(out_file):
            out_folder = Path(out_file).parent.absolute()
        else:
            out_folder = out_file
        serialize_to_tables(cta, table_name_prefix, out_folder)

    return cta.to_dict()


def ingest_user_data(data_file: str, config_file: str):
    """
    Ingest given user data into standard cell type annotation data structure using the given configuration.
    :param data_file: Unformatted user data in tsv/csv format.
    :param config_file: configuration file path.
    """

    config = load_config(config_file)
    is_config_valid = validate(config)
    if not is_config_valid:
        raise Exception("Configuration file is not valid!")
    cta = CellTypeAnnotation(config["author_name"], list())
    headers, records = read_tsv_to_dict(data_file, generated_ids=True)
    config_fields = config["fields"]
    populate_labelsets(cta, config_fields)
    ao_names = dict()
    utilized_columns = set()
    for record_index in records:
        record = records[record_index]
        ao = Annotation("", "")
        parents = [None] * 10
        for field in config_fields:
            # handle hierarchical columns
            if field["column_type"] == "cluster_name":
                ao.labelset = field["column_name"]
                ao.cell_label = str(record[field["column_name"]])
                utilized_columns.add(field["column_name"])
            elif field["column_type"] == "cluster_id":
                ao.cell_set_accession = str(record[field["column_name"]])
                ao.rank = int(str(field["rank"]).strip())
                utilized_columns.add(field["column_name"])
            elif field["column_type"] == "cell_set":
                parent_ao = Annotation(field["column_name"], record[field["column_name"]])
                parent_ao.rank = int(str(field["rank"]).strip())
                parents.insert(int(str(field["rank"]).strip()), parent_ao)
                utilized_columns.add(field["column_name"])
            else:
                # handle annotation columns
                if "typing.List[str]" in str(get_type_hints(ao)[field["column_type"]]):
                    list_value = str(record[field["column_name"]]).split(',')
                    stripped = list(map(str.strip, list_value))
                    setattr(ao, field["column_type"], stripped)
                else:
                    setattr(ao, field["column_type"], record[field["column_name"]])
                utilized_columns.add(field["column_name"])

        add_user_annotations(ao, headers, record, utilized_columns)
        add_parent_node_names(ao, ao_names, cta, parents)

        ao_names[ao.cell_label] = ao
        cta.add_annotation_object(ao)
    return cta


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


def populate_labelsets(cta, config_fields):
    """
    Populates labelsets list based on the fields of the config.
    :param cta: main object
    :param config_fields: config file fields
    """
    labelsets = list()
    for field in config_fields:
        if field['column_type'] == 'cell_set' or field['column_type'] == 'cluster_name':
            label_set = Labelset(field['column_name'])
            if 'rank' in field:
                label_set.rank = str(field["rank"])
            labelsets.append(label_set)
    if labelsets:
        cta.labelsets = labelsets


def serialize_to_json(cta, out_file, print_undefined=False):
    """
    Writes cell type annotation object to a json file.
    :param cta: cell type annotation object to serialize.
    :param out_file: output file path.
    :param print_undefined: prints null values to the output json if true. Omits undefined values from the json output if
    """
    global exclude_none_values
    exclude_none_values = not print_undefined

    output_data = cta.to_json(indent=2)
    with open(out_file, "w") as out_file:
        out_file.write(output_data)



