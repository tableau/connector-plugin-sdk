import sys
import logging

from pathlib import Path
from typing import List, Optional

from xmlschema import XMLSchema

from defusedxml.ElementTree import parse

from .connector_file import ConnectorFile
from .connector_properties import ConnectorProperties

logger = logging.getLogger('packager_logger')

MAX_FILE_SIZE = 1024 * 256  # This is based on the max file size we will load on the Tableau side
PATH_TO_XSD_FILES = Path("../validation").absolute()
VALID_XML_EXTENSIONS = ['tcd', 'tdr', 'tdd', 'xml']  # These are the file extensions that we will validate
PLATFORM_FIELD_NAMES = ['server', 'port', 'sslmode', 'authentication', 'username', 'password', 'instanceurl', 'vendor1', 'vendor2', 'vendor3']
VENDOR_FIELD_NAMES = ['vendor1', 'vendor2', 'vendor3']
VENDOR_FIELD_NAME_PREFIX = 'v-'

# Holds the mapping between file type and XSD file name
XSD_DICT = {
    "manifest": "connector_plugin_manifest_latest",
    "connection-dialog": "tcd_latest",
    "connection-resolver": "tdr_latest",
    "dialect": "tdd_latest",
    "resource": "connector_plugin_resources_latest",
    "connection-fields": "connection_fields",
    "connection-metadata": "connector_plugin_metadata",
    "oauth-config": "oauth_config"}


