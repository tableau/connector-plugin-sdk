"""
    Tableau Datasource Verification Tool Tester - TDVTT
    Test the TDVT.

    Run from the 'test' directory. The path to tabquerycli is configured in test/config/tdvt.
    You can run these like:
    All tests:
        py -3 -m tdvt_test
    A Class:
        py -3 -m tdvt_test ReRunFailedTestsTest
    One specific test:
        py -3 -m tdvt_test ReRunFailedTestsTest.test_logical_rerun_fail

"""


import configparser
import io
import logging
import os
import pkg_resources
import shutil
import sys
import unittest

from unittest import mock

from defusedxml.ElementTree import parse,ParseError

from tdvt import tdvt_core
from tdvt.tdvt import enqueue_failed_tests
from tdvt.config_gen import tdvtconfig
from tdvt.config_gen import datasource_list
from tdvt.config_gen.test_config import ExpressionTestSet, LogicalTestSet, TestFile
from tdvt.resources import get_path, make_temp_dir
from tdvt.test_results import *
from tdvt.tabquery import *


class DiffTest(unittest.TestCase):
    def test_diff(self):
        logging.debug("Starting diff tests:\n")
        subdir = 'diff_tests'
        #Go through the 'expected' files as the driver.
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
            if 'expected.sql' in test:
                compare_sql = True
            if 'expected.tuples' in test:
                compare_tuples = True
            if 'expected.both' in test:
                compare_tuples = True
                compare_sql = True
            test_config = TdvtTestConfig(compare_sql, compare_tuples)
            results = tdvt_core.TestResult(test_config=test_config)
            results.add_test_results(actual_xml, actual_file)
            expected_output = tdvt_core.TestResult(test_config=test_config)
            expected_output.add_test_results(expected_xml, '')

            num_diffs, diff_string = tdvt_core.diff_test_results(results, expected_output)
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
        self.test_config = TdvtTestConfig()
        self.test_config.output_dir = make_temp_dir([self.test_config.suite_name])

    def tearDown(self):
        shutil.rmtree(self.test_config.output_dir)

    def check_results(self, test_results, total_test_count, should_pass=True):
        test_status_expected = "passed" if should_pass else "failed"
        #Make sure we ran the right number of tests and that they all passed.
        self.assertTrue(len(test_results) == total_test_count, "Did not run the right number of tests.")
        for path, test_result in test_results.items():
            passed = test_result is not None
            passed = passed and test_result.all_passed()
            test_status = "passed" if passed else "failed"
            self.assertTrue(passed == should_pass,
                            "Test [{0}] {1} but should have {2}.".format(path, test_status, test_status_expected))

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
        #Tests picking a local test suite.
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
        all_test_results = {}
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
        #This will cause the test to fail as expected.
        self.test_config.tested_sql = True
        all_test_results = tdvt_core.run_tests_impl(self.config_set, self.test_config)
        tdvt_core.write_standard_test_output(all_test_results, self.test_dir)

        self.check_results(all_test_results, 1, False)

        # Now rerun the failed tests which should fail again,
        # indicating that the 'tested_sql' option was persisted correctly.

        tests = enqueue_failed_tests(get_path('tool_test', 'tdvt_output.json', __name__), TEST_DIRECTORY, None)
        all_test_results = tdvt_core.run_tests_serial(tests)

        self.check_results(all_test_results, 1, False)

    def test_logical_rerun(self):
        tests = enqueue_failed_tests(get_path('tool_test/rerun_failed_tests', 'logical.json', __name__),
                                     TEST_DIRECTORY, None)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 1)

    def test_expression_rerun(self):
        tests = enqueue_failed_tests(get_path('tool_test/rerun_failed_tests', 'exprtests.json', __name__),
                                     TEST_DIRECTORY, None)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 2)

    def test_combined_rerun(self):
        tests = enqueue_failed_tests(get_path('tool_test/rerun_failed_tests', 'combined.json', __name__),
                                     TEST_DIRECTORY, None)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 3)

    def test_combined_rerun_local_tests(self):
        tests = enqueue_failed_tests(get_path('tool_test/rerun_failed_tests', 'combined_local.json', __name__),
                                     TEST_DIRECTORY, None)
        all_test_results = tdvt_core.run_tests_serial(tests)
        self.check_results(all_test_results, 5)

    def test_logical_rerun_fail(self):
        tests = enqueue_failed_tests(get_path('tool_test/rerun_failed_tests', 'logical_compare_sql.json', __name__),
                                     TEST_DIRECTORY, None)
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

