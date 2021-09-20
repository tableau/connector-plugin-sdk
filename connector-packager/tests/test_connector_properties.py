import unittest
import logging
from pathlib import Path

from .jar_packager import create_jar
from connector_packager.connector_file import ConnectorFile
from connector_packager.connector_properties import ConnectorProperties
from connector_packager.xsd_validator import validate_all_xml

logger = logging.getLogger(__name__)

TEST_FOLDER = Path("tests/test_resources")


class TestConnectorProperties(unittest.TestCase):

    def test_uses_tcd_property(self):
        # Check that validate_all_xml properly sets uses_tcd to True if using .tcd file
        test_folder = TEST_FOLDER / Path("valid_connector")  # This connector uses a .tcd file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.tdd", "dialect"),
            ConnectorFile("connectionResolver.tdr", "connection-resolver"),
            ConnectorFile("resources-en_US.xml", "resource")]

        properties_uses_tcd = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_uses_tcd), "Valid connector not marked as valid")
        self.assertTrue(properties_uses_tcd.uses_tcd, "uses_tcd not set to True for connector using .tcd file")

        # Check that validate_all_xml properly sets uses_tcd to False if not using .tcd file
        test_folder = TEST_FOLDER / Path("modular_dialog_connector")  # This connector uses a connection-fields.xml file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]

        properties_does_not_use_tcd = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_does_not_use_tcd), "Valid connector not marked as valid")
        self.assertFalse(properties_does_not_use_tcd.uses_tcd, "uses_tcd not set to False for connector using .tcd file")

    def test_connector_fields_property(self):
        # Check that we correctly populate the connection fields property
        expected_connection_fields = ['server', 'port', 'v-custom', 'authentication', 'username', 'password', 'v-custom2', 'vendor1', 'vendor2', 'vendor3']

        test_folder = TEST_FOLDER / Path("modular_dialog_connector")  # This connector uses a connection-fields.xml file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]

        properties = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties), "Valid connector not marked as valid")
        self.assertEqual(expected_connection_fields, properties.connection_fields, "Actual properties.connection_fields did not match expected")

    def test_connection_metadata_property(self):
        test_folder = TEST_FOLDER / Path("modular_dialog_connector")  # This connector uses a connection-fields.xml file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]

        properties = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties), "Valid connector not marked as valid")
        self.assertTrue(properties.connection_metadata_database, "Database metadata not detected")

        test_folder = TEST_FOLDER / Path("database_field_not_in_normalizer")  # This connector uses a connection-fields.xml file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]

        properties = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties), "Valid connector not marked as valid")
        self.assertFalse(properties.connection_metadata_database, "Database metadata detected incorrectly")


    def test_is_jdbc_property(self):
        # Check that validate_all_xml properly sets is_jdbc to False if not using superclass=jdbc
        test_folder = TEST_FOLDER / Path("valid_connector")  # This connector uses a .tcd file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.tdd", "dialect"),
            ConnectorFile("connectionResolver.tdr", "connection-resolver"),
            ConnectorFile("resources-en_US.xml", "resource")]

        properties_not_jdbc = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_not_jdbc), "Valid connector not marked as valid")
        self.assertFalse(properties_not_jdbc.is_jdbc, "is_jdbc not set to False for connector with superclass other than jdbc")

        # Check that validate_all_xml properly sets is_jdbc to True if using superclass=jdbc
        test_folder = TEST_FOLDER / Path("modular_dialog_connector")  # This connector uses a connection-fields.xml file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]

        properties_is_jdbc = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_is_jdbc), "Valid connector not marked as valid")
        self.assertTrue(properties_is_jdbc.is_jdbc, "is_jdbc not set to True for connector with superclass jdbc")

    def test_vendor_defined_fields_tcd(self):
        # This connector uses a .tcd file and does not have vendor-defined fields
        test_folder = TEST_FOLDER / Path("valid_connector")  # This connector uses a .tcd file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.tdd", "dialect"),
            ConnectorFile("connectionResolver.tdr", "connection-resolver"),
            ConnectorFile("resources-en_US.xml", "resource")]

        properties_no_vendor_defined_fields = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_no_vendor_defined_fields), "Valid connector not marked as valid")
        self.assertFalse(properties_no_vendor_defined_fields.vendor_defined_fields, "Found vendor-defined fields when none were defined")

        # This connector uses a .tcd file and has vendor-defined fields
        test_folder = TEST_FOLDER / Path("tcd_vendor_defined_fields")

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog")]

        properties_has_vendor_defined_fields = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_has_vendor_defined_fields), "Valid connector not marked as valid")
        self.assertListEqual(properties_has_vendor_defined_fields.vendor_defined_fields, ['vendor1', 'vendor2', 'vendor3'], "Vendor-defined attributes not detected")

    def test_vendor_defined_fields_mcd(self):
        # This connector uses connection-fields file and does not have vendor-defined fields
        test_folder = TEST_FOLDER / Path("mcd_no_vendor_defined_fields")  # This connector uses a .tcd file

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata")]

        properties_no_vendor_defined_fields = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_no_vendor_defined_fields), "Valid connector not marked as valid")
        self.assertFalse(properties_no_vendor_defined_fields.vendor_defined_fields, "Found vendor-defined fields when none were defined")

        # This connector uses a connection-fields file and has vendor-defined fields
        test_folder = TEST_FOLDER / Path("modular_dialog_connector")

        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]

        properties_has_vendor_defined_fields = ConnectorProperties()
        self.assertTrue(validate_all_xml(files_list, test_folder, properties_has_vendor_defined_fields), "Valid connector not marked as valid")
        self.assertListEqual(properties_has_vendor_defined_fields.vendor_defined_fields, ['v-custom', 'v-custom2', 'vendor1', 'vendor2', 'vendor3'], "Vendor-defined attributes not detected")
