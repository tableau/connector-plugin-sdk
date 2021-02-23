import unittest
import logging
from pathlib import Path

from connector_packager.xsd_validator import validate_all_xml, validate_single_file
from connector_packager.connector_file import ConnectorFile

logger = logging.getLogger(__name__)

TEST_FOLDER = Path("tests/test_resources")


class TestXSDValidator(unittest.TestCase):

    def test_validate_all_xml(self):

        test_folder = TEST_FOLDER / Path("valid_connector")

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.tdd", "dialect"),
            ConnectorFile("connectionResolver.tdr", "connection-resolver"),
            ConnectorFile("resources-en_US.xml", "resource")]

        self.assertTrue(validate_all_xml(files_list, test_folder), "Valid connector not marked as valid")

        print("\nTest broken xml. Throws a XML validation error.")
        test_folder = TEST_FOLDER / Path("broken_xml")

        files_list = [ConnectorFile("manifest.xml", "manifest")]

        self.assertFalse(validate_all_xml(files_list, test_folder), "Invalid connector was marked as valid")

        test_folder = TEST_FOLDER / Path("broken_xml")

    def test_validate_single_file(self):

        test_file = TEST_FOLDER / Path("valid_connector/manifest.xml")
        file_to_test = ConnectorFile("manifest.xml", "manifest")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                        "Valid XML file not marked as valid")

        test_file = TEST_FOLDER / Path("big_manifest/manifest.xml")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                         "Big XML file marked as valid")

        print("\nTest broken xml. Throws XML validation error.")
        test_file = TEST_FOLDER / Path("broken_xml/manifest.xml")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                         "XML file that doesn't follow schema marked as valid")

        print("\nTest malformed xml. Throws XML validation error.")
        test_file = TEST_FOLDER / Path("broken_xml/connectionResolver.tdr")
        file_to_test = ConnectorFile("connectionResolver.tdr", "connection-resolver")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                         "Malformed XML file marked as valid")

        logging.debug("test_validate_single_file xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_validate_vendor_prefix(self):

        test_file = TEST_FOLDER / "modular_dialog_connector/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                        "Valid XML file not marked as valid")

        print("\nTest malformed xml. Throws XML validation error.")
        test_file = TEST_FOLDER / "broken_xml/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                         "XML file with invalid name values marked as valid")

        logging.debug("test_validate_vendor_prefix xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_validate_required_advanced_field_has_default_value(self):

        test_file = TEST_FOLDER / "modular_dialog_connector/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                        "Valid XML file not marked as valid")

        print("\nTest missing default-value for non-optional advanced field. Throws XML validation error.")
        test_file = TEST_FOLDER / "advanced_required_missing_default/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                         "XML file containing required field in 'advanced' category with no default value marked as valid")

        logging.debug("test_validate_required_advanced_field_has_default_value xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_validate_duplicate_fields_absent(self):

        test_file = TEST_FOLDER / "modular_dialog_connector/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                        "Valid XML file not marked as valid")

        print("\nTest duplicate fields not allowed. Throws XML validation error.")
        test_file = TEST_FOLDER / "duplicate_fields/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                         "A field with the field name = server already exists. Cannot have multiple fields with the same name.")

        logging.debug("test_validate_duplicate_fields_absent xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_validate_instanceurl(self):
        test_file = TEST_FOLDER / "oauth_connector/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                        "Valid XML file not marked as valid")

        test_file = TEST_FOLDER / "instanceurl/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                        "An instanceurl field must be conditional to authentication field with value=oauth")
