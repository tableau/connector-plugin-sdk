import sys
import logging

from pathlib import Path
from typing import List, Optional

from xmlschema import XMLSchema

from .connector_file import ConnectorFile

logger = logging.getLogger('packager_logger')

MAX_FILE_SIZE = 1024 * 256  # This is based on the max file size we will load on the Tableau side
PATH_TO_XSD_FILES = Path("../validation").absolute()
VALID_XML_EXTENSIONS = ['tcd', 'tdr', 'tdd', 'xml']  # These are the file extensions that we will validate

# Holds the mapping between file type and XSD file name
XSD_DICT = {
    "manifest": "connector_plugin_manifest_latest",
    "connection-dialog": "tcd_latest",
    "connection-resolver": "tdr_latest",
    "dialect": "tdd_latest",
    "resource": "connector_plugin_resources_latest"
}


def validate_all_xml(files_list: List[ConnectorFile], folder_path: Path) -> bool:
    """"
    Arguments:
        files_list {list[ConnectorFile]} -- List of files to validate
        folder_path {Path} -- path to folder that contains the files

    Returns:
        bool -- True if all xml files pass validation,false if they do not or there is an error

    Assumes the file_list and folder_path are correct, and do not point to files that don't exist or directories
    """

    logger.debug("Starting XSD validation...")

    if type(files_list) is not list:
        logger.error("Error: validate_all_xml: input is not a list")
        return False

    if len(files_list) < 1:
        logger.error("Error: validate_all_xml: input list is empty")
        return False

    xml_violations_found = 0
    xml_violations_buffer = ["XML violations found."]
    # If xml violations are found, we save them here and logger.debug at end of method

    for file_to_test in files_list:
        path_to_file = folder_path / file_to_test.file_name

        # if the extension is not an xml file, we don't need to validate it
        if file_to_test.extension() not in VALID_XML_EXTENSIONS:
            continue

        if validate_single_file(file_to_test, path_to_file, xml_violations_buffer):
            logger.debug("XML validation successful")
        else:
            xml_violations_found += 1

    if xml_violations_found <= 0:
        logger.debug("No XML violations found")
    else:
        for line in xml_violations_buffer:
            logger.debug(line)

        logger.error("XML validation failed. " + str(xml_violations_found) + " violations found.")

    logger.debug(str(len(files_list)) + " xml files parsed.")

    return xml_violations_found <= 0


def validate_single_file(file_to_test: ConnectorFile, path_to_file: Path, xml_violations_buffer: List[str]) -> bool:
    """
    Arguments:
        file_to_test {ConnectorFile} -- path to a single file to test
        path_to_file {Path} -- path to the file
        xml_violations_buffer {list[str]} -- a list of strings that holds the xml violation messages

    Returns:
        bool -- True if the xml file passes validation, false if it does not or there is an error
        Any xml violation messages will be appended to xml_violations_buffer
    """

    logger.debug("Validating " + str(path_to_file))

    xsd_file = get_xsd_file(file_to_test)

    if not xsd_file:
        xml_violations_buffer.append("Error: No valid XSD for file type:" + file_to_test.file_type)
        return False

    manifest_schema = XMLSchema(str(PATH_TO_XSD_FILES / Path(xsd_file)))
    saved_error = None

    # If the file is too big, we shouldn't try and parse it, just log the violation and move on
    if path_to_file.stat().st_size > MAX_FILE_SIZE:
        xml_violations_buffer.append(file_to_test.file_name + " exceeds maximum size of " +
                                     str(int(MAX_FILE_SIZE / 1024)) + " KB")
        return False

    # Try to validate the xml. If the xml validation error is thrown, save the violation information to the buffer
    try:
        manifest_schema.validate(str(path_to_file))
    except Exception:
        saved_error_type = sys.exc_info()[0]
        saved_error = sys.exc_info()[1]
        xml_violations_buffer.append("File: " + file_to_test.file_name + " Error Type: " + str(saved_error_type) +
                                     "\n" + str(saved_error))
        logger.error("XML Validation failed for " + file_to_test.file_name)
        return False

    return True


# Return the XSD file to test against
def get_xsd_file(file_to_test: ConnectorFile) -> Optional[str]:
    """
    Arguments:
        file_to_test {ConnectorFile} -- the file we want to find an XSD file for

    Returns:
        str -- the name of the XSD file. Will return None if no XSD file found
    """
    xsd_file = XSD_DICT.get(file_to_test.file_type)
    if xsd_file:
        return xsd_file + ".xsd"
    else:
        return None
