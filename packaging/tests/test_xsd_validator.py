import unittest
from pathlib import Path

from package.xsd_validator import validate_xsd, validate_single_file, get_xsd_file
from package.connector_file import ConnectorFile

XSD_TEST_FOLDER = Path("tests/test_resources/")

class TestXSDValidator(unittest.TestCase):
    
    def test_validate_xsd(self):
        
        test_folder = XSD_TEST_FOLDER / Path("valid_connector")
        
        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.tdd", "dialect"),
            ConnectorFile("connectionResolver.tdr", "connection-resolver"),
            ConnectorFile("resources-en_US.xml", "resource")]
        
        self.assertTrue(validate_xsd(files_list, test_folder), "Valid connector not marked as valid")

        test_folder = XSD_TEST_FOLDER / Path("bad_manifest")

        files_list = [ConnectorFile("manifest.xml", "manifest")]

        self.assertFalse(validate_xsd(files_list, test_folder), "Invalid connector was marked as valid")


    def test_validate_single_file(self):

        test_file = XSD_TEST_FOLDER / Path("valid_connector/manifest.xml")
        file_to_test = ConnectorFile("manifest.xml", "manifest")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer), "Valid XML file not marked as valid")

        test_file = XSD_TEST_FOLDER / Path("bad_manifest/manifest.xml")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer), "Invalid XML file marked as valid")

        test_file = XSD_TEST_FOLDER / Path("big_manifest/manifest.xml")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer), "Big XML file marked as valid")
