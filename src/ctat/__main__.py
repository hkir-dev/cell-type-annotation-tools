import sys
import argparse
import pathlib
from ctat.cell_type_annotation import format_data
from ctat.schema_validator import validate_file


def main():
    parser = argparse.ArgumentParser(prog="ctat", description='Cell Type Annotation Tools cli interface.')
    subparsers = parser.add_subparsers(help='Available ctat actions', dest='action')

    parser_validate = subparsers.add_parser("validate",
                                            description="The validate parser",
                                            help="The provided YAML/YML configuration file is validated against the Cell Type Annotation Schema.")
    parser_validate.add_argument('-i', '--input', action='store', type=pathlib.Path, required=True)

    parser_export = subparsers.add_parser("format", add_help=False,
                                          description="The data formatter parser",
                                          help="Formats given data into standard cell type annotation data structure using the given configuration.")
    parser_export.add_argument('-i', '--input', action='store', type=pathlib.Path, required=True)
    parser_export.add_argument('-c', '--config', action='store', type=pathlib.Path, required=True)
    parser_export.add_argument('-o', '--output', action='store', type=pathlib.Path, required=True)

    args = parser.parse_args()

    if args.action == "validate":
        is_valid = validate_file(str(args.input))
        if not is_valid:
            sys.exit(1)
    elif args.action == "format":
        format_data(args.input, args.config, args.output)


if __name__ == "__main__":
    main()
