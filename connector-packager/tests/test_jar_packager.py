import unittest
import os.path
from pathlib import Path
import subprocess
import shutil
import xml.etree.ElementTree as ET

from .jar_packager import create_jar
from connector_packager.jar_jdk_packager import jdk_create_jar
from connector_packager.connector_file import ConnectorFile
from connector_packager.version import __default_min_version_tableau__

TEST_FOLDER = Path("tests/test_resources")
MANIFEST_FILE_NAME = "manifest.xml"

VERSION_2020_3 = "2020.3"
VERSION_2021_1 = "2021.1"
VERSION_FUTURE = "2525.1"
VERSION_THREE_PART = "2021.1.3"


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
                         __default_min_version_tableau__, "wrong min-version-tableau attr or doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)

    def test_higher_min_tableau_version(self):
        files_list = [ConnectorFile("manifest.xml", "manifest")]
        source_dir = TEST_FOLDER / Path("higher_min_version")
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
                        VERSION_FUTURE, "wrong min-version-tableau attr or doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)

    def test_three_part_min_tableau_version(self):
        files_list = [ConnectorFile("manifest.xml", "manifest")]
        source_dir = TEST_FOLDER / Path("three_part_min_version")
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
                        VERSION_THREE_PART, "wrong min-version-tableau attr or doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)

    def test_tableau_support_link_min_tableau_version(self):
        files_list = [ConnectorFile("manifest.xml", "manifest")]
        source_dir = TEST_FOLDER / Path("tableau_support_link")
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
                        VERSION_2021_1, "wrong min-version-tableau attr or doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)

    def test_inferred_connection_resolver_min_tableau_version(self):
        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]
        source_dir = TEST_FOLDER / Path("inferred_connection_resolver")
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
                         VERSION_2021_1, "wrong min-version-tableau attr or doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)

    def test_jdk_create_jar_mcd(self):
        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script")]
        source_dir = TEST_FOLDER / Path("modular_dialog_connector")
        dest_dir = TEST_FOLDER / Path("packaged-connector-by-jdk/")
        package_name = "test_mcd.taco"

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
                         VERSION_2020_3, "wrong min-version-tableau attr or doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)

    def test_jdk_create_jar_oauth(self):
        files_list = [
            ConnectorFile("manifest.xml", "manifest"),
            ConnectorFile("connectionFields.xml", "connection-fields"),
            ConnectorFile("connectionMetadata.xml", "connection-metadata"),
            ConnectorFile("connectionBuilder.js", "script"),
            ConnectorFile("dialect.xml", "dialect"),
            ConnectorFile("connectionResolver.xml", "connection-resolver"),
            ConnectorFile("connectionProperties.js", "script"),
            ConnectorFile("oauth-config.xml", "oauth-config")]
        source_dir = TEST_FOLDER / Path("oauth_connector")
        dest_dir = TEST_FOLDER / Path("packaged-connector-by-jdk/")
        package_name = "test_oauth.taco"

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
                         VERSION_2021_1, "wrong min-version-tableau attr or doesn't exist")

        if dest_dir.exists():
            shutil.rmtree(dest_dir)
