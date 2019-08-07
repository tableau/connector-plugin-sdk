import unittest
from connector_packager import version


class TestPackage(unittest.TestCase):

    def test_version(self):
        self.assertTrue(version.__version__ == '0.0.1')
