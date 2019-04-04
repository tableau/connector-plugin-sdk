import unittest
from package.connector_file import ConnectorFile

class TestConnectorFile(unittest.TestCase):

    def test_extension(self):
        c = ConnectorFile("test.tcd", "dialog")
        self.assertTrue(c.extension() == "tcd")

        c = ConnectorFile("test", "empty")
        self.assertTrue(c.extension() == "")

        c = ConnectorFile(".test", "empty")
        self.assertTrue(c.extension() == "")

