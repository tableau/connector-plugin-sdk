import sys
from pathlib import Path
from xmlschema import XMLSchema
from xmlschema.validators.exceptions import XMLSchemaValidationError

from .connector_file import ConnectorFile


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


def validate_xsd(files_list, folder_path):
    """"[summary]

    Arguments:
        files_list {list[ConnectorFile]} -- List of files to validate
        folder_path {Path} -- path to folder that contains the files

    Returns:
        bool -- True if all xml files pass validation,false if they do not or there is an error

    Assumes the file_list and folder_path are correct, and do not point to files that don't exist or directories
    """

    print("Starting XSD validation...")

    if type(files_list) != list:
        print("Error: validate_xsd: input is not a list")
        return False

    if len(files_list) < 1:
        print("Error: validate_xsd: input list is empty")
        return False

    xml_violations_found = 0
    xml_violations_buffer = ["XML violations found.\n\n"]
    # If xml violations are found, we save them here and print at end of method

    for file_to_test in files_list:
        path_to_file = folder_path / file_to_test.file_name

        # if the extension is not an xml file, we don't need to validate it
        if file_to_test.extension() not in VALID_XML_EXTENSIONS:
            continue

        if validate_single_file(file_to_test, path_to_file, xml_violations_buffer):
            print("XML validation successful")
        else:
            xml_violations_found+=1

    if xml_violations_found <= 0:
        print("No XML violations found")
    else:        
        for line in xml_violations_buffer:
            print(line)

        print("XML validation failed!\n" + str(xml_violations_found) + " violations found.")

    print(str(len(files_list)) + " xml files parsed.")

    return xml_violations_found <= 0

def validate_single_file(file_to_test, path_to_file, xml_violations_buffer):
    """[summary]

    Arguments:
        file_to_test {ConnectorFile} -- path to a single file to test
        path_to_file {Path} -- path to the file
        xml_violations_buffer {list[str]} -- a list of strings that holds the xml violation messages

    Returns:
        bool -- True if the xml file passes validation, false if it does not or there is an error
        Any xml violation messages will be appended to xml_violations_buffer
    """
    
    print("Validating " + str(path_to_file))

    xsd_file = get_xsd_file(file_to_test)

    if not xsd_file:
        xml_violations_buffer.append("Error: No valid XSD for file type:" + file_to_test.file_type)
        return False

    manifest_schema = XMLSchema(str(PATH_TO_XSD_FILES / Path(xsd_file)))
    saved_error = None

    # If the file is too big, we shouldn't try and parse it, just log the violation and move on
    if path_to_file.stat().st_size > MAX_FILE_SIZE:
        xml_violations_buffer.append(file_to_test.file_name + " exceeds maximum size of " + str(int(MAX_FILE_SIZE / 1024)) + " KB")
        return False

    # Try to validate the xml. If the xml validation error is thrown, save the violation information to the buffer
    try:
        manifest_schema.validate(str(path_to_file))
    except XMLSchemaValidationError:
        saved_error = sys.exc_info()[1]
        xml_violations_buffer.append("File: " + file_to_test.file_name + "\n" + str(saved_error))
        print("Validation failed.")
        return False

    return True


# Return the XSD file to test against
def get_xsd_file(file_to_test):
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


# Pass in a folder to test. Calls the file list generator and validates the xml files against the XSDs.
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Too few arguments. You must pass in the path to a folder containing the xml files.")
        sys.exit()

    folder_to_test = Path(sys.argv[1])

    if not folder_to_test.is_dir():
        print("Error: " + str(folder_to_test) + " does not exist or is not a directory")
        sys.exit()

    # TODO: Once the plugin files list generator is completed, remove the ugly hardcoded list
    files_list = [
        ConnectorFile("manifest.xml", "manifest"),
        ConnectorFile("connection-dialog.tcd", "connection-dialog"),
        ConnectorFile("connectionBuilder.js", "script"),
        ConnectorFile("dialect.tdd", "dialect"),
        ConnectorFile("connectionResolver.tdr", "connection-resolver")]

    validate_xsd(files_list, folder_to_test)
