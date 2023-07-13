# Cell Type Annotation Tools

This repository provides schema of the cell type annotation and related data standardization operations.

## Installation

Install the latest [pypi package](https://test.pypi.org/project/ctat/) through following the instructions in the pypi page.

## Configuration Spec

Configuration spec defines schema for the CTA data conversion config files. Latest schema is located at: [ctat_schema.yaml](src/schema/ctat_schema.yaml)

## Operations

Cell Type Annotation Tool provides the following operations:

### Validate

The provided YAML/YML configuration file is validated against the Cell Type Annotation Schema.

```
ctat validate -i /path/to/my_config.yaml
```

If config is valid, program exits with system code 0, otherwise logs the issues and exits with a non-zero code.

### Format

Formats the given data into standard cell type annotation data structure using the given configuration. Output is persisted as a json file.

```
ctat format -i /path/to/my_data.tsv -c /path/to/my_config.yaml -o /path/to/output.json
```

Fields that are not mapped in the config file are stored as `userAnnotations`.

A sample configuration file can be found at [test_config.yaml](src/test/test_data/test_config.yaml). After applying this config to [the user data](src/test/test_data/AIT115_annotation_sheet.tsv), sample output file can be found at [test_result.json](src/test/test_data/test_result.json).