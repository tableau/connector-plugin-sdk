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

        test_file = TEST_FOLDER / Path("broken_xml/manifest.xml")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                         "XML file that doesn't follow schema marked as valid")

        test_file = TEST_FOLDER / Path("broken_xml/connectionResolver.tdr")
        file_to_test = ConnectorFile("connectionResolver.tdr", "connection-resolver")

        self.assertFalse(validate_single_file(file_to_test, test_file, xml_violations_buffer),
                         "Malformed XML file marked as valid")

        logging.debug("test_validate_single_file xml violations:")
        for violation in xml_violations_buffer:
            logging.debug(violation)
