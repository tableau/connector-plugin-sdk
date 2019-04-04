import sys
import logging
import argparse
from pathlib import Path

from .connector_file import ConnectorFile
from .jar_packager import create_jar
from .version import __version__
from .xsd_validator import validate_xsd
from .file_list_generator import generate_file_list


LOG_FILE = 'packaging_log.txt'
PACKAGED_EXTENSION = ".tcnx"

def create_parser():
    parser = argparse.ArgumentParser(description="Tableau Connector Packaging Tool", usage="Package files into a single Tableau Connector file.")
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true', help='Verbose output.', required=False)
    parser.add_argument('--package', dest='package', help='Packages files in the folder path provided', required=False)
    parser.add_argument('--validate', dest='validate', help='Validates xml files in the folder path provided', required=False)
    parser.add_argument('--dest', '-d', dest='dest', help='Destination folder for packaged connector', required=False)
    parser.add_argument('--name', '-n', dest='name', help='Name of the packaged connector', required=False)

    return parser

def init():
    parser = create_parser()
    args = parser.parse_args()

    #Create logger.
    logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    ch = logging.StreamHandler()
    if args.verbose:
        #Log to console also.
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    logger.debug("Starting Tableau Connector Packaging Version " + __version__)

    return parser, args, logger



def main():
    parser, args, logger = init()

    # TODO: Actually generate these
    files_to_package = [
        ConnectorFile("manifest.xml", "manifest"),
        ConnectorFile("connection-dialog.tcd", "connection-dialog"),
        ConnectorFile("connectionBuilder.js", "script"),
        ConnectorFile("dialect.tdd", "dialect"),
        ConnectorFile("connectionResolver.tdr", "connection-resolver")]
    
    if args.package:
        if not args.name:
            logger.warning("Error: no name specified for packaged connector. Use --name or -n command line arguments.")   
            return
        
        path_from_args = Path(args.package)

        files_to_package = generate_file_list(path_from_args)

        if files_to_package and validate_xsd(files_to_package, path_from_args):
            
            jar_dest_path = Path("jar/")
            jar_name = args.name + PACKAGED_EXTENSION

            if args.dest:
                jar_dest_path = args.dest

            create_jar(path_from_args, files_to_package, jar_name, jar_dest_path)
        else:
            logger.info("Packaging failed. Check " + LOG_FILE + " for more information.")

    elif args.validate:
        path_from_args = Path(args.validate)  

        files_to_package = generate_file_list(path_from_args)
        
        if files_to_package and validate_xsd(files_to_package, path_from_args):
            logger.info("XML Validation succeeded.")
        else:
            logger.info("XML Validation failed. Check " + LOG_FILE + " for more information.")

    # if we reach here we didn't get an arg to do stuff, so print help before exiting
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