class CommandLineTest(unittest.TestCase):
    def setUp(self):
        self.test_config = TdvtTestConfig()
        self.test_config.logical = False
        self.test_config.tds = 'mytds.tds'

        self.test_file = 'some/test/file.txt'
        self.test_set = ExpressionTestSet('', TEST_DIRECTORY, 'mytest', self.test_config.tds, '', self.test_file, '')

    def test_command_line_full(self):
        self.test_config.output_dir = 'my/output/dir'
        self.test_config.d_override = '-DLogLevel=Debug'

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
        suite = 'password_test'

        self.test_set = ExpressionTestSet('', TEST_DIRECTORY, 'mytest', self.test_config.tds, '', self.test_file, suite)
        work = tdvt_core.BatchQueueWork(self.test_config, self.test_set)
        cmd_line = build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        self.assertTrue('--password-file' in cmd_line_str and 'password_test.password' in cmd_line_str)

    def test_command_line_full_extension(self):

        self.test_config.output_dir = 'my/output/dir'
        self.test_config.d_override = '-DLogLevel=Debug'

        work = tdvt_core.BatchQueueWork(self.test_config, self.test_set)
        work.test_extension = True
        cmd_line = build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        if sys.platform in ('win32', 'cygwin'):
            expected = 'tabquerytool.exe --expression-file-list my/output/dir\mytest\\tests.txt -d mytds.tds --combined --output-dir my/output/dir -DLogDir=my/output/dir\mytest -DOverride=ProtocolServerNewLog -DLogLevel=Debug -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable --test_arg my/output/dir'  # noqa: E501
        elif sys.platform in ('darwin', 'linux'):
            expected = 'tabquerytool --expression-file-list my/output/dir/mytest/tests.txt -d mytds.tds --combined --output-dir my/output/dir -DLogDir=my/output/dir/mytest -DOverride=ProtocolServerNewLog -DLogLevel=Debug -DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall -DInMemoryLogicalCacheDisable --test_arg my/output/dir'  # noqa: E501
        else:
            self.skipTest("Unsupported test OS: {}".format(sys.platform))
        self.assertTrue(cmd_line_str == expected, 'Actual: ' + cmd_line_str + ': Expected: ' + expected)

    def test_command_line_no_expected(self):
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
        self.assert_number_of_tests(ExpressionTestSet('', ROOT_DIRECTORY, 'logical.tde', 'cast_calcs.tde.tds', 'mytest3',
                                                      'e/suite1/setup.*.txt', ''), 2)


