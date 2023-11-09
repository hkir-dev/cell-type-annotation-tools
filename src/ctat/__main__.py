import sys
import argparse
import pathlib
from ctat.cell_type_annotation import format_data
from ctat.schema_validator import validate_file
from ctat.tdt_export import export_cas_data


def main():
    parser = argparse.ArgumentParser(prog="ctat", description='Cell Type Annotation Tools cli interface.')
    subparsers = parser.add_subparsers(help='Available ctat actions', dest='action')

    parser_validate = subparsers.add_parser("validate",
                                            description="The validate parser",
                                            help="The provided YAML/YML configuration file is validated against the Cell Type Annotation Schema.")
    parser_validate.add_argument('-i', '--input', action='store', type=pathlib.Path, required=True)

    parser_ingest = subparsers.add_parser("format", add_help=False,
                                          description="The data formatter parser",
                                          help="Ingests given data into standard cell type annotation data structure using the given configuration.")
    parser_ingest.add_argument('-i', '--input', action='store', type=pathlib.Path, required=True)
    parser_ingest.add_argument('-c', '--config', action='store', type=pathlib.Path, required=True)
    parser_ingest.add_argument('-f', '--format', help="Data format to save. Valid values json/tsv")
    parser_ingest.add_argument('-pu', '--print_undefined', action='store_true', help="Prints null values to the output json if true. Omits otherwise.")
    parser_ingest.add_argument('-o', '--output', action='store', type=pathlib.Path, required=True)

    parser_export = subparsers.add_parser("export", add_help=False,
                                          description="The data exporter parser",
                                          help="Gather data from TDT tables and saves CAS data to the output location.")
    parser_export.add_argument('-o', '--output', action='store', type=pathlib.Path, required=True,
                               help="Output folder path.")

    args = parser.parse_args()

    if args.action == "validate":
        is_valid = validate_file(str(args.input))
        if not is_valid:
            sys.exit(1)
    elif args.action == "format":
        print_undefined = False
        if 'print_undefined' in args and args.print_undefined:
            print_undefined = args.print_undefined
        export_format = "json"
        if 'format' in args and args.format and args.format in ['json', 'tsv']:
            export_format = args.format
        format_data(args.input, args.config, args.output, export_format, print_undefined)
    elif args.action == "export":
        export_cas_data(args.output)


if __name__ == "__main__":
    main()
