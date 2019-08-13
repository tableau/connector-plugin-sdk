import unittest
import os.path
from pathlib import Path
import subprocess
import shutil
import xml.etree.ElementTree as ET

from .jar_packager import create_jar
from connector_packager.jar_jdk_packager import jdk_create_jar
from connector_packager.connector_file import ConnectorFile
from connector_packager.version import __min_version_tableau__

TEST_FOLDER = Path("tests/test_resources")
MANIFEST_FILE_NAME = "manifest.xml"


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
        package_name = "test.taco"

        create_jar(source_dir, files_list, package_name, dest_dir)

        path_to_test_file = dest_dir / Path(package_name)
        self.assertTrue(os.path.isfile(path_to_test_file), "taco file doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)

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
        package_name = "test.taco"

        jdk_create_jar(source_dir, files_list, package_name, dest_dir)

        path_to_test_file = dest_dir / Path(package_name)
        self.assertTrue(os.path.isfile(path_to_test_file), "taco file doesn't exist")

        # test min support tableau version is stamped
        args = ["jar", "xf", package_name, MANIFEST_FILE_NAME]
        p = subprocess.Popen(args, cwd=os.path.abspath(dest_dir))
        self.assertEqual(p.wait(), 0, "can not extract manfifest file from taco")
        path_to_extracted_manifest = dest_dir / MANIFEST_FILE_NAME
        self.assertTrue(os.path.isfile(path_to_extracted_manifest), "extracted manifest file doesn't exist")

        manifest = ET.parse(path_to_extracted_manifest)
        self.assertEqual(manifest.getroot().get("min-version-tableau"),
                         __min_version_tableau__, "wrong min-version-tableau attr or doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)
