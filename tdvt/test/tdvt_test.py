"""
    Tableau Datasource Verification Tool Tester - TDVTT
    Test the TDVT.

    Run from the 'test' directory. The path to tabquerycli is configured in test/config/tdvt.
    You can run these like:
    All tests:
        python -m tdvt_test
    A Class:
        python -m tdvt_test ReRunFailedTestsTest
    One specific test:
        python -m tdvt_test ReRunFailedTestsTest.test_logical_rerun_fail

"""

import io
import logging
import platform
import re
import shutil
import subprocess
import sys
import unittest

from pathlib import Path
from typing import List
from unittest import mock

from defusedxml.ElementTree import parse

from tdvt import tdvt_core
from tdvt.tdvt import enqueue_failed_tests, create_parser, get_ds_list
from tdvt.config_gen import datasource_list
from tdvt.config_gen.test_config import ExpressionTestSet, LogicalTestSet, RunTimeTestConfig, TestFile, TabQueryPath
from tdvt.test_results import *
from tdvt.tabquery import *

from tdvt.config_gen.test_creator import TestCreator
from tdvt.setup_env import updated_tds_as_str, get_failed_cmd_line
from tdvt.tdvt_core import get_cleaned_results, do_work
from tdvt.tdvt import TestOutputFiles


class DiffTest(unittest.TestCase):

    def test_diff(self):
        logging.debug("Starting diff tests:\n")
        subdir = 'diff_tests'
        # Go through the 'expected' files as the driver.
        test_files = []
        for item in os.listdir(os.path.join(TEST_DIRECTORY, subdir)):
            if 'expected.' in item:
                test_files.append(item)

        failed_tests = []
        for test in test_files:
            actual_file = test.replace('expected', 'actual')

            actual_file = os.path.join(os.path.join(TEST_DIRECTORY, subdir), actual_file)
            expected_file = os.path.join(os.path.join(TEST_DIRECTORY, subdir), test)

            logging.debug("Testing: " + test)
            actual_xml = parse(actual_file).getroot()
            expected_xml = parse(expected_file).getroot()
            compare_sql = False
            compare_tuples = False
            compare_error = False
            if 'expected.sql' in test:
                compare_sql = True
            if 'expected.tuples' in test:
                compare_tuples = True
            if 'expected.both' in test:
                compare_tuples = True
                compare_sql = True
            if 'expected.error' in test:
                compare_error = True
            test_config = TdvtInvocation()
            test_config.tested_sql = compare_sql
            test_config.tested_tuples = compare_tuples
            test_config.tested_error = compare_error
            results = tdvt_core.TestResult(test_config=test_config)
            results.add_test_results(actual_xml, actual_file)
            expected_output = tdvt_core.TestResult(test_config=test_config)
            expected_output.add_test_results(expected_xml, '')

            num_diffs, diff_string = results.diff_test_results(expected_output)
            results.set_best_matching_expected_output(expected_output, expected_file, 0, [0])

            if results.all_passed() and 'shouldfail' not in test:
                logging.debug("Test passed: " + test)
                self.assertTrue(True)
            elif not results.all_passed() and 'shouldfail' in test:
                logging.debug("Test passed: " + test)
                self.assertTrue(True)
            else:
                logging.debug("Test failed: " + test)
                failed_tests.append(test)
                self.assertTrue(False)
            logging.debug("\n")

        if failed_tests:
            logging.debug("All failed tests:\n")
            for item in failed_tests:
                logging.debug("Failed -- " + item)

        logging.debug("Ending diff tests:\n")
        return len(test_files), len(failed_tests)


class BaseTDVTTest(unittest.TestCase):
    def setUp(self):
        self.test_config = TdvtInvocation()
        env_tabquery = os.environ.get('TABQUERY_CLI_PATH')
        if env_tabquery:
            rt = RunTimeTestConfig()
            rt.set_tabquery_paths(env_tabquery, env_tabquery, env_tabquery)
            self.test_config.set_run_time_test_config(rt)

        if self.test_config.tested_run_time_config:
            self.assertTrue(tabquerycli_exists(self.test_config.tested_run_time_config.tabquery_paths))
        else:
            self.assertTrue(tabquerycli_exists())
        self.test_config.output_dir = make_temp_dir([self.test_config.suite_name])

    def tearDown(self):
        shutil.rmtree(self.test_config.output_dir)

    def check_results(self, test_results, total_test_count, should_pass=True):
        test_status_expected = "passed" if should_pass else "failed"
        # Make sure we ran the right number of tests and that they all passed.
        self.assertEqual(len(test_results), total_test_count)
        for path, test_result in test_results.items():
            passed = test_result is not None
            passed = passed and test_result.all_passed()
            test_status = "passed" if passed else "failed"
            self.assertEqual(passed, should_pass)


class ExpressionTest(BaseTDVTTest):
    def setUp(self):
        super(type(self), self).setUp()
        self.config_set = ExpressionTestSet('', ROOT_DIRECTORY, 'expression.tde', 'cast_calcs.tde.tds', '',
                                            'tool_test\exprtests\setup.*.txt', '')
        self.test_config.tds = tdvt_core.get_tds_full_path(ROOT_DIRECTORY, 'tool_test/tds/cast_calcs.tde.tds')

    def test_expression_tests(self):
        all_test_results = {}
        all_test_results = tdvt_core.run_tests_impl(self.config_set, self.test_config)
        self.check_results(all_test_results, 2)


class LocalExpressionTest(BaseTDVTTest):
    def setUp(self):
        super(type(self), self).setUp()
        # Tests picking a local test suite.
        self.config_set = ExpressionTestSet('', ROOT_DIRECTORY, 'expression.tde', 'cast_calcs.tde.tds', 'mytest3',
                                            'e/suite1/', '')
        self.test_config.tds = tdvt_core.get_tds_full_path(ROOT_DIRECTORY, 'tool_test/tds/cast_calcs.tde.tds')

    def test_expression_tests(self):
        all_test_results = {}
        all_test_results = tdvt_core.run_tests_impl(self.config_set, self.test_config)
        self.check_results(all_test_results, 2)


class LogicalTest(BaseTDVTTest):
    def setUp(self):
        super(type(self), self).setUp()
        self.config_set = LogicalTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                         'tool_test\logicaltests\setup\calcs\setup.*.xml', '')
        self.test_config.tds = tdvt_core.get_tds_full_path(ROOT_DIRECTORY, 'tool_test/tds/cast_calcs.tde.tds')
        self.test_config.logical = True

    def test_logical_tests(self):
        all_test_results = tdvt_core.run_tests_impl(self.config_set, self.test_config)

        self.check_results(all_test_results, 1)


class LocalLogicalTest(BaseTDVTTest):
    def setUp(self):
        super(type(self), self).setUp()
        self.config_set = LogicalTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                         'logical/setup/suite1/setup.*.xml', '')
        self.test_config.tds = tdvt_core.get_tds_full_path(ROOT_DIRECTORY, 'tool_test/tds/cast_calcs.tde.tds')
        self.test_config.logical = True

    def test_logical_tests(self):
        all_test_results = {}
        all_test_results = tdvt_core.run_tests_impl(self.config_set, self.test_config)

        self.check_results(all_test_results, 1)


