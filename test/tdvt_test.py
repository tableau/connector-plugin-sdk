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
import os
import unittest
import xml.etree.ElementTree
import pkg_resources
import logging
from tdvt import tdvt_core
from tdvt.config_gen import datasource_list
from tdvt.config_gen.test_config import TestSet
from tdvt.resources import get_path
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
            actual_xml = xml.etree.ElementTree.parse(actual_file).getroot()
            expected_xml = xml.etree.ElementTree.parse(expected_file).getroot()
            compare_sql = False
            compare_tuples = False
            if 'expected.sql' in test:
                compare_sql = True
            if 'expected.tuples' in test:
                compare_tuples = True
            if 'expected.both' in test:
                compare_tuples = True
                compare_sql = True
            test_config = tdvt_core.TdvtTestConfig(compare_sql, compare_tuples)
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
    def check_results(self, test_results, total_test_count, should_pass=True):
        test_status_expected = "passed" if should_pass else "failed"
        #Make sure we ran the right number of tests and that they all passed.
        self.assertTrue(len(test_results) == total_test_count, "Did not run the right number of tests.")
        for path, test_result in test_results.items():
            passed = test_result is not None
            passed = passed and test_result.all_passed()
            test_status = "passed" if passed else "failed"
            self.assertTrue(passed == should_pass, "Test [{0}] {1} but should have {2}.".format(path, test_status, test_status_expected))

class ExpressionTest(BaseTDVTTest):
    def setUp(self):
        self.config_file = 'tool_test/config/expression.tde.cfg'
        self.test_config = tdvt_core.TdvtTestConfig()
        self.test_config.tds = tdvt_core.get_tds_full_path(ROOT_DIRECTORY, 'tool_test/tds/cast_calcs.tde.tds')

    def test_expression_tests(self):
        all_test_results = {}
        all_test_results = tdvt_core.run_tests_parallel(tdvt_core.generate_test_file_list(ROOT_DIRECTORY, '', self.config_file, ''), self.test_config)
        self.check_results(all_test_results, 2)

class LogicalTest(BaseTDVTTest):
    def setUp(self):
        self.config_file = 'tool_test/config/logical.tde.cfg'
        self.test_config = tdvt_core.TdvtTestConfig()
        self.test_config.tds = tdvt_core.get_tds_full_path(ROOT_DIRECTORY, 'tool_test/tds/cast_calcs.tde.tds')
        self.test_config.logical = True

    def test_logical_tests(self):
        all_test_results = {}
        all_test_results = tdvt_core.run_tests_parallel(tdvt_core.generate_test_file_list(ROOT_DIRECTORY, '', self.config_file, ''), self.test_config)

        self.check_results(all_test_results, 1)

class ReRunFailedTestsTest(BaseTDVTTest):
    def setUp(self):
        self.test_dir = TEST_DIRECTORY
        self.config_file = 'tool_test/config/logical.tde.cfg'
        self.tds_file = tdvt_core.get_tds_full_path(ROOT_DIRECTORY, 'tool_test/tds/cast_calcs.tde.tds')
        self.test_config = tdvt_core.TdvtTestConfig()
        self.test_config.logical = True
        self.test_config.config_file = self.config_file
        self.test_config.tds = self.tds_file

    def test_failed_test_output(self):
        """Make sure TDVT writes the correct output file for rerunning failed tests."""
        all_test_results = {}
        #This will cause the test to fail as expected.
        self.test_config.tested_sql = True
        all_test_results = tdvt_core.run_tests_parallel(tdvt_core.generate_test_file_list(ROOT_DIRECTORY, '', self.config_file, ''), self.test_config)
        tdvt_core.write_standard_test_output(all_test_results, self.test_dir)

        self.check_results(all_test_results, 1, False)

        #Now rerun the failed tests which should fail again, indicating that the 'tested_sql' option was persisted correctly.
        all_test_results = tdvt_core.run_failed_tests_impl(get_path('tool_test', 'tdvt_output.json', __name__), TEST_DIRECTORY, 1)

        self.check_results(all_test_results, 1, False)

    def test_logical_rerun(self):
        all_test_results = tdvt_core.run_failed_tests_impl(get_path('tool_test/rerun_failed_tests', 'logical.json', __name__), TEST_DIRECTORY, 1)
        self.check_results(all_test_results, 1)

    def test_expression_rerun(self):
        all_test_results = tdvt_core.run_failed_tests_impl(get_path('tool_test/rerun_failed_tests','exprtests.json', __name__), TEST_DIRECTORY, 1)
        self.check_results(all_test_results, 2)

    def test_combined_rerun(self):
        all_test_results = tdvt_core.run_failed_tests_impl(get_path('tool_test/rerun_failed_tests', 'combined.json', __name__), TEST_DIRECTORY, 1)
        self.check_results(all_test_results, 3)

    def test_logical_rerun_fail(self):
        all_test_results = tdvt_core.run_failed_tests_impl(get_path('tool_test/rerun_failed_tests', 'logical_compare_sql.json', __name__), TEST_DIRECTORY, 1)
        self.check_results(all_test_results, 1, False)

