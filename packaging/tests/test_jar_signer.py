import unittest
from pathlib import Path
from unittest.mock import patch 
from package.jar_jdk_signer import jdk_sign_jar


TEST_FOLDER = Path("tests/test_resources/test_taco_to_sign")
TEST_TACO = "postgres_odbc.taco"
TEST_ALIAS_DIFF_PWD = "key_diff_pwd"
TEST_ALIAS_SAME_PWD= "key_same_pwd"
TEST_KEYSTORE = "tests/test_resources/test_keystore/test_ks.jks"


class TestJarSigner(unittest.TestCase):
    

    @patch('package.jar_jdk_signer.get_user_pwd')
    def test_diff_pwd(self, some_f):
        some_f.return_value = (str.encode("password\n"), str.encode("diffpwd\n"))
        result = jdk_sign_jar(TEST_FOLDER, TEST_TACO, TEST_ALIAS_DIFF_PWD, TEST_KEYSTORE)
        self.assertTrue(result)

    @patch('package.jar_jdk_signer.get_user_pwd')
    def test_wrong_ks_pwd(self, some_f):
        some_f.return_value = (str.encode("wrongpwd\n"), str.encode("diffpwd\n"))
        result = jdk_sign_jar(TEST_FOLDER, TEST_TACO, TEST_ALIAS_DIFF_PWD, TEST_KEYSTORE)
        self.assertFalse(result)

    @patch('package.jar_jdk_signer.get_user_pwd')
    def test_wrong_alias_pwd(self, some_f):
        some_f.return_value = (str.encode("password\n"), str.encode("wrongpwd\n"))
        result = jdk_sign_jar(TEST_FOLDER, TEST_TACO, TEST_ALIAS_DIFF_PWD, TEST_KEYSTORE)
        self.assertFalse(result)

    @patch('package.jar_jdk_signer.get_user_pwd')
    def test_same_pwd(self, some_f):
        some_f.return_value = (str.encode("password\n"), str.encode("\n"))
        result = jdk_sign_jar(TEST_FOLDER, TEST_TACO, TEST_ALIAS_SAME_PWD, TEST_KEYSTORE)
        self.assertTrue(result)