class ConfigTest(unittest.TestCase):
    def test_load_ini(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'aurora.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet('aurora', TEST_DIRECTORY, 'logical.calcs.aurora', 'cast_calcs.aurora.tds', '',
                               'logicaltests/setup/calcs/setup.*.bool_.xml', test_config.dsname)

        test2 = LogicalTestSet('aurora', TEST_DIRECTORY, 'logical.staples.aurora', 'Staples.aurora.tds', 'Filter.Trademark',
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

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.aurora', 'Staples.aurora.tds', 'Filter.Trademark',
                               'logicaltests/setup/staples/setup.*.bool_.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.aurora', 'cast_calcs.aurora.tds',
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

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.aurora', 'cast_calcs.aurora.tds', '', 'logicaltests/setup/calcs/setup.*.bool_.xml', test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.aurora', 'Staples.aurora.tds', '', 'logicaltests/setup/staples/setup.*.bool_.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.aurora', 'cast_calcs.aurora.tds', '', 'exprtests/standard/setup.*.txt', test_config.dsname)

        tests = [test1, test2, test3]

        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_bigquery(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'bigquery.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.bigquery', 'cast_calcs.bigquery.tds', '',
                               'logicaltests/setup/calcs/setup.*.bigquery.xml', test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.bigquery', 'Staples.bigquery.tds', '',
                               'logicaltests/setup/staples/setup.*.bigquery.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.bigquery', 'cast_calcs.bigquery.tds',
                                  'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse',    # noqa: E501
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

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical_test1.bigquery_sql_test', 'Staples.bigquery.tds', '',
                               'logicaltests/setup.*.bigquery.xml', test_config.dsname)
        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical_test2.bigquery_sql_test', 'Staples.bigquery_sql_test.tds', '',
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
                            "[Did not find expected value of [{0}, found {1} instead.]".format(expected_password_file, actual_file))  # noqa: E50

    def test_load_ini_logical_config(self):
        config = configparser.ConfigParser()
        #Preserve the case of elements.
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

        #Duplicates should be removed and the order preserved.
        standard = ['teradata', 'netezza']
        all_passing = ['teradata', 'netezza', 'bigquery', 'exasolution']
        all_test = ['hadoophive2_hortonworks', 'teradata', 'netezza', 'bigquery', 'exasolution']
        all_test2 = ['hadoophive2_hortonworks', 'teradata', 'netezza', 'bigquery', 'exasolution']

        self.assertTrue(standard == reg.get_datasources('standard'))
        self.assertTrue(all_passing == reg.get_datasources('all_passing'))
        self.assertTrue(all_test == reg.get_datasources('all_test'))
        self.assertTrue(all_test2 == reg.get_datasources('all_test2'))


    def test_load_command_line_override(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'override.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.bigquery', 'cast_calcs.bigquery.tds', '', 'logicaltests/setup/calcs/setup.*.bigquery.xml', test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.bigquery', 'Staples.bigquery.tds', '', 'logicaltests/setup/staples/setup.*.bigquery.xml', test_config.dsname)

        test3 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.bigquery', 'cast_calcs.bigquery.tds', '', 'exprtests/standard/setup.*.txt', test_config.dsname)

        tests = [test1, test2, test3]

        self.assertTrue(test_config.d_override == 'WorkFaster=True Override=TurnOff:yes,TurnOn:no', 'Override did not match: ' + test_config.d_override)

        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_bigquery_sql(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'bigquery_sql.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.calcs.bigquery_sql', 'cast_calcs.bigquery_sql.tds', '', 'logicaltests/setup/calcs/setup.*.bigquery_sql.xml', test_config.dsname)

        test2 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.staples.bigquery_sql', 'Staples.bigquery_sql.tds', 'Filter.Trademark', 'logicaltests/setup/staples/setup.*.bigquery_sql.xml', test_config.dsname)

        test3 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical.lod.bigquery_sql', 'Staples.bigquery_sql.tds', '', 'logicaltests/setup/lod/setup.*.bigquery_sql.xml', test_config.dsname)

        test4 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.standard.bigquery_sql', 'cast_calcs.bigquery_sql.tds', 'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls,logical', 'exprtests/standard/setup.*.txt', test_config.dsname)

        test5 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression_test_dates.bigquery_sql', 'cast_calcs.bigquery_sql_dates.tds', 'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls', 'exprtests/standard/', test_config.dsname)

        test6 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression_test_dates2.bigquery_sql', 'cast_calcs.bigquery_sql_dates2.tds', 'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls', 'exprtests/standard/', test_config.dsname)

        test7 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.lod.bigquery_sql', 'cast_calcs.bigquery_sql.tds', '', 'exprtests/lodcalcs/setup.*.txt', test_config.dsname)

        test8 = LogicalTestSet(test_config.dsname, TEST_DIRECTORY, 'logical_test_dates.bigquery_sql', 'cast_calcs.bigquery_sql.tds', '', 'exprtests/standard/setup.*.bigquery_dates.xml', test_config.dsname)

        tests = [test1, test2, test3, test4, test5, test6, test7, test8]

        for test in tests:
            found = [y for y in x if y == test]
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_staplesdata_on(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'staples_data.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = ExpressionTestSet(test_config.dsname, TEST_DIRECTORY, 'expression.staples.bigquery', 'Staples.bigquery.tds', '', 'exprtests/staples/setup.*.txt', test_config.dsname)

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
        self.assertFalse(test_config.run_as_perf,'run_as_perf did not match: ' + str(test_config.run_as_perf))


    def test_load_run_as_perf_true(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'perf_true.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        self.assertTrue(test_config.run_as_perf, 'run_as_perf did not match: ' + str(test_config.run_as_perf))


    def test_load_run_as_perf_false(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'perf_false.ini', __name__))
        test_config = datasource_list.load_test(config, TEST_DIRECTORY)
        self.assertFalse(test_config.run_as_perf, 'run_as_perf did not match: ' + str(test_config.run_as_perf))


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
            MockTestRegistry.get_datasources.return_value=['postgres_jdbc', 'postgres_odbc']
            correct_out = "\nAvailable datasources:\npostgres_jdbc\npostgres_odbc\n\nAvailable suites:\nall\n\tpostgres_jdbc, postgres_odbc"
            captured_output = io.StringIO()
            sys.stdout = captured_output
            datasource_list.print_configurations(MockTestRegistry, None, None)
            self.assertIn(correct_out, captured_output.getvalue())


ROOT_DIRECTORY = pkg_resources.resource_filename(__name__, '')
TEST_DIRECTORY = pkg_resources.resource_filename(__name__, 'tool_test')
print ("Using root dir " + str(ROOT_DIRECTORY))
print ("Using test dir " + str(TEST_DIRECTORY))
logging.basicConfig(filename='tdvt_test_log.txt',level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
configure_tabquery_path()
if __name__ == '__main__':

    logging.debug("Starting TDVT tests\n")

    unittest.main()

    logging.debug("Ending TDVT tests\n")