class PathTest(unittest.TestCase):
    def test_config_file_path(self):
        cfg_path = tdvt_core.get_config_file_full_path(ROOT_DIRECTORY, 'tool_test/config/logical.tde.cfg')
        self.assertTrue(os.path.isfile(cfg_path))

    def test_config_file_default_path(self):
        cfg_path = tdvt_core.get_config_file_full_path(os.path.join(ROOT_DIRECTORY, 'tool_test'), 'logical.tde.cfg')
        self.assertTrue(os.path.isfile(cfg_path))

        #        self.tds_file = tdvt_core.get_tds_full_path(ROOT_DIRECTORY, 'tool_test/tds/cast_calcs.tde.tds')

class CommandLineTest(unittest.TestCase):
    def test_command_line_full(self):
        test_config = tdvt_core.TdvtTestConfig()
        test_config.logical = False
        test_config.tds = 'mytds.tds'
        #Optional.
        test_config.output_dir = 'my/output/dir'
        test_config.d_override = 'LogLevel=Debug'

        test_file = 'some/test/file.txt'
        work = tdvt_core.QueueWork(test_config, test_file)
        cmd_line = tdvt_core.build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        expected = 'tabquerycli.exe -e some/test/file.txt -d mytds.tds --combined --output-dir my/output/dir -DLogLevel=Debug'
        self.assertTrue(cmd_line_str == expected, 'Actual: ' + cmd_line_str + ': Expected: ' + expected)

    def test_command_line_no_expected(self):
        test_config = tdvt_core.TdvtTestConfig()
        test_config.logical = False
        test_config.tds = 'mytds.tds'

        test_file = 'some/test/file.txt'
        work = tdvt_core.QueueWork(test_config, test_file)
        cmd_line = tdvt_core.build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        expected = 'tabquerycli.exe -e some/test/file.txt -d mytds.tds --combined'
        self.assertTrue(cmd_line_str == expected, 'Actual: ' + cmd_line_str + ': Expected: ' + expected)

    def test_command_line_multiple_override(self):
        test_config = tdvt_core.TdvtTestConfig()
        test_config.logical = False
        test_config.tds = 'mytds.tds'
        test_config.d_override = 'LogLevel=Debug UseJDBC Override=MongoDBConnector:on,SomethingElse:off'

        test_file = 'some/test/file.txt'
        work = tdvt_core.QueueWork(test_config, test_file)
        cmd_line = tdvt_core.build_tabquery_command_line_local(work)
        cmd_line_str = ' '.join(cmd_line)
        expected = 'tabquerycli.exe -e some/test/file.txt -d mytds.tds --combined -DLogLevel=Debug -DUseJDBC -DOverride=MongoDBConnector:on,SomethingElse:off'
        self.assertTrue(cmd_line_str == expected, 'Actual: ' + cmd_line_str + ': Expected: ' + expected)

