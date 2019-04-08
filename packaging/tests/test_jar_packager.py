import unittest
import os.path
from pathlib import Path

from package.jar_packager import create_jar
from package.jar_jdk_packager import jdk_create_jar
from package.connector_file import ConnectorFile

TEST_FOLDER = Path("tests/test_resources")


class TestJarPackager(unittest.TestCase):

    def test_create_jar(self):
        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.tdd", "dialect"),
            ConnectorFile("connectionResolver.tdr", "connection-resolver"),
            ConnectorFile("resources-en_US.xml", "resource")]
        source_dir = TEST_FOLDER / Path("valid_connector")
        dest_dir = TEST_FOLDER / Path("packaged-connector/")

        create_jar(source_dir, files_list, "test.taco", dest_dir)
        self.assertTrue(os.path.isfile(dest_dir/Path("test.taco")), "taco file doesn't exist")

    def test_jdk_create_jar(self):
        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connection-dialog.tcd", "connection-dialog"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.tdd", "dialect"),
            ConnectorFile("connectionResolver.tdr", "connection-resolver"),
            ConnectorFile("resources-en_US.xml", "resource")]
        source_dir = TEST_FOLDER / Path("valid_connector")
        dest_dir = TEST_FOLDER / Path("packaged-connector-by-jdk/")

        jdk_create_jar(source_dir, files_list, "test.taco", dest_dir)
        self.assertTrue(os.path.isfile(dest_dir/Path("test.taco")), "taco file doesn't exist")