class ReRunFailedTestsTest(BaseTDVTTest):
    def setUp(self):
        super(type(self), self).setUp()
        self.test_dir = TEST_DIRECTORY
        self.config_file = 'config/logical.tde.cfg'
        self.config_set = LogicalTestSet('', TEST_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                         'logicaltests\setup\calcs\setup.*.xml', '')
        self.tds_file = tdvt_core.get_tds_full_path(TEST_DIRECTORY, 'tds/cast_calcs.tde.tds')
        self.test_config.logical = True
        self.test_config.config_file = self.config_file
        self.test_config.tds = self.tds_file

    def test_failed_test_output(self):
        """Make sure TDVT writes the correct output file for rerunning failed tests."""
        all_test_results = {}
        # This will cause the test to fail as expected.
        self.test_config.tested_sql = True
        all_test_results = tdvt_core.run_tests_impl(self.config_set, self.test_config)
        tdvt_core.write_standard_test_output(all_test_results, self.test_dir)

        self.check_results(all_test_results, 1, False)

        # Now rerun the failed tests which should fail again,
        # indicating that the 'tested_sql' option was persisted correctly.

        tests = enqueue_failed_tests(Path(get_path('tool_test', 'tdvt_output.json', __name__)), TEST_DIRECTORY, None,
                                     self.test_config.tested_run_time_config)
        all_test_results = tdvt_core.run_tests_serial(tests)

        self.check_results(all_test_results, 1, False)

    def test_logical_rerun(self):
        tests = enqueue_failed_tests(Path(get_path('tool_test/rerun_failed_tests', 'logical.json', __name__)),
                                     TEST_DIRECTORY, None, self.test_config.tested_run_time_config)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 1)

    def test_expression_rerun(self):
        tests = enqueue_failed_tests(Path(get_path('tool_test/rerun_failed_tests', 'exprtests.json', __name__)),
                                     TEST_DIRECTORY, None, self.test_config.tested_run_time_config)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 2)

    def test_combined_rerun(self):
        tests = enqueue_failed_tests(Path(get_path('tool_test/rerun_failed_tests', 'combined.json', __name__)),
                                     TEST_DIRECTORY, None, self.test_config.tested_run_time_config)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 3)

    def test_combined_rerun_local_tests(self):
        tests = enqueue_failed_tests(Path(get_path('tool_test/rerun_failed_tests', 'combined_local.json', __name__)),
                                     TEST_DIRECTORY, None, self.test_config.tested_run_time_config)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 5)

    def test_failed_rerun(self):
        tests = enqueue_failed_tests(Path(get_path('tool_test/rerun_failed_tests', 'failed_tests.json', __name__)),
                                     TEST_DIRECTORY, None, self.test_config.tested_run_time_config)
        self.assertTrue(tests[0][0].get_expected_message() == "Invalid username or password",
                        "Expected message was not read in correctly.")

    def test_logical_rerun_fail(self):
        tests = enqueue_failed_tests(
            Path(get_path('tool_test/rerun_failed_tests', 'logical_compare_sql.json', __name__)),
            TEST_DIRECTORY, None, self.test_config.tested_run_time_config)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 1, False)


def build_tabquery_command_line_local(work):
    """To facilitate testing. Just get the executable name and not the full path to the executable which depends on
    where the test is run."""
    cmd = build_tabquery_command_line(work)
    new_cmd = []
    new_cmd.append(os.path.split(cmd[0])[1])
    new_cmd += cmd[1:]
    return new_cmd


class ArgumentTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_list(self):
        parser = create_parser()
        args = parser.parse_args(['list'])
        self.assertTrue(args.list_ds == '')

        args = parser.parse_args(['list', 'mydb'])
        self.assertTrue(args.list_ds == 'mydb')

        args = parser.parse_args(['list-logical-configs'])
        self.assertTrue(args.list_logical_configs == '')

        args = parser.parse_args(['list-logical-configs', 'mydb'])
        self.assertTrue(args.list_logical_configs == 'mydb')

        # self.assertRaises(argparse.ArgumentError, parser.parse_args(['list', '--logical_config', 'mydb', '--ds']))

    def test_run(self):
        parser = create_parser()
        args = parser.parse_args(['run', 'sqldb'])
        self.assertTrue(args.command == 'run')
        ds = get_ds_list(args.ds)
        self.assertTrue('sqldb' in ds)

        args = parser.parse_args(['run', 'sqldb,mysqldb'])
        ds = get_ds_list(args.ds)
        self.assertTrue('sqldb' in ds)
        self.assertTrue('mysqldb' in ds)

        args = parser.parse_args(['run', 'sqldb, mysqldb'])
        ds = get_ds_list(args.ds)
        self.assertTrue('sqldb' in ds)
        self.assertTrue('mysqldb' in ds)


