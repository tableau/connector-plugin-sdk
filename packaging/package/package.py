import sys
import logging
import argparse
from pathlib import Path

from .connector_file import ConnectorFile
from .jar_packager import create_jar
from .version import __version__
from .xsd_validator import validate_all_xml
from .xml_parser import XMLParser


PACKAGED_EXTENSION = ".taco"


def create_arg_parser():
    parser = argparse.ArgumentParser(description="Tableau Connector Packaging Tool: package connector files into a singe Tableau Connector (" + PACKAGED_EXTENSION + ") file.")
    parser.add_argument('--input_dir', help='path to directory of connector files to package')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose output', required=False)
    parser.add_argument('-l', '--log', dest='log_path', help='path of logging output', default='packaging_log.txt')
    parser.add_argument('--validate_only', dest='validate_only', action='store_true', help='runs package validation steps only', required=False)
    parser.add_argument('-d', '--dest', dest='dest', help='destination folder for packaged connector', default='packaged-connector')
    parser.add_argument('-n', '--name', dest='name', help='name of the packaged connector', required=False)

    return parser


def init_logging(log_path, verbose):
    # Create logger.
    logging.basicConfig(filename=log_path, level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    ch = logging.StreamHandler()
    if verbose:
        # Log to console also.
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    logger.debug("Starting Tableau Connector Packaging Version " + __version__)

    return logger


def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    logger = init_logging(args.log_path, args.verbose)

    path_from_args = Path(args.input_dir)

    xmlparser = XMLParser(path_from_args)
    files_to_package = xmlparser.generate_file_list()  # validates XSD's as well

    if args.validate_only:
        if files_to_package and validate_all_xml(files_to_package, path_from_args):
            logger.info("XML Validation succeeded.")
        else:
            logger.info("XML Validation failed. Check " + args.log_path + " for more information.")
        return

    if not files_to_package:
        logger.info("Packaging failed. Check " + args.log_path + " for more information.")
        return

    package_name = xmlparser.class_name
    if args.name:
        package_name = args.name

    jar_dest_path = Path(args.dest)
    jar_name = package_name + PACKAGED_EXTENSION

    create_jar(path_from_args, files_to_package, jar_name, jar_dest_path)


if __name__ == '__main__':
    main()
