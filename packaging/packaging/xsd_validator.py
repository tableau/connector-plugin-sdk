import sys
import xmlschema
from pathlib import Path

from connector_file import ConnectorFile

PATH_TO_XSD_FILES = Path("validation").absolute()
VALID_XML_EXTENSIONS = ['tcd', 'tdr', 'tdd', 'xml'] # These are the file extensions that we will validate

# Holds the mapping between file type and XSD file name
XSD_DICT = {
    "manifest": "connector_plugin_manifest_latest",
    "connection-dialog": "tcd_latest",
    "connection_resolver": "tdr_latest",
    "dialect": "tdd_latest",
    "resource": "connector_plugin_resources_latest"
}

# files_list: List of files to validate
# folder_path: path to folder that contains the files.
# Return value: True if all xml files pass validation, false if they do not or there is an error
def validate_xsd(files_list, folder_path):
    
    print("Starting XSD validation...")

    if type(files_list) != list:
        print("Error: validate_xsd: input is not a list")
        return False
    
    if len(files_list) < 1:
        print("Error: validate_xsd: input list is empty")
        return False

    all_files_valid = True
    xml_violations_buffer = "XML violations found.\n\n" # If xml violations are found, we save them here and print at end of method

    for file_to_test in files_list:
        path_to_file = folder_path / file_to_test.file_name

        # if the extension is not an xml file, we don't need to validate it
        if file_to_test.extension() not in VALID_XML_EXTENSIONS:
            continue
        
        print("Validating " + str(path_to_file))
        
        
        xsd_file = GetXSDFile(file_to_test)
        
        if not xsd_file:
            print("Error: No valid XSD for file type:" + file_to_test.file_type)
            all_files_valid = False
            continue

        manifest_schema = xmlschema.XMLSchema(str(PATH_TO_XSD_FILES / Path(xsd_file)))
        saved_error = None
        
        # Try to validate the xml. If the xml validation error is thrown, save the violation information to the buffer
        try:
            manifest_schema.validate(str(path_to_file))
        except xmlschema.validators.exceptions.XMLSchemaValidationError:
            saved_error = sys.exc_info()[1]
            all_files_valid = False
            xml_violations_buffer += "File: " + str(path_to_file) + "\n" + str(saved_error)
            print("Validation failed.")
        except:
            raise error

    if all_files_valid:
        print("No XSD violations found")
    else:
        print(xml_violations_buffer)
        print("XSD validation failed")

    return all_files_valid

# Return the XSD file to test against
def GetXSDFile(file_to_test):
    xsd_file = XSD_DICT.get(file_to_test.file_type)
    if xsd_file:
        return xsd_file + ".xsd"
    else:
        return None


#For testing, will remove and add unit tests once initial version is done
if __name__ == "__main__":
    hardcoded_plugin_folder = Path("C:/Users/pvanderknyff/Documents/connector-plugins/postgres_odbc")
    #hardcoded_plugin_folder = Path("samples/plugins/postgres_odbc")
    #files_list = [ConnectorFile("manifest.xml", "manifest")]
    files_list = [
        ConnectorFile("manifest.xml", "manifest"),
        ConnectorFile("connection-dialog.tcd", "connection-dialog"),
        ConnectorFile("connectionBuilder.js", "script"),
        ConnectorFile("dialect.tdd", "dialect"),
        ConnectorFile("connection-resolver.tdr", "connection-resolver")]
    validate_xsd(files_list, hardcoded_plugin_folder)