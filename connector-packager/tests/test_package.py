import os
import unittest
import logging
from pathlib import Path

from connector_packager.package import PACKAGED_EXTENSION


logger = logging.getLogger(__name__)


class TestPackage(unittest.TestCase):

    def test_package_main(self):

        expected_package_name = "postgres_odbc"
        expected_dest_directory = Path("tests/test_resources/jars")
        files_directory = Path("tests/test_resources/valid_connector")

        path_to_test_file = expected_dest_directory / Path(expected_package_name + PACKAGED_EXTENSION)

        if path_to_test_file.exists():
            logging.debug("Removing old test file " + str(Path))
            path_to_test_file.unlink()

        os.system("python -m connector_packager.package " + str(files_directory) +
                  " --dest " + str(expected_dest_directory))

        self.assertTrue(path_to_test_file.exists(), "Packaged connector not found in expected directory")

        if path_to_test_file.exists():
            path_to_test_file.unlink()
