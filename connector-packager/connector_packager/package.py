import argparse
import logging
import os
import sys

from argparse import ArgumentParser

from pathlib import Path

from .connector_properties import ConnectorProperties
from .jar_jdk_packager import jdk_create_jar
from .xsd_validator import validate_all_xml
from .xml_parser import XMLParser
from .version import __version__

PACKAGED_EXTENSION = ".taco"


class UniqueActionStore(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        if getattr(namespace, self.dest, self.default) is not self.default:
            parser.error(option_string + " appears > 1 times.")
        setattr(namespace, self.dest, values)


def create_arg_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Tableau Connector Packaging Tool: package and sign connector files into a single Tableau Connector (" + PACKAGED_EXTENSION + ") file.")  # noqa: E501
    parser.add_argument('input_dir', help='path to directory of connector files to package and sign')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose output', required=False)
    parser.add_argument('-l', '--log', dest='log_path', help='Path to directory for log output. Logs are saved in the file packaging_logs.txt. Default is the current working directory.',
                        default=os.getcwd())
    parser.add_argument('--validate-only', dest='validate_only', action='store_true',
                        help='runs package validation steps only', required=False)
    parser.add_argument('--backwards-compatible', dest='backwards_compatible', action='store_true',
                        help='forgives some validation errors to package connectors made with older versions of the SDK', required=False)
    parser.add_argument('-d', '--dest', dest='dest', help='destination folder for packaged connector',
                        default='packaged-connector', action=UniqueActionStore)
    parser.add_argument('--force-package', dest='force_package', action='store_true', help='Forces packager to package even if validation fails. Warning: may produce non-functional .taco files, and packaging process may fail.', required=False)
    return parser


def init_logging(log_path: Path, verbose: bool = False) -> logging.Logger:
    # Create logger.
    logger = logging.getLogger('packager_logger')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    fh = logging.FileHandler(log_path, mode='w')
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] | %(message)s')
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    if verbose:
        # Log to console also.
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)

    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.debug("Starting Tableau Connector Packaging Version " + __version__)

    return logger


def log_path_checker(path_to_logs: str) -> Path:
    proper_path = Path(path_to_logs)
    if proper_path.exists():
        print("The log path {} exists".format(str(proper_path)))
    else:
        print("The specified log path does not exist - attempting to create {}".format(proper_path))
        try:
            proper_path.mkdir()
            logging.info("Created {}".format(proper_path))
        except Exception:
            print("Unable to create log directory. Exiting.")
            sys.exit(-1)
    return proper_path / 'packaging_logs.txt'


def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    log_file = log_path_checker(args.log_path)
    logger = init_logging(log_file, args.verbose)

    path_from_args = Path(args.input_dir)

    xmlparser = XMLParser(path_from_args)
    files_to_package = xmlparser.generate_file_list()  # validates XSD's as well

    # Validate xml. If not valid, return.
    properties = ConnectorProperties()
    properties.backwards_compatibility_mode = args.backwards_compatible
    if files_to_package and validate_all_xml(files_to_package, path_from_args, properties):
        logger.info("Validation succeeded.\n")
    else:
        logger.info("Validation failed. Check " + str(log_file) + " for more information.")

        if args.force_package:
            logger.warning("--force-package detected, so attempting to package .taco file despite validation failing. Connector may be non-functional or contain bugs, and packaging process may fail.")
        else:
            return

    # Display warning that vendor-defined attributes will be logged
    if len(properties.vendor_defined_fields) > 0:
        logger.info("Detected vendor-defined fields:")
        logger.info(properties.vendor_defined_fields)
        logger.info("Vendor-defined fields will be logged and persisted to Tableau workbook xml in plain text. You must" +
                    " confirm that the user inputs for fields listed above do not contain PII before distributing this connector to customers.\n")

    # Double check that all files exist
    for f in files_to_package:
        f_full_path = str(Path(path_from_args / f.file_name))

        if not os.path.isfile(f_full_path):
            logger.error("Error: " + f_full_path + "does not exist or is not a file.")
            return

    # Validation is done, so if --validate-only we return before we start packaging
    if args.validate_only:
        return

    package_dest_path = Path(args.dest)
    package_name = xmlparser.class_name + PACKAGED_EXTENSION

    if not jdk_create_jar(path_from_args, files_to_package, package_name, package_dest_path):
        logger.info("Taco packaging failed. Check " + str(log_file) + " for more information.")
        return

    logger.info("\nTaco packaged. To sign taco file, use jarsigner.")


if __name__ == '__main__':
    main()