class ConfigTest(unittest.TestCase):
    def test_load_ini(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'aurora.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = TestSet('logical.calcs.aurora.cfg', 'cast_calcs.aurora.tds', '', 'logicaltests/setup/calcs/setup.*.bool_.xml')

        test2 = TestSet('logical.staples.aurora.cfg', 'Staples.aurora.tds', 'Filter.Trademark', 'logicaltests/setup/staples/setup.*.bool_.xml')

        test3 = TestSet('logical.lod.aurora.cfg', 'Staples.aurora.tds', '', 'logicaltests/setup/lod/setup.*.bool_.xml')

        test4 = TestSet('expression.standard.aurora.cfg', 'cast_calcs.aurora.tds', 'string.char,dateparse', 'exprtests/standard/')

        test5 = TestSet('expression.lod.aurora.cfg', 'cast_calcs.aurora.tds', '', 'exprtests/lodcalcs/setup.*.txt')

        tests = [test1, test2, test3, test4, test5]
        
        for test in tests:
            found = [y for y in x if y == test] 
            msg = "[Did not find expected value of [{0}]".format(test)
            self.assertTrue(found, msg)


    def test_load_ini_missing(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'aurora_missing.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = TestSet('logical.calcs.aurora.cfg', 'cast_calcs.aurora.tds', '', 'logicaltests/setup/calcs/setup.*.bool_.xml')

        test2 = TestSet('logical.staples.aurora.cfg', 'Staples.aurora.tds', 'Filter.Trademark', 'logicaltests/setup/staples/setup.*.bool_.xml')

        test3 = TestSet('expression.standard.aurora.cfg', 'cast_calcs.aurora.tds', 'string.char,dateparse', 'exprtests/standard/')

        tests = [test1, test2, test3]
        
        for test in tests:
            found = [y for y in x if y == test] 
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))
        
    def test_load_ini_missing2(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'aurora_missing2.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = TestSet('logical.calcs.aurora.cfg', 'cast_calcs.aurora.tds', '', 'logicaltests/setup/calcs/setup.*.bool_.xml')

        test2 = TestSet('logical.staples.aurora.cfg', 'Staples.aurora.tds', '', 'logicaltests/setup/staples/setup.*.bool_.xml')

        test3 = TestSet('expression.standard.aurora.cfg', 'cast_calcs.aurora.tds', '', 'exprtests/standard/')

        tests = [test1, test2, test3]
        
        for test in tests:
            found = [y for y in x if y == test] 
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_bigquery(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'bigquery.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = TestSet('logical.calcs.bigquery.cfg', 'cast_calcs.bigquery.tds', '', 'logicaltests/setup/calcs/setup.*.bigquery.xml')

        test2 = TestSet('logical.staples.bigquery.cfg', 'Staples.bigquery.tds', '', 'logicaltests/setup/staples/setup.*.bigquery.xml')

        test3 = TestSet('expression.standard.bigquery.cfg', 'cast_calcs.bigquery.tds', 'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse', 'exprtests/standard/')

        tests = [test1, test2, test3]
        
        for test in tests:
            found = [y for y in x if y == test] 
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_new_tests(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'new_tests.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        for a in x:
            print(a)

        test1 = TestSet('logical_test1.bigquery_sql_test.cfg', 'Staples.bigquery.tds', '', 'logicaltests/setup.*.bigquery.xml')
        test2 = TestSet('logical_test2.bigquery_sql_test.cfg', 'Staples.bigquery_sql_test.tds', '', 'logicaltests/setup.*.bigquery.xml')

        test3 = TestSet('expression_test1.bigquery_sql_test.cfg', 'cast_calcs.bigquery_sql_dates2.tds', 'string.ascii', 'exprtests/standard/')
        test4 = TestSet('expression_test2.bigquery_sql_test.cfg', 'cast_calcs.bigquery_sql_test.tds', 'string.char', 'exprtests/standard/')

        tests = [test1, test2, test3, test4]
        
        for test in tests:
            found = [y for y in x if y == test] 
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_logical_config(self):
        config = configparser.ConfigParser()
        #Preserve the case of elements.
        config.optionxform = str
        config.read(get_path('tool_test/ini', 'logical_config.ini', __name__))
        test_config = datasource_list.LoadTest(config)

        cfg = test_config.logical_config['my_logical_query']
        self.assertTrue(test_config.logical_config_name == 'my_logical_query')
        self.assertTrue(cfg['tablename'] == 'CRAZYTABLE_$dsName')
        self.assertTrue(cfg['tablePrefix'] == '[LOCO].')
        self.assertTrue(cfg['tablenameUpper'] == 'True')


    def test_load_windows_override(self):
        ini_file = get_path('tool_test/ini', 'windows_override.ini', __name__)
        reg = datasource_list.TestRegistry('')
        reg.load_registry(ini_file)
       
        standard = ['teradata', 'netezza']
        all_passing = ['teradata', 'netezza', 'bigquery', 'exasolution']
        all_test = ['hadoophive2_hortonworks', 'teradata', 'netezza', 'teradata', 'netezza', 'bigquery', 'exasolution']
        all_test2 = ['hadoophive2_hortonworks', 'teradata', 'netezza', 'teradata', 'netezza', 'bigquery', 'exasolution', 'teradata', 'netezza', 'bigquery', 'exasolution']

        self.assertTrue(standard == reg.get_datasources('standard'))
        self.assertTrue(all_passing == reg.get_datasources('all_passing'))
        self.assertTrue(all_test == reg.get_datasources('all_test'))
        self.assertTrue(all_test2 == reg.get_datasources('all_test2'))
 

    def test_load_command_line_override(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'override.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = TestSet('logical.calcs.bigquery.cfg', 'cast_calcs.bigquery.tds', '', 'logicaltests/setup/calcs/setup.*.bigquery.xml')

        test2 = TestSet('logical.staples.bigquery.cfg', 'Staples.bigquery.tds', '', 'logicaltests/setup/staples/setup.*.bigquery.xml')

        test3 = TestSet('expression.standard.bigquery.cfg', 'cast_calcs.bigquery.tds', '', 'exprtests/standard/')

        tests = [test1, test2, test3]
        
        self.assertTrue(test_config.d_override == 'WorkFaster=True Override=TurnOff:yes,TurnOn:no', 'Override did not match: ' + test_config.d_override)

        for test in tests:
            found = [y for y in x if y == test] 
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_bigquery_sql(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'bigquery_sql.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = TestSet('logical.calcs.bigquery_sql.cfg', 'cast_calcs.bigquery_sql.tds', '', 'logicaltests/setup/calcs/setup.*.bigquery_sql.xml')

        test2 = TestSet('logical.staples.bigquery_sql.cfg', 'Staples.bigquery_sql.tds', 'Filter.Trademark', 'logicaltests/setup/staples/setup.*.bigquery_sql.xml')

        test3 = TestSet('logical.lod.bigquery_sql.cfg', 'Staples.bigquery_sql.tds', '', 'logicaltests/setup/lod/setup.*.bigquery_sql.xml')

        test4 = TestSet('expression.standard.bigquery_sql.cfg', 'cast_calcs.bigquery_sql.tds', 'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls,logical', 'exprtests/standard/')

        test5 = TestSet('expression_test_dates.bigquery_sql.cfg', 'cast_calcs.bigquery_sql_dates.tds', 'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls', 'exprtests/standard/')

        test6 = TestSet('expression_test_dates2.bigquery_sql.cfg', 'cast_calcs.bigquery_sql_dates2.tds', 'string.ascii,string.char,string.bind_trim,string.left.real,string.right.real,dateparse,math.degree,math.radians,cast.str,cast.int.nulls', 'exprtests/standard/')

        test7 = TestSet('expression.lod.bigquery_sql.cfg', 'cast_calcs.bigquery_sql.tds', '', 'exprtests/lodcalcs/setup.*.txt')

        test8 = TestSet('logical_test_dates.bigquery_sql.cfg', 'cast_calcs.bigquery_sql.tds', '', 'exprtests/standard/setup.*.bigquery_dates.xml')

        tests = [test1, test2, test3, test4, test5, test6, test7, test8]

        for test in tests:
            found = [y for y in x if y == test] 
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_staplesdata_on(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'staples_data.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        test1 = TestSet('expression.staples.bigquery.cfg', 'Staples.bigquery.tds', '', 'exprtests/staples/setup.*.txt')

        tests = [test1]
        
        for test in tests:
            found = [y for y in x if y == test] 
            self.assertTrue(found, "[Did not find expected value of [{0}]".format(test))

    def test_load_ini_staplesdata_off(self):
        config = configparser.ConfigParser()
        config.read(get_path('tool_test/ini', 'staples_data_off.ini', __name__))
        test_config = datasource_list.LoadTest(config)
        x = test_config.get_logical_tests() + test_config.get_expression_tests()

        self.assertTrue(not x)

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