class CommandLineTest(unittest.TestCase):
    def setUp(self):
        self.test_config = TdvtInvocation()
        self.test_config.logical = False
        self.test_config.tds = 'mytds.tds'
        self.test_config.tested_run_time_config = RunTimeTestConfig()

        self.test_file = 'some/test/file.txt'
        self.test_set = ExpressionTestSet('', TEST_DIRECTORY, 'mytest', self.test_config.tds, '', self.test_file, '')

    def test_command_line_override_full(self):
        linux_path = 'some_other_linux'
        mac_path = 'another_mac'
        mac_arm_path = 'another_arm_mac'
        win_path = 'something_windows.exe'
        self.test_config.tested_run_time_config.set_tabquery_paths(linux_path, mac_path, mac_arm_path, win_path)

        work = tdvt_core.BatchQueueWork(self.test_config, self.test_set)
        cmd_line = build_tabquery_command_line_local(work)
        if sys.platform in ('win32', 'cygwin'):
            expected = win_path
        elif sys.platform == 'darwin':
            expected = mac_path
        elif sys.platform == 'linux':
            expected = linux_path
        else:
            self.skipTest("Unsupported test OS: {}".format(sys.platform))
        self.assertTrue(cmd_line[0] == expected, 'Actual: ' + cmd_line[0] + ': Expected: ' + expected)

    def test_command_line_full(self):
        self.test_config.output_dir = 'my/output/dir'
        self.test_config.d_override = '-DLogLevel=Debug'
        self.test_config.tested_run_time_config.set_tabquery_paths("tabquerytool", "tabquerytool", "tabquerycli", "tabquerytool.exe")

        work = tdvt_core.BatchQueueWork(self.test_config, self.test_set)
        cmd_line = build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        if sys.platform in ('win32', 'cygwin'):
            expected = 'tabquerytool.exe --expression-file-list my/output/dir\mytest\\tests.txt -d mytds.tds --combined --output-dir my/output/dir -DLogDir=my/output/dir\mytest -DOverride=ProtocolServerNewLog -DLogLevel=Debug -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable'  # noqa: E501
        elif sys.platform in ('darwin', 'linux'):
            expected = 'tabquerytool --expression-file-list my/output/dir/mytest/tests.txt -d mytds.tds --combined --output-dir my/output/dir -DLogDir=my/output/dir/mytest -DOverride=ProtocolServerNewLog -DLogLevel=Debug -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable'  # noqa: E501
        else:
            self.skipTest("Unsupported test OS: {}".format(sys.platform))
        self.assertTrue(cmd_line_str == expected, 'Actual: ' + cmd_line_str + ': Expected: ' + expected)

    def test_password_file(self):
        self.test_config.output_dir = 'my/output/dir'
        self.test_config.tested_run_time_config.set_tabquery_paths("tabquerytool", "tabquerytool", "tabquerycli", "tabquerytool.exe")
        suite = 'password_test'

        self.test_set = ExpressionTestSet('', TEST_DIRECTORY, 'mytest', self.test_config.tds, '', self.test_file, suite)
        work = tdvt_core.BatchQueueWork(self.test_config, self.test_set)
        cmd_line = build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        self.assertTrue('--password-file' in cmd_line_str and 'password_test.password' in cmd_line_str)

    def test_command_line_no_expected(self):
        self.test_config.tested_run_time_config.set_tabquery_paths("tabquerytool", "tabquerytool", "tabquerycli", "tabquerytool.exe")
        work = tdvt_core.BatchQueueWork(self.test_config, self.test_set)
        cmd_line = build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        if sys.platform in ('win32', 'cygwin'):
            expected = 'tabquerytool.exe --expression-file-list mytest\\tests.txt -d mytds.tds --combined -DLogDir=mytest -DOverride=ProtocolServerNewLog -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable'  # noqa: E501
        elif sys.platform in ('darwin', 'linux'):
            expected = 'tabquerytool --expression-file-list mytest/tests.txt -d mytds.tds --combined -DLogDir=mytest -DOverride=ProtocolServerNewLog -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable'  # noqa: E501
        else:
            self.skipTest("Unsupported test OS: {}".format(sys.platform))
        self.assertTrue(cmd_line_str == expected, 'Actual: ' + cmd_line_str + ': Expected: ' + expected)

    def test_command_line_multiple_override(self):
        self.test_config.d_override = '-DLogLevel=Debug -DUseJDBC -DOverride=MongoDBConnector:on,SomethingElse:off'
        self.test_config.tested_run_time_config.set_tabquery_paths("tabquerytool", "tabquerytool", "tabquerycli", "tabquerytool.exe")

        work = tdvt_core.BatchQueueWork(self.test_config, self.test_set)
        cmd_line = build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        if sys.platform in ('win32', 'cygwin'):
            expected = 'tabquerytool.exe --expression-file-list mytest\\tests.txt -d mytds.tds --combined -DLogDir=mytest -DOverride=ProtocolServerNewLog -DLogLevel=Debug -DUseJDBC -DOverride=MongoDBConnector:on,SomethingElse:off -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable'  # noqa: E501
        elif sys.platform in ('darwin', 'linux'):
            expected = 'tabquerytool --expression-file-list mytest/tests.txt -d mytds.tds --combined -DLogDir=mytest -DOverride=ProtocolServerNewLog -DLogLevel=Debug -DUseJDBC -DOverride=MongoDBConnector:on,SomethingElse:off -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable'  # noqa: E501
        else:
            self.skipTest(reason="Unsupported test OS: {}".format(sys.platform))
        self.assertTrue(cmd_line_str == expected, 'Actual: ' + cmd_line_str + ': Expected: ' + expected)

    def test_command_line_multiple_override_from_invocation(self):
        rtt = RunTimeTestConfig(60 * 60, 1,
                                '-DLogLevel=Debug -DUseJDBC -DOverride=MongoDBConnector:on,SomethingElse:off')
        test_config = TdvtInvocation()
        test_config.set_run_time_test_config(rtt)
        test_config.logical = False
        test_config.tds = 'mytds.tds'

        test_file = 'some/test/file.txt'
        test_set = ExpressionTestSet('', TEST_DIRECTORY, 'mytest', test_config.tds, '', self.test_file, '')
        test_config.tested_run_time_config.set_tabquery_paths("tabquerytool", "tabquerytool", "tabquerycli", "tabquerytool.exe")

        work = tdvt_core.BatchQueueWork(test_config, self.test_set)
        cmd_line = build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        if sys.platform in ('win32', 'cygwin'):
            expected = 'tabquerytool.exe --expression-file-list mytest\\tests.txt -d mytds.tds --combined -DLogDir=mytest -DOverride=ProtocolServerNewLog -DLogLevel=Debug -DUseJDBC -DOverride=MongoDBConnector:on,SomethingElse:off -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable'  # noqa: E501
        elif sys.platform in ('darwin', 'linux'):
            expected = 'tabquerytool --expression-file-list mytest/tests.txt -d mytds.tds --combined -DLogDir=mytest -DOverride=ProtocolServerNewLog -DLogLevel=Debug -DUseJDBC -DOverride=MongoDBConnector:on,SomethingElse:off -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable'  # noqa: E501
        else:
            self.skipTest(reason="Unsupported test OS: {}".format(sys.platform))
        self.assertTrue(cmd_line_str == expected, 'Actual: ' + cmd_line_str + ': Expected: ' + expected)


class TestPathTest(unittest.TestCase):
    def assert_number_of_tests(self, config_set, test_size):
        all_tests = config_set.generate_test_file_list()
        self.assertTrue(len(all_tests) == test_size)

    def test_dir(self):
        self.assert_number_of_tests(LogicalTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                                   'logical/setup/suite1/', ''), 1)

    def test_file(self):
        self.assert_number_of_tests(LogicalTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                                   'logical/setup/suite1/setup.sum.tde.xml', ''), 1)

    def test_glob(self):
        self.assert_number_of_tests(LogicalTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                                   'logical/setup/suite1/setup.*.xml', ''), 1)

    def test_exclude(self):
        self.assert_number_of_tests(LogicalTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', 'sum',
                                                   'logical/setup/suite1/setup.*.xml', ''), 0)

    def test_exclude_comma(self):
        self.assert_number_of_tests(LogicalTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', ',',
                                                   'logical/setup/suite1/setup.*.xml', ''), 1)

    def test_exclude_space(self):
        self.assert_number_of_tests(LogicalTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', ' sum',
                                                   'logical/setup/suite1/setup.*.xml', ''), 0)

    def test_local_dir(self):
        self.assert_number_of_tests(ExpressionTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                                      'e/suite1/', ''), 3)

    def test_local_file(self):
        self.assert_number_of_tests(ExpressionTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                                      'e/suite1/setup.mytest.txt', ''), 1)

    def test_local_glob(self):
        self.assert_number_of_tests(ExpressionTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', '',
                                                      'e/suite1/setup.*.txt', ''), 3)

    def test_local_exclude(self):
        self.assert_number_of_tests(
            ExpressionTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', 'mytest3',
                              'e/suite1/setup.*.txt', ''), 2)


