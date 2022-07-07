import unittest
import logging
from pathlib import Path

from connector_packager.xsd_validator import validate_all_xml, validate_single_file, warn_file_specific_rules
from connector_packager.connector_file import ConnectorFile
from connector_packager.connector_properties import ConnectorProperties

logger = logging.getLogger(__name__)

TEST_FOLDER = Path("tests/test_resources")

dummy_properties = ConnectorProperties()


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

        self.assertTrue(validate_all_xml(files_list, test_folder, dummy_properties), "Valid connector not marked as valid")

        print("\nTest broken xml. Throws a XML validation error.")
        test_folder = TEST_FOLDER / Path("broken_xml")

        files_list = [ConnectorFile("manifest.xml", "manifest")]

        self.assertFalse(validate_all_xml(files_list, test_folder, dummy_properties), "Invalid connector was marked as valid")

    def test_validate_single_file(self):

        test_file = TEST_FOLDER / Path("valid_connector/manifest.xml")
        file_to_test = ConnectorFile("manifest.xml", "manifest")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                        "Valid XML file not marked as valid")

        test_file = TEST_FOLDER / Path("big_manifest/manifest.xml")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "Big XML file marked as valid")

        print("\nTest broken xml. Throws XML validation error.")
        test_file = TEST_FOLDER / Path("broken_xml/manifest.xml")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "XML file that doesn't follow schema marked as valid")

        print("\nTest malformed xml. Throws XML validation error.")
        test_file = TEST_FOLDER / Path("broken_xml/connectionResolver.tdr")
        file_to_test = ConnectorFile("connectionResolver.tdr", "connection-resolver")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "Malformed XML file marked as valid")

        logging.debug("test_validate_single_file xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_validate_vendor_prefix(self):

        test_file = TEST_FOLDER / "modular_dialog_connector/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                        "Valid XML file not marked as valid")

        print("\nTest malformed xml. Throws XML validation error.")
        test_file = TEST_FOLDER / "broken_xml/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "XML file with invalid name values marked as valid")

        logging.debug("test_validate_vendor_prefix xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_validate_required_advanced_field_has_default_value(self):

        test_file = TEST_FOLDER / "modular_dialog_connector/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                        "Valid XML file not marked as valid")

        print("\nTest missing default-value for non-optional advanced field. Throws XML validation error.")
        test_file = TEST_FOLDER / "advanced_required_missing_default/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "XML file containing required field in 'advanced' category with no default value marked as valid")

        logging.debug("test_validate_required_advanced_field_has_default_value xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_validate_duplicate_fields_absent(self):

        test_file = TEST_FOLDER / "modular_dialog_connector/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                        "Valid XML file not marked as valid")

        print("\nTest duplicate fields not allowed. Throws XML validation error.")
        test_file = TEST_FOLDER / "duplicate_fields/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "A field with the field name = server already exists. Cannot have multiple fields with the same name.")

        logging.debug("test_validate_duplicate_fields_absent xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_validate_instanceurl(self):
        test_file = TEST_FOLDER / "oauth_connector/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                        "Valid XML file not marked as valid")

        test_file = TEST_FOLDER / "instanceurl/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        xml_violations_buffer = []

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "An instanceurl field must be conditional to authentication field with value=oauth")

        # instanceURL should not be required in required-attributes since it's automatically added
        test_folder = TEST_FOLDER / Path("oauth_connector")  # This connector uses a connection-fields.xml file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]
        properties_uses_tcd = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_uses_tcd),
         "InstanceURL not in required-attributes is valid")

    def test_warn_defaultSQLDialect_as_base(self):

        test_dialect_file = TEST_FOLDER / "defaultSQLDialect_as_base/dialect.tdd"
        file_to_test = ConnectorFile("dialect.tdd", "dialect")

        with self.assertLogs('packager_logger', level='WARNING') as cm:
            warn_file_specific_rules(file_to_test, test_dialect_file)

        self.assertEqual(len(cm.output), 1)
        self.assertIn('DefaultSQLDialect', cm.output[0], "DefaultSQLDialect not found in warning message")

    def test_warn_authentication_attribute(self):

        file_to_test = ConnectorFile("connectionResolver.tdr", "connection-resolver")

        print("\nTest no warning when authentication attribute is in required attributes list.")
        test_tdr_file = TEST_FOLDER / "authentication_attribute/with_authentication.tdr"
        with self.assertLogs('packager_logger', level='WARNING') as cm:
            # Log a dummy message so that the log will exist.
            logging.getLogger('packager_logger').warning('dummy message')
            warn_file_specific_rules(file_to_test, test_tdr_file)

        self.assertEqual(len(cm.output), 1)
        self.assertNotIn("'authentication' attribute is missing", cm.output[0],
                         "\"'authentication' attribute is missing\" found in warning message")

        print("Test no warning when required attributes list is not specified.")
        test_tdr_file = TEST_FOLDER / "authentication_attribute/no_required_attributes_list.tdr"
        with self.assertLogs('packager_logger', level='WARNING') as cm:
            # Log a dummy message so that the log will exist.
            logging.getLogger('packager_logger').warning('dummy message')
            warn_file_specific_rules(file_to_test, test_tdr_file)

        self.assertEqual(len(cm.output), 1)
        self.assertNotIn("'authentication' attribute is missing", cm.output[0],
                         "\"'authentication' attribute is missing\" found in warning message")

        print("Test warning when authentication attribute is not in required attributes list.")
        test_tdr_file = TEST_FOLDER / "authentication_attribute/without_authentication.tdr"
        with self.assertLogs('packager_logger', level='WARNING') as cm:
            warn_file_specific_rules(file_to_test, test_tdr_file)

        self.assertEqual(len(cm.output), 1)
        self.assertIn("'authentication' attribute is missing", cm.output[0],
                      "\"'authentication' attribute is missing\" not found in warning message")

    def test_validate_auth_attr_in_connection_fields(self):
        test_file = TEST_FOLDER / "authentication_attribute/connection_fields_with_authentication.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        properties = ConnectorProperties()
        xml_violations_buffer = []

        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                        "XML Validation failed for valid connection fields file")

        test_file = TEST_FOLDER / "authentication_attribute/connection_fields_no_authentication.xml"
        properties = ConnectorProperties()
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                        "XML Validation passed for connection fields file without authentication field")

    def test_validate_connection_field_name(self):
        test_file = TEST_FOLDER / "field_name_validation/valid/connectionFields.xml"
        file_to_test = ConnectorFile("connectionFields.xml", "connection-fields")
        print("Test connectionFields is validated by XSD when field name is vaild ")
        xml_violations_buffer = []
        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                        "XML Validation passed for connectionFields.xml")

        print("Test connectionFields is invalidated by XSD when field name"
        "contains special character other than - or _")
        test_file = TEST_FOLDER / "field_name_validation/invalid/special_character/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "XML Validation failed for connectionFields.xml")

        print("Test connectionFields is invalidated by XSD when field name starts with a number")
        test_file = TEST_FOLDER / "field_name_validation/invalid/starting_number/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "XML Validation failed for connectionFields.xml")

        print("Test connectionFields is invalidated by XSD when field name starts with a space")
        test_file = TEST_FOLDER / "field_name_validation/invalid/starting_space/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "XML Validation failed for connectionFields.xml")
        print("Test connectionFields is invalidated by XSD when field name has space in between")

        test_file = TEST_FOLDER / "field_name_validation/invalid/space_in_between/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "XML Validation failed for connectionFields.xml")

        print("Test connectionFields is invalidated by XSD when field name ends with a space")
        test_file = TEST_FOLDER / "field_name_validation/invalid/ending_space/connectionFields.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "XML Validation failed for connectionFields.xml")

        logging.debug("test_validate_connetion_field_name xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)

    def test_inferred_connection_resolver_validation(self):
        properties = ConnectorProperties()
        xml_violations_buffer = []
        file_to_test = ConnectorFile("connectionResolver.xml", "connection-resolver")
        test_file = TEST_FOLDER / "inferred_connection_resolver/connectionResolver.xml"

        print("Test that connection resolver without connection-normalizer for a connector that uses a .tcd file is invalidated")
        properties.uses_tcd = True
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                         "Inferred connection resolver validated when tcd was used")

        print("Test that connection resolver with connection-normalizer for a connector that uses a .tcd file is validated")
        properties.uses_tcd = False
        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                        "Valid connector marked as invalid")

    def test_all_fields_in_normalizer(self):
        properties = ConnectorProperties()
        properties.uses_tcd = False
        properties.connection_fields = ['server', 'port', 'v-custom', 'username', 'password', 'v-custom2', 'vendor1', 'vendor2', 'vendor3']
        properties.connection_metadata_database = True
        xml_violations_buffer = []

        print("Test that normalizer not containing 'dbname' if connection-metadata database field is used is validated")
        file_to_test = ConnectorFile("connectionResolver.xml", "connection-resolver")
        test_file = TEST_FOLDER / "database_field_not_in_normalizer/connectionResolver.xml"
        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                        "Dbname is optional if unused so connection resolver is valid")


        print("Test that normalizer not containing all the fields in connection-fields is invalidated")
        file_to_test = ConnectorFile("connectionResolver.xml", "connection-resolver")
        test_file = TEST_FOLDER / "mcd_field_not_in_normalizer/connectionResolver.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                         "Inferred connection resolver validated when tcd was used")

        print("Test that normalizer containing all the fields in connection-fields is validated")
        file_to_test = ConnectorFile("connectionResolver.xml", "connection-resolver")
        test_file = TEST_FOLDER / "modular_dialog_connector/connectionResolver.xml"
        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                        "Valid connector marked as invalid")


    def test_validate_company_name_length(self):
        xml_violations_buffer = []
        file_to_test = ConnectorFile("manifest.xml", "manifest")

        print("Test that company name with length less than 1 is invalidated")
        test_file = TEST_FOLDER / "company_name_length_validation/min/manifest.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "Empty company name marked as valid")

        print("Test that company name with length greater than 24 is invalidated")
        test_file = TEST_FOLDER / "company_name_length_validation/max/manifest.xml"
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, dummy_properties),
                         "Company name with length greater than 24 marked as valid")

    def test_validate_jdbc_properties_builder(self):
        properties = ConnectorProperties()
        xml_violations_buffer = []
        file_to_test = ConnectorFile("connectionResolver.xml", "connection-resolver")
        test_file = TEST_FOLDER / "properties_builder/odbc/connectionResolver.xml"

        print("Test that a connection resolver without <connection-properties> and non-jdbc superclass is valid")
        properties.is_jdbc = False
        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                        "optional connection-properties not found and marked invalid")

        print("Test that a connection resolver without <connection-properties> and jdbc superclass is invalid")
        properties.is_jdbc = True
        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                         "required connection-properties not found and marked valid")

        test_file = TEST_FOLDER / "properties_builder/jdbc/connectionResolver.xml"

        print("Test that a connection resolver with <connection-properties> and non-jdbc superclass is valid")
        properties.is_jdbc = False
        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                        "optional connection-properties found and marked as invalid")

        print("Test that a connection resolver with <connection-properties> and jdbc superclass is valid")
        properties.is_jdbc = True
        self.assertTrue(validate_single_file(file_to_test, test_file, xml_violations_buffer, properties),
                        "required connection-properties found and marked as invalid")

    def test_warn_server_attribute(self):
        file_to_test = ConnectorFile("connectionResolver.tdr", "connection-resolver")

        print("\nTest no warning when server is in required attributes list.")
        test_tdr_file = TEST_FOLDER / "server_attribute/with_server.tdr"
        with self.assertLogs('packager_logger', level='WARNING') as cm:
            # Log a dummy message so that the log will exist.
            logging.getLogger('packager_logger').warning('dummy message')
            warn_file_specific_rules(file_to_test, test_tdr_file)

        self.assertEqual(len(cm.output), 1)
        self.assertNotIn("'server' attribute is missing", cm.output[0],
                         "\"'server' attribute is missing\" found in warning message")

        print("Test no warning when required attributes list is not specified.")
        test_tdr_file = TEST_FOLDER / "server_attribute/no_required_attributes_list.tdr"
        with self.assertLogs('packager_logger', level='WARNING') as cm:
            # Log a dummy message so that the log will exist.
            logging.getLogger('packager_logger').warning('dummy message')
            warn_file_specific_rules(file_to_test, test_tdr_file)

        self.assertEqual(len(cm.output), 1)
        self.assertNotIn("'server' attribute is missing", cm.output[0],
                         "\"'server' attribute is missing\" found in warning message")

        print("Test warning when server attribute is not in required attributes list.")
        test_tdr_file = TEST_FOLDER / "server_attribute/without_server.tdr"
        with self.assertLogs('packager_logger', level='WARNING') as cm:
            warn_file_specific_rules(file_to_test, test_tdr_file)

        self.assertEqual(len(cm.output), 1)
        self.assertIn("'server' attribute is missing", cm.output[0],
                      "\"'server' attribute is missing\" not found in warning message")
