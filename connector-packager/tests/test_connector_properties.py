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
        expected_connection_fields = ['server', 'port', 'v-custom', 'username', 'password', 'v-custom2', 'vendor1', 'vendor2', 'vendor3']

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
        self.assertTrue(properties.database_field, "Database field not detected")
