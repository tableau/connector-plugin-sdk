import sys
import logging
from pathlib import Path

from .connector_file import ConnectorFile
from .jar_packager import create_jar
from .version import __version__
from .xsd_validator import validate_xsd


LOG_FILE = 'packaging_log.txt'

def create_package_output(path):
    print("create jar package from: " + str(path))


def main():
    # TODO: Handle logger creation in init() function that also handles args like TDVT does
    verbose = False #TODO: Get from args

    #Create logger.
    logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    ch = logging.StreamHandler()
    if verbose:
        #Log to console also.
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.WARNING)
    logger.addHandler(ch)

    logger.debug("Starting Tableau Connector Packaging Version " + __version__)


    # TODO: Replace all hard coded below input when ready.
    path_from_args = Path("..\samples\plugins\postgres_odbc")
    files_to_package = [
        ConnectorFile("manifest.xml", "manifest"),
        ConnectorFile("connection-dialog.tcd", "connection-dialog"),
        ConnectorFile("connectionBuilder.js", "script"),
        ConnectorFile("dialect.tdd", "dialect"),
        ConnectorFile("connectionResolver.tdr", "connection-resolver")]

    if validate_xsd(files_to_package, path_from_args):
        jar_dest_path = Path("jar/")
        jar_name = "postgres_odbc.jar"
        create_jar(path_from_args, files_to_package, jar_name, jar_dest_path)
    else:
        logger.warning("XML Validation failed, connector not packaged. Check " + LOG_FILE + " for more information.")


if __name__ == '__main__':
    main()