class ConfigTest(unittest.TestCase):
    def test_load_ini(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'aurora.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet('aurora', TEST_DIRECTORY, 'logical.calcs.aurora', 'cast_calcs.aurora.tds', '',
                               'logicaltests/setup/calcs/setup.*.bool_.xml', test_config.dsname)

        test2 = LogicalTestSet('aurora', TEST_DIRECTORY, 'logical.staples.aurora', 'Staples.aurora.tds',
                               'Filter.Trademark',
                               'logicaltests/setup/staples/setup.*.bool_.xml', test_config.dsname)

        test3 = LogicalTestSet('aurora', TEST_DIRECTORY, 'logical.lod.aurora', 'Staples.aurora.tds', '',
                               'logicaltests/setup/lod/setup.*.bool_.xml', test_config.dsname)

        test4 = ExpressionTestSet('aurora', TEST_DIRECTORY, 'expression.standard.aurora', 'cast_calcs.aurora.tds',
                                  'string.char,dateparse', 'exprtests/standard/setup.*.txt', test_config.dsname)

        test5 = ExpressionTestSet('aurora', TEST_DIRECTORY, 'expression.lod.aurora', 'cast_calcs.aurora.tds', '',
                                  'exprtests/lodcalcs/setup.*.txt', test_config.dsname)

        tests = [test1, test2, test3, test4, test5]

        for test in tests:
            found = [y for y in x if y == test]
            msg = "[Did not find expected value of [{0}]".format(test)
            self.assertTrue(found, msg)

    def test_load_ini_missing(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'aurora_missing.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.aurora', 'cast_calcs.aurora.tds', '',
                               'logicaltests/setup/calcs/setup.*.bool_.xml', test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.aurora', 'Staples.aurora.tds',
                               'Filter.Trademark',
                               'logicaltests/setup/staples/setup.*.bool_.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.aurora',
                                  'cast_calcs.aurora.tds',
                                  'string.char,dateparse', 'exprtests/standard/setup.*.txt', test_config.dsname)

        tests = [test1, test2, test3]

        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_missing2(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'aurora_missing2.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.aurora', 'cast_calcs.aurora.tds', '',
                               'logicaltests/setup/calcs/setup.*.bool_.xml', test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.aurora', 'Staples.aurora.tds', '',
                               'logicaltests/setup/staples/setup.*.bool_.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.aurora',
                                  'cast_calcs.aurora.tds', '', 'exprtests/standard/setup.*.txt', test_config.dsname)

        tests = [test1, test2, test3]

        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_bigquery(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'bigquery.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.bigquery', 'cast_calcs.bigquery.tds',
                               '',
                               'logicaltests/setup/calcs/setup.*.bigquery.xml', test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.bigquery', 'Staples.bigquery.tds',
                               '',
                               'logicaltests/setup/staples/setup.*.bigquery.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.bigquery',
                                  'cast_calcs.bigquery.tds',
                                  'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse',
                                  # noqa: E501
                                  'exprtests/standard/setup.*.txt', test_config.dsname)

        tests = [test1, test2, test3]

        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_new_tests(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'new_tests.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical_test1.bigquery_sql_test',
                               'Staples.bigquery.tds', '',
                               'logicaltests/setup.*.bigquery.xml', test_config.dsname)
        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical_test2.bigquery_sql_test',
                               'Staples.bigquery_sql_test.tds', '',
                               'logicaltests/setup.*.bigquery.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression_test1.bigquery_sql_test',
                                  'cast_calcs.bigquery_sql_dates2.tds', 'string.ascii', 'exprtests/standard/',
                                  test_config.dsname)
        test4 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression_test2.bigquery_sql_test',
                                  'cast_calcs.bigquery_sql_test.tds', 'string.char', 'exprtests/standard/',
                                  test_config.dsname)

        tests = [test1, test2, test3, test4]

        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_password_file(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'password_file.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        expected_password_file = "a_wrong.password"
        self.assertTrue(len(x) == 10, "[Did not find expected number of tests. Found [{0}]".format(len(x)))
        for test in x:
            actual_file = os.path.split(test.get_password_file_name())[1]
            self.assertTrue(actual_file == expected_password_file,
                            "[Did not find expected value of [{0}, found {1} instead.]".format(expected_password_file,
                                                                                               actual_file))  # noqa: E50

    def test_load_ini_logical_config(self):
        config = configparser.ConfigParser()
        # Preserve the case of elements.
        config.optionxform = str
        config.read(get_path('tool_test/ini', 'logical_config.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)

        cfg = test_config.logical_config['my_logical_query']
        self.assertTrue(test_config.logical_config_name == 'my_logical_query')
        self.assertTrue(cfg['tablename'] == 'CRAZYTABLE_$dsName')
        self.assertTrue(cfg['tablePrefix'] == '[LOCO].')
        self.assertTrue(cfg['tablenameUpper'] == 'True')

    def test_load_windows_override(self):
        ini_file = get_path('tool_test/ini', 'windows_override.ini', __name__)
        reg = datasource_list.TestRegistry('')
        reg.load_registry(ini_file)

        # Duplicates should be removed and the order preserved.
        standard = ['teradata', 'netezza']
        all_passing = ['teradata', 'netezza', 'bigquery', 'exasolution']
        all_test = ['hadoophive2_hortonworks', 'teradata', 'netezza', 'bigquery', 'exasolution']
        all_test2 = ['hadoophive2_hortonworks', 'teradata', 'netezza', 'bigquery', 'exasolution']

        self.assertTrue(standard == reg.get_datasources(['standard']))
        self.assertTrue(all_passing == reg.get_datasources(['all_passing']))
        self.assertTrue(all_test == reg.get_datasources(['all_test']))
        self.assertTrue(all_test2 == reg.get_datasources(['all_test2']))

    def test_load_command_line_override(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'override.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        list_of_test_sets = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.bigquery', 'cast_calcs.bigquery.tds',
                               '', 'logicaltests/setup/calcs/setup.*.bigquery.xml', test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.bigquery', 'Staples.bigquery.tds',
                               '', 'logicaltests/setup/staples/setup.*.bigquery.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.bigquery',
                                  'cast_calcs.bigquery.tds', '', 'exprtests/standard/setup.*.txt', test_config.dsname)

        tests = [test1, test2, test3]

        self.assertTrue(test_config.run_time_config.d_override == 'WorkFaster=True Override=TurnOff:yes,TurnOn:no',
                        'Override did not match: ' + test_config.run_time_config.d_override)

        for test in tests:
            found = [y for y in list_of_test_sets if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]; found {1}".format(test, found))

    def test_load_tabquery_override(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'postgres_jdbc_tabquerytool.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)

        if sys.platform.startswith('darwin') and platform.machine() == 'arm64':
            self.assertTrue(test_config.run_time_config.tabquery_paths.get_path("darwin") == 'tabquerytool_mac_arm')
        else:
            self.assertTrue(test_config.run_time_config.tabquery_paths.get_path("darwin") == 'tabquerytool_mac')
        self.assertTrue(test_config.run_time_config.tabquery_paths.get_path("linux") == 'tabquerytool_linux')
        self.assertTrue(test_config.run_time_config.tabquery_paths.get_path("win32") == 'tabquerytool_windows.exe')

    def test_load_ini_bigquery_sql(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'bigquery_sql.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.bigquery_sql',
                               'cast_calcs.bigquery_sql.tds', '', 'logicaltests/setup/calcs/setup.*.bigquery_sql.xml',
                               test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.bigquery_sql',
                               'Staples.bigquery_sql.tds', 'Filter.Trademark',
                               'logicaltests/setup/staples/setup.*.bigquery_sql.xml', test_config.dsname)

        test3 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.lod.bigquery_sql',
                               'Staples.bigquery_sql.tds', '', 'logicaltests/setup/lod/setup.*.bigquery_sql.xml',
                               test_config.dsname)

        test4 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.bigquery_sql',
                                  'cast_calcs.bigquery_sql.tds',
                                  'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls,logical',
                                  'exprtests/standard/setup.*.txt', test_config.dsname)

        test5 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression_test_dates.bigquery_sql',
                                  'cast_calcs.bigquery_sql_dates.tds',
                                  'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls',
                                  'exprtests/standard/', test_config.dsname)

        test6 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression_test_dates2.bigquery_sql',
                                  'cast_calcs.bigquery_sql_dates2.tds',
                                  'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls',
                                  'exprtests/standard/', test_config.dsname)

        test7 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.lod.bigquery_sql',
                                  'cast_calcs.bigquery_sql.tds', '', 'exprtests/lodcalcs/setup.*.txt',
                                  test_config.dsname)

        test8 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical_test_dates.bigquery_sql',
                               'cast_calcs.bigquery_sql.tds', '', 'exprtests/standard/setup.*.bigquery_dates.xml',
                               test_config.dsname)

        tests = [test1, test2, test3, test4, test5, test6, test7, test8]

        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_staplesdata_on(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'staples_data.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.staples.bigquery',
                                  'Staples.bigquery.tds', '', 'exprtests/staples/setup.*.txt', test_config.dsname)

        tests = [test1]
        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_staplesdata_off(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'staples_data_off.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        self.assertTrue(not x)

    def test_load_run_as_perf_not_set(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'perf_notset.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        self.assertFalse(test_config.run_time_config.run_as_perf,
                         'run_as_perf did not match: ' + str(test_config.run_time_config.run_as_perf))

    def test_load_run_as_perf_true(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'perf_true.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        self.assertTrue(test_config.run_time_config.run_as_perf,
                        'run_as_perf did not match: ' + str(test_config.run_time_config.run_as_perf))

    def test_load_run_as_perf_false(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'perf_false.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        self.assertFalse(test_config.run_time_config.run_as_perf,
                         'run_as_perf did not match: ' + str(test_config.run_time_config.run_as_perf))


class PrintConfigurationsTest(unittest.TestCase):
    def test_print_configuration_with_no_dsname_and_no_ds_all_returns_explanation(self):
        with mock.patch('tdvt.config_gen.datasource_list.TestRegistry.get_datasources', side_effect=TypeError):
            captured_output = io.StringIO()
            sys.stdout = captured_output  # redirect stdout to a StringIO obj to catch the print statement.
            datasource_list.print_configurations(datasource_list.TestRegistry('test'), None, None)
            self.assertIn(datasource_list.RUN_IN_INCORRECT_DIRECTORY_MSG, captured_output.getvalue())

    def test_print_configuration_with_no_dsname(self):
        with mock.patch('tdvt.config_gen.datasource_list.TestRegistry') as MockTestRegistry:
            MockTestRegistry.suite_map = {'all': ['postgres_jdbc', 'postgres_odbc']}
            MockTestRegistry.get_datasources.return_value = ['postgres_jdbc', 'postgres_odbc']
            correct_out = "\nAvailable datasources:\npostgres_jdbc\npostgres_odbc\n\nAvailable suites:\nall\n\tpostgres_jdbc, postgres_odbc"
            captured_output = io.StringIO()
            sys.stdout = captured_output
            datasource_list.print_configurations(MockTestRegistry, None, None)
            self.assertIn(correct_out, captured_output.getvalue())


class MockTestSet(TestSet):
    def __init__(self, mock_test_path, mock_test_name, ds_name, root_dir, config_name, tds_name, exclusions,
                 test_pattern, is_logical, suite_name, password_file, expected_message):
        super(MockTestSet, self).__init__(ds_name, root_dir, config_name, tds_name, exclusions, test_pattern,
                                          is_logical, suite_name, password_file, expected_message, False, True, False)
        self.mock_test_name = mock_test_name
        self.mock_test_path = mock_test_path

    def get_expected_output_file_path(self, test_file, output_dir):
        return self.mock_test_path + 'actual.' + self.mock_test_name


class MockBatchQueueWork(tdvt_core.BatchQueueWork):
    def __init__(self, mock_tests: List[MockTestSet], test_config: TdvtInvocation, test_set: MockTestSet,
                 runtime_exception=None):
        super(MockBatchQueueWork, self).__init__(test_config, test_set)
        self.keep_actual_file = True
        self.runtime_exception = runtime_exception
        self.mock_tests = mock_tests

    def setup_files(self, test_list):
        pass

    def run_process(self, cmdline):
        if self.runtime_exception:
            raise self.runtime_exception
        pass


class ResultsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_results_passed(self):
        test_name = 'setup.mytest.txt'
        test_path = './tests/e/suite1/'
        mock_batch = self.create_mock_and_process(test_name, test_path)

        self.assertEqual(len(mock_batch.results), 1)
        for test_file in mock_batch.results:
            self.assertTrue(mock_batch.results[test_file].all_passed())

    def test_results_missing_actual(self):
        test_name = 'setup.mytest.txt'
        test_path = './tests/e/suite1/missing_actual_1/'
        mock_batch = self.create_mock_and_process(test_name, test_path)

        self.assertTrue(len(mock_batch.results) == 1)
        for test_file in mock_batch.results:
            self.assertFalse(mock_batch.results[test_file].all_passed())
            self.assertIsInstance(mock_batch.results[test_file].error_status, TestErrorMissingActual)
            self.assertIsInstance(mock_batch.results[test_file].test_case_map[0].error_type, TestErrorMissingActual)
            self.assertFalse(mock_batch.results[test_file].test_case_map[0].all_passed())

    def test_results_missing_tuple(self):
        test_name = 'setup.mytest.txt'
        test_path = './tests/e/suite1/failed_1/'
        mock_batch = self.create_mock_and_process(test_name, test_path)

        self.assertEqual(len(mock_batch.results), 1)

        for test_file in mock_batch.results:
            self.assertFalse(mock_batch.results[test_file].all_passed())
            self.assertIsInstance(mock_batch.results[test_file].error_status, TestErrorResults)
            self.assertEqual(mock_batch.results[test_file].diff_count, 17)

    def create_mock_and_process(self, test_name, test_path):
        mock_tests = [TestFile('tests', test_path + test_name)]
        test_config = TdvtInvocation()
        ts1_expr = MockTestSet(test_path, test_name, 'mock ds', 'tests', 'mock config', 'mock.tds', '', 'tests/*.txt',
                               False, 'mock suite expression', '', '')
        mock_batch = MockBatchQueueWork(mock_tests, test_config, ts1_expr)
        mock_batch.run(mock_batch.mock_tests)
        mock_batch.process_test_results(mock_batch.mock_tests)
        return mock_batch

    def test_results_wrong_value(self):
        test_name = 'setup.mytest.txt'
        test_path = './tests/e/suite1/tuple_1/'
        mock_batch = self.create_mock_and_process(test_name, test_path)

        self.assertEqual(len(mock_batch.results), 1)
        for test_file in mock_batch.results:
            self.assertFalse(mock_batch.results[test_file].all_passed())
            self.assertIsInstance(mock_batch.results[test_file].error_status, TestErrorResults)
            self.assertEqual(mock_batch.results[test_file].diff_count, 1)


class ResultsExceptionTest(unittest.TestCase):
    def setUp(self):
        self.mock_tests = [TestFile('tests', './tests/e/suite1/setup.mytest.txt')]
        self.test_config = TdvtInvocation()
        self.ts1_expr = MockTestSet('not used', 'not used', 'mock ds', 'tests', 'mock config', 'mock.tds', '',
                                    'tests/*.txt', False, 'mock suite expression', '', '')

    def tearDown(self):
        pass

    def test_runtime_error(self):
        error_message = 'Mock RunTime Error'
        error_state = TestErrorOther
        mock_batch = MockBatchQueueWork(self.mock_tests, self.test_config, self.ts1_expr, RuntimeError(error_message))

        self.check_errors(error_message, error_state, mock_batch)

    def test_process_error_timeout(self):
        error_message = 'Test timed out.'
        error_state = TestErrorTimeout
        mock_batch = MockBatchQueueWork(self.mock_tests, self.test_config, self.ts1_expr,
                                        subprocess.TimeoutExpired('test', 1))

        self.check_errors(error_message, error_state, mock_batch)

    def test_process_error_abort(self):
        error_message = 'error message from exception'
        error_state = TestErrorAbort
        proc_error_code = 18
        mock_batch = MockBatchQueueWork(self.mock_tests, self.test_config, self.ts1_expr,
                                        subprocess.CalledProcessError(proc_error_code, 'test', error_message))
        self.check_errors(error_message, error_state, mock_batch)

    def test_process_error_other(self):
        error_message = 'error message from exception'
        error_state = TestErrorOther
        proc_error_code = 1
        mock_batch = MockBatchQueueWork(self.mock_tests, self.test_config, self.ts1_expr,
                                        subprocess.CalledProcessError(proc_error_code, 'test', error_message))
        self.check_errors(error_message, error_state, mock_batch)

    def test_process_error_expected(self):
        error_state = TestErrorExpected
        proc_error_code = 1
        test_set_expected = MockTestSet('not_used', 'not used', 'mock ds', 'tests', 'mock config', 'mock.tds', '',
                                        'tests/*.txt', False, 'mock suite expression', '', '')
        test_set_expected.expected_message = 'No one expects the Spanish Inquisition'
        error_message = 'some stuff ' + test_set_expected.expected_message + ' some other stuff'
        mock_batch = MockBatchQueueWork(self.mock_tests, self.test_config, test_set_expected,
                                        subprocess.CalledProcessError(proc_error_code, 'test', error_message))
        self.check_errors(error_message, error_state, mock_batch)

        for test_file in mock_batch.results:
            actual_message = mock_batch.results[test_file].get_failure_message_or_all_exceptions()
            self.assertIsInstance(mock_batch.results[test_file].test_case_map[0].error_type, error_state)
            self.assertTrue(mock_batch.results[test_file].test_case_map[0].all_passed())

    def test_process_error_output_json_expected(self):
        error_state = TestErrorExpected
        proc_error_code = 1
        test_set_expected = MockTestSet('not_used', 'not used', 'mock ds', 'tests', 'mock config', 'mock.tds', '',
                                        'tests/*.txt', False, 'mock suite expression', '', '')
        test_set_expected.expected_message = 'Invalid username or password'
        error_message = test_set_expected.expected_message
        mock_batch = MockBatchQueueWork(self.mock_tests, self.test_config, test_set_expected,
                                        subprocess.CalledProcessError(proc_error_code, 'test', error_message))
        self.check_errors(error_message, error_state, mock_batch)

        for test_file in mock_batch.results:
            json_str = json.dumps(mock_batch.results[test_file], cls=TestOutputJSONEncoder)
            json_object = json.loads(json_str)
            self.assertEqual(json_object['expected_message'], error_message)
            self.assertIsInstance(mock_batch.results[test_file].test_case_map[0].error_type, error_state)
            self.assertTrue(mock_batch.results[test_file].test_case_map[0].all_passed())

    def test_process_error_output_json_not_expected(self):
        error_state = TestErrorExpected
        proc_error_code = 1
        test_set_expected = MockTestSet('not_used', 'not used', 'mock ds', 'tests', 'mock config', 'mock.tds', '',
                                        'tests/*.txt', False, 'mock suite expression', '', '')
        test_set_expected.expected_message = 'Invalid username or password'
        error_message = test_set_expected.expected_message
        mock_batch = MockBatchQueueWork(self.mock_tests, self.test_config, test_set_expected,
                                        subprocess.CalledProcessError(proc_error_code, 'test', error_message))
        self.check_errors(error_message, error_state, mock_batch)

        for test_file in mock_batch.results:
            json_str = json.dumps(mock_batch.results[test_file], cls=TestOutputJSONEncoder)
            json_object = json.loads(json_str)
            self.assertEqual(json_object['expected_message'], error_message)
            self.assertIsInstance(mock_batch.results[test_file].test_case_map[0].error_type, error_state)
            self.assertTrue(mock_batch.results[test_file].test_case_map[0].all_passed())

    def test_process_timeout_multiple(self):
        test_name = 'setup.mytest.txt'
        test_name2 = 'setup.mytest2.txt'
        test_path = './tests/e/suite1/missing_actual_1/'
        mock_tests = [TestFile('tests', test_path + test_name), TestFile('tests', test_path + test_name2)]
        ts1_expr = MockTestSet(test_path, test_name, 'mock ds', 'tests', 'mock config', 'mock.tds', '', 'tests/*.txt',
                               False, 'mock suite expression', '', '')
        mock_batch = MockBatchQueueWork(mock_tests, self.test_config, ts1_expr, subprocess.TimeoutExpired('test', 1))

        error_message = 'Test timed out.'
        error_state = TestErrorTimeout
        self.check_errors(error_message, error_state, mock_batch, 2)

    def check_errors(self, expected_message, expected_state, mock_batch, error_count=1):
        mock_batch.run(mock_batch.mock_tests)
        mock_batch.process_test_results(mock_batch.mock_tests)

        self.assertEqual(len(mock_batch.results), error_count)
        for test_file in mock_batch.results:
            actual_message = mock_batch.results[test_file].get_failure_message_or_all_exceptions()
            self.assertTrue(actual_message == expected_message,
                            "Expected [{0}] got [{1}]".format(expected_message, actual_message))
            self.assertIsInstance(mock_batch.results[test_file].error_status, expected_state)

    def test_get_cleaned_results(self):
        srcfile = TEST_DIRECTORY + '/exprtests/expected.setup.agg.avg.txt'
        cleaned_results = get_cleaned_results(srcfile)
        self.assertIn("AVG([int0])'>\n    <table>", cleaned_results)
        self.assertIn("AVG([num4])'>\n    <table>", cleaned_results)


class TabQueryPathTest(unittest.TestCase):
    def test_init(self):
        t = TabQueryPath('linux/linux', 'mac/mac/mac', 'mac_arm/mac_arm/mac_arm', 'win\\win.exe')
        if sys.platform.startswith("darwin"):
            if platform.machine() == 'arm64':
                self.assertTrue(str(t.get_path('darwin')) == 'mac_arm/mac_arm/mac_arm')
            else:
                self.assertTrue(str(t.get_path('darwin')) == 'mac/mac/mac')
        self.assertTrue(str(t.get_path('linux')) == 'linux/linux')
        self.assertTrue(str(t.get_path('windows')) == 'win\\win.exe')

    def test_string(self):
        t = TabQueryPath('linux', 'mac', 'mac_arm', 'win')
        if sys.platform.startswith("darwin"):
            if platform.machine() == 'arm64':
                self.assertTrue(t.get_path('darwin') == 'mac_arm')
            else:
                self.assertTrue(t.get_path('darwin') == 'mac')
        self.assertTrue(t.get_path('linux') == 'linux')
        self.assertTrue(t.get_path('windows') == 'win')

        string_value = t.to_array()
        self.assertTrue(string_value[0] == 'linux')
        self.assertTrue(string_value[1] == 'mac')
        self.assertTrue(string_value[2] == 'mac_arm')
        self.assertTrue(string_value[3] == 'win')
        t2 = TabQueryPath.from_array(string_value)
        if sys.platform.startswith("darwin"):
            if platform.machine() == 'arm64':
                self.assertTrue(t2.get_path('darwin') == 'mac_arm')
            else:
                self.assertTrue(t2.get_path('darwin') == 'mac')
        self.assertTrue(t2.get_path('linux') == 'linux')
        self.assertTrue(t2.get_path('windows') == 'win')


class TestCreatorTest(unittest.TestCase):
    test_creator = TestCreator('tool_test/test_generation/full_map_to_calcs.json', 'good_ds')
    tc_with_one_data_type = TestCreator('tool_test/test_generation/only_one_data_type.json', 'one_data_type_ds')
    tc_with_perfect_match = TestCreator('tool_test/test_generation/full_map_to_calcs.json', 'perfect_match_ds')
    tc_missing_t0 = TestCreator('tool_test/test_generation/full_map_to_calcs_missing_t0.json', 'missing_t0_ds')
    headers = test_creator._json_to_header_list()

    def test_bad_csv_path(self):
        bad_test_creator = TestCreator('bad.csv', 'bad-ds')
        self.assertFalse(bad_test_creator._check_output_dir_and_input_json_exist())

    def test_csv_path(self):
        self.assertTrue(self.test_creator._check_output_dir_and_input_json_exist())

    def test_csv_to_list_returns_all_cols(self):
        self.assertEqual(len(self.headers), 27)

    def test_headers_are_correct(self):
        self.assertEqual(
            self.headers[0:5],
            ['k',
             'n0',
             'n1',
             'n2',
             'n3',
             ]
        )

    def test_return_user_data_cols(self):
        self.assertEqual(
            self.tc_with_one_data_type._map_user_cols_to_test_cols(),
            {'txt': {'empties': False,
                     'negatives': False,
                     'nulls': True,
                     'type': 'VARCHAR'},
             'txt2': {'empties': False,
                      'negatives': True,
                      'nulls': False,
                      'type': 'VARCHAR'},
             'txt3': {'empties': True,
                      'negatives': False,
                      'nulls': True,
                      'type': 'VARCHAR'},
             'txt4': {'empties': True,
                      'negatives': False,
                      'nulls': False,
                      'type': 'VARCHAR'},
             'txt5': {'empties': False,
                      'negatives': False,
                      'nulls': False,
                      'type': 'VARCHAR'}}
        )

    def test_map_user_cols_to_test_cols(self):
        self.assertEqual(
            self.tc_with_one_data_type.map_user_cols_to_test_args(),
            {'bool0': [],
             'bool1': [],
             'bool2': [],
             'bool3': [],
             'date0': [],
             'date1': [],
             'date2': [],
             'date3': [],
             'datetime0': [],
             'datetime1': ['txt3'],
             'int0': [],
             'int1': [],
             'int2': [],
             'int3': [],
             'key': ['txt5'],
             'num0': [],
             'num1': [],
             'num2': [],
             'num3': [],
             'num4': [],
             'str0': ['txt5'],
             'str1': ['txt5'],
             'str2': ['txt'],
             'str3': ['txt'],
             'time0': [],
             'time1': [],
             'zzz': ['txt5']
             }
        )

    def test_map_user_cols_to_test_cols_perfect_match(self):
        self.assertEqual(
            self.tc_with_perfect_match.map_user_cols_to_test_args(),
            {'bool0': ['b0', 'b1', 'b3'],
             'bool1': ['b0', 'b1', 'b3'],
             'bool2': ['b2'],
             'bool3': ['b0', 'b1', 'b3'],
             'date0': ['d0', 'd3'],
             'date1': ['d1', 'd2'],
             'date2': ['d1', 'd2'],
             'date3': ['d0', 'd3'],
             'datetime0': ['t0', 'dt0'],
             'datetime1': ['dt1'],
             'int0': ['i0'],
             'int1': ['i1'],
             'int2': ['i2'],
             'int3': ['i3'],
             'key': ['k', 's0', 's1', 'z'],
             'num0': ['n0', 'n4'],
             'num1': ['n1'],
             'num2': ['n2'],
             'num3': ['n3'],
             'num4': ['n0', 'n4'],
             'str0': ['k', 's0', 's1', 'z'],
             'str1': ['k', 's0', 's1', 'z'],
             'str2': ['s2', 's3'],
             'str3': ['s2', 's3'],
             'time0': ['t0', 'dt0'],
             'time1': ['t1'],
             'zzz': ['k', 's0', 's1', 'z']}
        )

    def test_map_user_cols_to_test_cols_missing_t0(self):
        self.assertEqual(
            self.tc_missing_t0.map_user_cols_to_test_args(),
            {'bool0': ['b0', 'b1', 'b3'],
             'bool1': ['b0', 'b1', 'b3'],
             'bool2': ['b2'],
             'bool3': ['b0', 'b1', 'b3'],
             'date0': ['d0', 'd3'],
             'date1': ['d1', 'd2'],
             'date2': ['d1', 'd2'],
             'date3': ['d0', 'd3'],
             'datetime0': ['dt0'],
             'datetime1': ['dt1'],
             'int0': ['i0'],
             'int1': ['i1'],
             'int2': ['i2'],
             'int3': ['i3'],
             'key': ['k', 's0', 's1', 'z'],
             'num0': ['n0', 'n4'],
             'num1': ['n1'],
             'num2': ['n2'],
             'num3': ['n3'],
             'num4': ['n0', 'n4'],
             'str0': ['k', 's0', 's1', 'z'],
             'str1': ['k', 's0', 's1', 'z'],
             'str2': ['s2', 's3'],
             'str3': ['s2', 's3'],
             'time0': ['dt0'],
             'time1': ['t1'],
             'zzz': ['k', 's0', 's1', 'z']}
        )

class MangleTest(unittest.TestCase):

    with open('tool_test/tds/cast_calcs.tde.tds', 'r') as f:
        new_lines = updated_tds_as_str(f, 'sqlserver_connection')

    with open('tool_test/tds/cast_calcs.postgres.tds', 'r') as postgres:
        postgres_tds = updated_tds_as_str(postgres, 'postgres_connection')

    with open('tool_test/tds/cast_calcs.hana.tds', 'r') as hana:
        hana_tds = updated_tds_as_str(hana, 'hana_connection')


    def test_mangletds_tdvtconnection(self):

        self.assertIn(
            "<connection tdvtconnection='sqlserver_connection' authentication='sqlserver' class='sqlserver' dbname='TestV1' odbc-native-protocol='yes' one-time-sql='' server='mssql2014' username='test' />",
            self.new_lines
        )
        self.assertIn(
            "<connection tdvtconnection='postgres_connection' authentication='username-password' class='postgres' dbname='TestV1' one-time-sql='' port='1234' server='postgres.server' username='test' />",
            self.postgres_tds
        )
        self.assertIn(
            "<connection tdvtconnection='hana_connection' authentication='username-password' class='saphana' connection-type='SingleNode' one-time-sql='' port='11235' schema='TESTV1' server='hana.harvey.hamster' sslcert='' sslmode='' username='harvey_wonder_hamster' workgroup-auth-mode=''>",
            self.hana_tds
        )

    def test_mangletds_relation_connection(self):
        self.assertIn(
            "<relation connection='leaf' name='Calcs' table='[dbo].[Calcs]' type='table' />",
            self.new_lines
        )
        self.assertIn(
            "<relation connection='leaf' name='Calcs' table='[public].[Calcs]' type='table' />",
            self.postgres_tds
        )
        self.assertIn(
            "<_.fcp.ObjectModelEncapsulateLegacy.false...relation connection='leaf' name='Calcs' table='[public].[Calcs]' type='table' />",
            self.postgres_tds
        )
        self.assertIn(
            "<_.fcp.ObjectModelEncapsulateLegacy.true...relation connection='leaf' name='Calcs' table='[public].[Calcs]' type='table' />",
            self.postgres_tds
        )
        self.assertIn(
            "<relation connection='leaf' name='Calcs' table='[TESTV1].[Calcs]' type='table' />",
            self.hana_tds
        )
        self.assertIn(
            "<_.fcp.ObjectModelEncapsulateLegacy.false...relation connection='leaf' name='Calcs' table='[TESTV1].[Calcs]' type='table' />",
            self.hana_tds
        )

    def test_mangletds_named_connection(self):
        self.assertIn(
            "<named-connection caption='mssql2014' name='leaf'>",
            self.new_lines
        )
        self.assertIn(
            "<named-connection caption='postgres.server' name='leaf'>",
            self.postgres_tds
        )
        self.assertIn(
            "<named-connection name='leaf'>",
            self.hana_tds
        )

class TestOutputFilesTest(unittest.TestCase):
    good_test_results = TestOutputFiles()
    good_test_results.combined_output = [
        {'Suite': 'postgres', 'Test Set': 'StaplesConnectionTestpostgres', 'TDSName': 'Staples.postgres',
         'TestName': 'staples.connection.test',
         'TestPath': 'path/to/tdvt/root/logicaltests/setup/connection_test/setup.staples.connection.test.simple.xml',
         'Passed': 'True', 'Closest Expected': '0', 'Diff count': '0',
         'Test Case': 'path/to/tdvt/root/tdvt/tdvt/tdvt/logicaltests/setup/connection_test/setup.staples.connection.test.simple.xml',
         'Test Type': 'logical', 'Priority': 'unknown', 'Categories': 'unknown', 'Functions': 'unknown',
         'Process Output': 'Attempting to run query...\nRun query successful! Check output file\n', 'Error Msg': 'None',
         'Error Type': 'None', 'Query Time (ms)': '169.0',
         'Generated SQL': '\n      SELECT "Staples"."Discount" AS "Ship Priority"\nFROM "Staples"\nGROUP BY 1\n    ',
         'Actual (100)tuples': '"0"\n"0.01"\n"0.02"\n"0.03"\n"0.04"\n"0.05"\n"0.06"\n"0.07"\n"0.08"\n"0.09"\n"0.1"\n"0.11"\n"0.12"\n"0.13"\n"0.15"\n"0.21"\n"0.24"\n"0.27"\n"0.3"\n"0.36"\n"0.39"',
         'Expected (100)tuples': '"0"\n"0.01"\n"0.02"\n"0.03"\n"0.04"\n"0.05"\n"0.06"\n"0.07"\n"0.08"\n"0.09"\n"0.1"\n"0.11"\n"0.12"\n"0.13"\n"0.15"\n"0.21"\n"0.24"\n"0.27"\n"0.3"\n"0.36"\n"0.39"'},
        {'Suite': 'postgres', 'Test Set': 'CastCalcsConnectionTestpostgres', 'TDSName': 'cast_calcs.postgres',
         'TestName': 'calcs_connection_test',
         'TestPath': 'path/to/tdvt/root/tdvt/tdvt/tdvt/exprtests/pretest/connection_tests/calcs/setup.calcs_connection_test.txt',
         'Passed': 'True', 'Closest Expected': '0', 'Diff count': '0', 'Test Case': 'key', 'Test Type': 'expression',
         'Priority': 'unknown', 'Categories': 'unknown', 'Functions': 'unknown', 'Process Output': '',
         'Error Msg': 'None', 'Error Type': 'None', 'Query Time (ms)': '200.0',
         'Generated SQL': '\n      SELECT "Calcs"."key" AS "TEMP(Test)(3382465274)(0)"\nFROM "Calcs"\nGROUP BY 1\n    ',
         'Actual (100)tuples': '"key00"\n"key01"\n"key02"\n"key03"\n"key04"\n"key05"\n"key06"\n"key07"\n"key08"\n"key09"\n"key10"\n"key11"\n"key12"\n"key13"\n"key14"\n"key15"\n"key16"',
         'Expected (100)tuples': '"key00"\n"key01"\n"key02"\n"key03"\n"key04"\n"key05"\n"key06"\n"key07"\n"key08"\n"key09"\n"key10"\n"key11"\n"key12"\n"key13"\n"key14"\n"key15"\n"key16"'}]

    def test_logical_test_return(self):
        cmd_line = get_failed_cmd_line(self.good_test_results, 0)
        expected = 'python -m run-pattern postgres --logp path/to/tdvt/root/logicaltests/setup/connection_test/setup.staples.connection.test.simple.xml --tdp Staples.postgres.tds'
        self.assertEqual(cmd_line, expected)

    def test_expression_test_return(self):
        cmd_line = get_failed_cmd_line(self.good_test_results, 1)
        expected = 'python -m run-pattern postgres --exp path/to/tdvt/root/tdvt/tdvt/tdvt/exprtests/pretest/connection_tests/calcs/setup.calcs_connection_test.txt --tdp cast_calcs.postgres.tds'
        self.assertEqual(cmd_line, expected)


class Do_WorkFunctionTest(unittest.TestCase):
    def setUp(self):
        error_message = 'Mock RunTime Error'
        self.mock_tests = [TestFile('tests', './tests/e/suite1/setup.mytest.txt')]
        self.test_config = TdvtInvocation()
        self.ts1_expr = MockTestSet('not used', 'not used', 'mock ds', 'tests', 'mock config', 'mock.tds', '',
                                    'tests/*.txt', False, 'mock suite expression', '', '')
        self.mock_batch = MockBatchQueueWork(self.mock_tests, self.test_config, self.ts1_expr)

    def tearDown(self):
        pass

    def test_mock_batch_init(self):
        self.assertIsInstance(self.mock_batch, MockBatchQueueWork)

    def test_mock_batch_do_work(self):
        do_work(self.mock_batch)
        self.assertEqual(self.mock_batch.error_state, None)

    def test_mock_batch_do_work_disabled_test(self):
        self.mock_batch.test_set.test_is_enabled = False
        do_work(self.mock_batch)

        self.assertIsInstance(self.mock_batch.error_state, TestErrorDisabledTest)

    def test_mock_batch_do_work_skipped_test(self):
        self.mock_batch.test_set.test_is_skipped = True
        do_work(self.mock_batch)

        self.assertIsInstance(self.mock_batch.error_state, TestErrorSkippedTest)


class ToleranceTest(unittest.TestCase):
    """
    The TestResult.actual_expected_comparison() method returns True when actual & expected match, and False if there is
    no match.
    """
    tr = TestResult()

    def test_actual_expected_nulls_that_match_no_tolerance(self):

        self.assertTrue(
            self.tr.actual_expected_comparison('%null%', '%null%', None, False)
        )

    def test_actual_expected_nulls_match_with_tolerance_and_data_type(self):
        self.assertTrue(
            self.tr.actual_expected_comparison('%null%', '%null%', 0.05, True, 'float')
        )

    def test_actual_is_null_expected_is_float(self):
        self.assertFalse(
            self.tr.actual_expected_comparison('1.001', '%null%', 0.05, True, 'float')
        )

    def test_actual_expected_comparison_method_no_match_no_tolerance(self):
        self.assertFalse(
            self.tr.actual_expected_comparison('1', '2', None, False)
        )

    def test_actual_expected_comparison_method_no_match_no_tolerance_loose_enabled(self):
        self.assertFalse(
            self.tr.actual_expected_comparison('1', '2', None, True)
        )

    def test_actual_expected_comparison_method_match_with_or_without_tolerance(self):
        self.assertTrue(
            self.tr.actual_expected_comparison('1.01', '1.01', 0.05, True, 'float')
        )

    def test_actual_expected_comparison_method_match_with_or_without_tolerance_loose_disabled(self):
        self.assertTrue(
            self.tr.actual_expected_comparison('1.01', '1.01', 0.05, False, 'float')
        )

    def test_actual_expected_comparison_method_match_only_with_tolerance(self):
        self.assertTrue(
            self.tr.actual_expected_comparison('1.01', '1.05', 0.05, True, 'float')
        )

    def test_actual_expected_comparison_method_no_match_with_tolerance(self):
        self.assertFalse(
            self.tr.actual_expected_comparison('1.01', '1.25', 0.05, True, 'float')
        )

    def test_actual_expected_comparison_tolerance_with_trailing_zeors(self):
        # this test is for GitHub Issue 1178
        self.assertTrue(
            self.tr.actual_expected_comparison('1.01', '1.0100000', 0.05, True, 'float')
        )

    def test_actual_is_float_expected_is_int_with_tolerance(self):
        self.assertTrue(
            self.tr.actual_expected_comparison('1', '1.01', 0.05, True, 'float')
        )

    def test_actual_is_int_expected_is_float_with_tolerance(self):
        self.assertTrue(
           self.tr.actual_expected_comparison('1.01', '1', 0.05, True, 'float')
        )

    def test_comparison_method_with_tolerance_but_no_datatype_matches(self):
        self.assertTrue(
            self.tr.actual_expected_comparison('1.01', '1.01', 0.05, True, None)
        )

    def test_comparison_method_with_tolerance_but_no_datatype_does_not_match(self):
        self.assertFalse(
            self.tr.actual_expected_comparison('1.01', '1.25', 0.05, True, None)
        )

    def test_comparison_method_with_datatype_only(self):
        self.assertTrue(
            self.tr.actual_expected_comparison('1.01', '1.01', None, True, 'float')
        )

    def test_comparison_method_with_datatype_only_does_not_match(self):
        self.assertFalse(
            self.tr.actual_expected_comparison('1.01', '1.25', None, True, 'float')
        )

    def test_comparison_method_with_null_as_actual(self):
        self.assertFalse(
            self.tr.actual_expected_comparison('1.00', '%null%', .05, True, 'float')
        )


ROOT_DIRECTORY = pkg_resources.resource_filename(__name__, '')
TEST_DIRECTORY = pkg_resources.resource_filename(__name__, 'tool_test')
print("Using root dir " + str(ROOT_DIRECTORY))
print("Using test dir " + str(TEST_DIRECTORY))
logging.basicConfig(filename='tdvt_test_log.txt', level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
configure_tabquery_path()
if __name__ == '__main__':
    logging.debug("Starting TDVT tests\n")

    unittest.main()

    logging.debug("Ending TDVT tests\n")