def validate_all_xml(files_list: List[ConnectorFile], folder_path: Path, properties: ConnectorProperties) -> bool:
    """"
    Arguments:
        files_list {list[ConnectorFile]} -- List of files to validate
        folder_path {Path} -- path to folder that contains the files
        properties {ConnectorProperties} -- an object contating properties that apply to the entire connector

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

        if validate_single_file(file_to_test, path_to_file, xml_violations_buffer, properties):
            logger.debug("XML validation successful")
        else:
            xml_violations_found += 1

        warn_file_specific_rules(file_to_test, path_to_file)

    if xml_violations_found <= 0:
        logger.debug("No XML violations found")
    else:
        for line in xml_violations_buffer:
            logger.debug(line)

        logger.error("XML validation failed. " + str(xml_violations_found) + " violations found.")

    logger.debug(str(len(files_list)) + " xml files parsed.")

    return xml_violations_found <= 0


def validate_single_file(file_to_test: ConnectorFile, path_to_file: Path, xml_violations_buffer: List[str], properties: ConnectorProperties) -> bool:
    """
    Arguments:
        file_to_test {ConnectorFile} -- path to a single file to test
        path_to_file {Path} -- path to the file
        xml_violations_buffer {list[str]} -- a list of strings that holds the xml violation messages
        properties {ConnectorProperties} -- an object contating properties that apply to the entire connector

    Returns:
        bool -- True if the xml file passes validation, false if it does not or there is an error
        Any xml violation messages will be appended to xml_violations_buffer
    """
    logger.debug("Validating " + str(path_to_file))

    if file_to_test.file_type == 'connection-dialog':
        properties.uses_tcd = True

    xsd_file = get_xsd_file(file_to_test)

    if not xsd_file:
        xml_violations_buffer.append("Error: No valid XSD for file type:" + file_to_test.file_type)
        return False

    manifest_schema = XMLSchema(str(PATH_TO_XSD_FILES / Path(xsd_file)))

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

    if not validate_file_specific_rules(file_to_test, path_to_file, xml_violations_buffer, properties):
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


def validate_file_specific_rules(file_to_test: ConnectorFile, path_to_file: Path, xml_violations_buffer: List[str], properties: ConnectorProperties) -> bool:
    """
    Arguments:
        file_to_test {ConnectorFile} -- the file we want to validate
        path_to_file {Path} -- the path to the file we want to validate
        xml_violations_buffer {list[str]} -- a list of strings that holds the xml violation messages
        properties {ConnectorProperties} -- an object contating properties that apply to the entire connector

    Returns:
        bool -- True if the file passes all the file specific rules, otherwise false
        Any rule violation messages will be appended to xml_violations_buffer
    """

    if file_to_test.file_type == 'manifest':
        return validate_file_specific_rules_manifest(file_to_test, path_to_file, properties)
    elif file_to_test.file_type == 'connection-fields':
        return validate_file_specific_rules_connection_fields(file_to_test, path_to_file, xml_violations_buffer, properties)
    elif file_to_test.file_type == 'connection-metadata':
        return validate_file_specific_rules_connection_metadata(file_to_test, path_to_file, properties)
    elif file_to_test.file_type == 'connection-resolver':
        return validate_file_specific_rules_tdr(file_to_test, path_to_file, xml_violations_buffer, properties)
    elif file_to_test.file_type == 'connection-dialog':
        return validate_file_specific_rules_tcd(file_to_test, path_to_file, xml_violations_buffer, properties)

    return True


def validate_file_specific_rules_manifest(file_to_test: ConnectorFile, path_to_file: Path, properties: ConnectorProperties) -> bool:
    xml_tree = parse(str(path_to_file))
    root = xml_tree.getroot()

    if 'superclass' in root.attrib:
        # other superclasses could be jdbc-based, but this will catch the common case
        if 'jdbc' == root.attrib['superclass']:
            properties.is_jdbc = True

    return True


def validate_file_specific_rules_connection_fields(file_to_test: ConnectorFile, path_to_file: Path, xml_violations_buffer: List[str],  properties: ConnectorProperties) -> bool:
    field_names = set()
    xml_tree = parse(str(path_to_file))
    root = xml_tree.getroot()

    for child in root.iter('field'):
        if 'name' in child.attrib:
            field_name = child.attrib['name']
            properties.connection_fields.append(field_name)

            if field_name in VENDOR_FIELD_NAMES or field_name.startswith(VENDOR_FIELD_NAME_PREFIX):
                properties.vendor_defined_fields.append(field_name)

            if not (field_name in PLATFORM_FIELD_NAMES or field_name.startswith(VENDOR_FIELD_NAME_PREFIX)):
                xml_violations_buffer.append("Element 'field', attribute 'name'='" + field_name +
                                                "' not an allowed value. See 'Connection Field Platform Integration' section of documentation for allowed values.")
                return False
            if field_name in field_names:
                xml_violations_buffer.append("A field with the field name = " + field_name +
                                                " already exists. Cannot have multiple fields with the same name.")
                                                
                return False
            if field_name == 'instanceurl':
                used_for_oauth = False
                for conditions in child.iter("conditions"):
                    for condition in conditions.iter("condition"):
                        if 'field' in condition.attrib:
                            if condition.attrib['field'] == 'authentication':
                                if 'value' in condition.attrib:
                                    if condition.attrib['value'] == 'oauth':
                                        used_for_oauth = True
                if not used_for_oauth:
                    xml_violations_buffer.append("Element 'field', attribute 'name'='instanceurl' can only be used conditional on field " +
                                                    "'authentication' with 'value'='oauth'. See 'Connection Field Platform Integration' section " +
                                                    "of documentation for more information.")
                    return False

            field_names.add(field_name)

        if 'category' in child.attrib:
            category = child.attrib['category']
            optional = child.attrib.get('optional','true') == 'true'
            default_present = child.attrib.get('default-value','') != ''
            if category == 'advanced' and not optional and not default_present:
                xml_violations_buffer.append("Element 'field', attribute 'name'='" + field_name +
                                                "': Required fields in the Advanced category must be assigned a default value.")
                return False

    # Check that "authentication" is listed as a connection field
    if 'authentication' not in properties.connection_fields:

        if properties.backwards_compatibility_mode:
            logger.warning("No authentication field present in " + file_to_test.file_name + ". Still packaging connector because of backwards compatibility mode.")
        else:
            xml_violations_buffer.append("No authentication field present in " + file_to_test.file_name)
            return False

    return True


def validate_file_specific_rules_connection_metadata(file_to_test: ConnectorFile, path_to_file: Path, properties: ConnectorProperties) -> bool:
    xml_tree = parse(str(path_to_file))
    root = xml_tree.getroot()

    # connection-metadata file and database element are both optional, on by default
    for database in root.iter('database'):
        if 'enabled' in database.attrib:
            if 'true' != database.attrib['enabled']:
                properties.connection_metadata_database = False

    return True


def validate_file_specific_rules_tdr(file_to_test: ConnectorFile, path_to_file: Path, xml_violations_buffer: List[str], properties: ConnectorProperties) -> bool:

    xml_tree = parse(str(path_to_file))
    root = xml_tree.getroot()
    attribute_list = root.find('.//connection-normalizer/required-attributes/attribute-list')

    # The connection resolver appears after the dialog elements in the manifest's xml, so we know
    # USES_TCD is accurate here
    if not attribute_list and properties.uses_tcd:
        xml_violations_buffer.append("Connectors using a .tcd file cannot use inferred connection resolver,"
                                     "must manually populate required-attributes/attributes-list in "
                                     + str(path_to_file) + ".")
        return False

    # Check that all the connection-fields attributes are in the required attributes
    if properties.connection_fields and attribute_list:
        attributes = []
        for attr in attribute_list.iter():
            attributes.append(attr.text)

        if len(attributes) > 0 and properties.connection_fields:
            for field in properties.connection_fields:
                if field == 'instanceurl':
                    continue
                if field not in attributes:
                    xml_violations_buffer.append("Attribute '" + field + "' in connection-fields but not in required-attributes list.")
                    return False
                    
        if len(attributes) > 0 and properties.connection_metadata_database and not properties.uses_tcd:
            if 'dbname' not in attributes:
                logger.warning("Warning: connection-metadata 'database' enabled but 'dbname' is not in required-attributes list. Consider adding it if the value is used in connection-builder or connection-properties scripts")

        


    properties_builder = root.find('.//connection-properties')

    if not properties_builder and properties.is_jdbc:
        xml_violations_buffer.append("Connectors using a 'jdbc' superclass must declare a <connection-properties> element in " +
                                     str(path_to_file) + ".")
        return False

    return True

def validate_file_specific_rules_tcd(file_to_test: ConnectorFile, path_to_file: Path, xml_violations_buffer: List[str], properties: ConnectorProperties) -> bool:

    xml_tree = parse(str(path_to_file))
    root = xml_tree.getroot()

    # Check to see if we're using the vendor-defined fields (vendor1, etc), add them to the vendor_defined_fields list
    vendor1 = root.find('.//connection-config/vendor1-prompt')
    if vendor1 is not None:
        properties.vendor_defined_fields.append('vendor1')
    vendor2 = root.find('.//connection-config/vendor2-prompt')
    if vendor2 is not None:
        properties.vendor_defined_fields.append('vendor2')
    vendor3 = root.find('.//connection-config/vendor3-prompt')
    if vendor3 is not None:
        properties.vendor_defined_fields.append('vendor3')

    return True

# Check if connector file content contains warnings needs to notify connector developer
def warn_file_specific_rules(file_to_test: ConnectorFile, path_to_file: Path):

    if file_to_test.file_type == 'dialect':
        warn_file_specific_rules_dialect(path_to_file)
    elif file_to_test.file_type == 'connection-resolver':
        warn_file_specific_rules_tdr(path_to_file)


def warn_file_specific_rules_dialect(path_to_file: Path):

    xml_tree = parse(str(path_to_file))
    root = xml_tree.getroot()
    if 'base' in root.attrib and root.attrib['base'] == 'DefaultSQLDialect':
        logger.warning('Warning: DefaultSQLDialect is not a recommended base to inherit from, '
                       'please see the documentation for current best practices: '
                       'https://tableau.github.io/connector-plugin-sdk/docs/design#choose-a-dialect')


def warn_file_specific_rules_tdr(path_to_file: Path):

    xml_tree = parse(str(path_to_file))
    root = xml_tree.getroot()
    attribute_list = root.find('.//connection-normalizer/required-attributes/attribute-list')

    if not attribute_list:
        return

    authentication_attr_exists = False
    server_attr_exists = False
    for attr in attribute_list.iter('attr'):
        if attr.text == 'authentication':
            authentication_attr_exists = True

        if attr.text == 'server':
            server_attr_exists = True
            
    if not authentication_attr_exists:
        logger.warning("Warning: 'authentication' attribute is missing from "
                       "<connection-normalizer>/<required-attributes>/<attribute-list> in " + str(path_to_file) + ".")

    if not server_attr_exists:
            logger.warning("Warning: 'server' attribute is missing from "
                        "<connection-normalizer>/<required-attributes>/<attribute-list> in " + str(path_to_file) + ".")
