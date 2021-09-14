import unittest
from pathlib import Path

from connector_packager.xml_parser import XMLParser
from connector_packager.connector_file import ConnectorFile

TEST_FOLDER = Path("tests/test_resources")


class TestXMLParser(unittest.TestCase):

    def test_generate_file_list(self):

        # Test valid connector
        expected_class_name = "postgres_odbc"
        expected_file_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.tdd", "dialect"),
            ConnectorFile("connectionResolver.tdr", "connection-resolver"),
            ConnectorFile("resources-en_US.xml", "resource")]

        actual_file_list, actual_class_name = self.parser_test_case(TEST_FOLDER / Path("valid_connector"),
                                                                    expected_file_list, expected_class_name)

        self.assertTrue(actual_file_list, "Valid connector did not return a file list")
        self.assertTrue(sorted(actual_file_list) == sorted(expected_file_list),
                        "Actual file list does not match expected for valid connector")
        self.assertTrue(actual_class_name == expected_class_name,
                        "Actual class name does not match expected for valid connector")

        print("\nTest invalid connector. Throws XML validation error.")

        actual_file_list, actual_class_name = self.parser_test_case(TEST_FOLDER / Path("broken_xml"),
                                                                    expected_file_list, expected_class_name)
        self.assertFalse(actual_file_list, "Invalid connector returned a file list when it should not have")

        print("\nTest connector with class name mismatch. Throws XML validation error.")
        actual_file_list, actual_class_name = self.parser_test_case(TEST_FOLDER / Path("wrong_class"),
                                                                    expected_file_list, expected_class_name)
        self.assertFalse(actual_file_list, "Connector with class name mismatch returned a file list when it shouldn't")

        # Test connector with non-https url
        actual_file_list, actual_class_name = self.parser_test_case(TEST_FOLDER / Path("non_https"),
                                                                    expected_file_list, expected_class_name)
        self.assertFalse(actual_file_list, "Connector with non-https urls returned a file list when it shouldn't")

        # Test connector with missing English transaltion
        actual_file_list, actual_class_name = self.parser_test_case(TEST_FOLDER / Path("missing_english_translation"),
                                                                    expected_file_list, expected_class_name)
        self.assertFalse(actual_file_list, "Connector with localized strings but without a resources-en_US.xml file returned a file list when it shouldn't")

    def test_generate_file_list_mcd(self):
        # Test modular dialog connector
        expected_class_name = "postgres_mcd"
        expected_file_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]

        actual_file_list, actual_class_name = self.parser_test_case(TEST_FOLDER / Path("modular_dialog_connector"),
                                                                    expected_file_list, expected_class_name)

        self.assertTrue(actual_file_list, "Valid connector did not return a file list")
        self.assertTrue(sorted(actual_file_list) == sorted(expected_file_list),
                        "Actual file list does not match expected for valid connector")
        self.assertTrue(actual_class_name == expected_class_name,
                        "Actual class name does not match expected for valid connector")

    def test_generate_file_list_oauth(self):
        # Test oauth connector
        expected_class_name = "test_oauth"
        expected_file_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("oauth-config.xml", "oauth-config"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]

        actual_file_list, actual_class_name = self.parser_test_case(TEST_FOLDER / Path("oauth_connector"),
                                                                    expected_file_list, expected_class_name)

        self.assertTrue(actual_file_list, "Valid connector did not return a file list")
        self.assertTrue(sorted(actual_file_list) == sorted(expected_file_list),
                        "Actual file list does not match expected for valid connector")
        self.assertTrue(actual_class_name == expected_class_name,
                        "Actual class name does not match expected for valid connector")

    def parser_test_case(self, test_folder, expected_file_list, expected_class_name):

        xml_parser = XMLParser(test_folder)

        actual_file_list = xml_parser.generate_file_list()
        actual_class_name = xml_parser.class_name

        return actual_file_list, actual_class_name
