import os

from argparse import ArgumentParser

from pathlib import Path

from .helper import init_logging
from .jar_jdk_packager import jdk_create_jar
from .jar_jdk_signer import validate_signing_input
from .jar_jdk_signer import jdk_sign_jar
from .xsd_validator import validate_all_xml
from .xml_parser import XMLParser

PACKAGED_EXTENSION = ".taco"


def create_arg_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Tableau Connector Packaging Tool: package and sign connector files into a single Tableau Connector (" + PACKAGED_EXTENSION + ") file.")  # noqa: E501
    parser.add_argument('input_dir', help='path to directory of connector files to package and sign')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='verbose output', required=False)
    parser.add_argument('-l', '--log', dest='log_path', help='path to directory for logging output',
                        default=os.getcwd())
    parser.add_argument('--validate-only', dest='validate_only', action='store_true',
                        help='runs package validation steps only', required=False)
    parser.add_argument('-d', '--dest', dest='dest', help='destination folder for packaged connector',
                        default='packaged-connector')
    parser.add_argument('--package-only', dest='package_only', action='store_true',
                        help='package a taco only, skip signing', required=False)
    parser.add_argument('-a', '--alias', dest='alias',
                        help='alias identifying the private key to be used to sign taco file', required=False)
    parser.add_argument('-ks', '--keystore', dest='keystore',
                        help='keystore location, default is the jks file in user home directory', required=False)
    return parser


def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    log_file = args.log_path + '/packaging_log.txt'
    logger = init_logging(log_file, args.verbose)

    path_from_args = Path(args.input_dir)

    xmlparser = XMLParser(path_from_args)
    files_to_package = xmlparser.generate_file_list()  # validates XSD's as well

    if args.validate_only:
        if args.package_only:
            logger.warning("Because the validate-only flag was used, files will not be packaged.")
        if files_to_package and validate_all_xml(files_to_package, path_from_args):
            logger.info("XML Validation succeeded.")
        else:
            logger.info("XML Validation failed. Check " + log_file + " for more information.")
        return

    if not files_to_package:
        logger.info("Packaging failed. Check " + log_file + " for more information.")
        return

    package_dest_path = Path(args.dest)
    package_name = xmlparser.class_name + PACKAGED_EXTENSION

    if not jdk_create_jar(path_from_args, files_to_package, package_name, package_dest_path):
        logger.info("Taco packaging failed. Check " + log_file + " for more information.")
        return

    if args.package_only:
        logger.info("Taco packaging finished completely, signing skipped")
        return

    alias_from_args = args.alias
    keystore_from_args = args.keystore

    if not validate_signing_input(package_dest_path, package_name, alias_from_args, keystore_from_args):
        logger.debug("Signing input validation failed. check " + log_file + " for more information.")
        return

    if not jdk_sign_jar(package_dest_path, package_name, alias_from_args, keystore_from_args):
        logger.info("Signing failed. check console output and " + log_file + " for more information.")
        return


if __name__ == '__main__':
    main()
