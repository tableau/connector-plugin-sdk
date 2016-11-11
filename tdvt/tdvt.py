"""
    Tableau Datasource Verification Tool
    Run logical queiries and expression tests against datasources.

"""

import os
import sys
import re
import argparse
import subprocess
import shutil
import threading
import time
import xml.etree.ElementTree
import glob
import json
import csv
import configparser
from .config_gen.genconfig import generate_config_files
from .config_gen.gentests import generate_logical_files
from .resources import *

EXPR_CONFIG_ARG = '--expression-config'
EXPR_CONFIG_ARG_SHORT = '-e'
LOGICAL_CONFIG_ARG = '--logical-query-config'
LOGICAL_CONFIG_ARG_SHORT = '-q'
TDS_CONFIG_ARG = '--tds'
TDS_CONFIG_ARG_SHORT = '-d'
ALWAYS_GENERATE_EXPECTED = False
VERBOSE = False
MAX_SUBPROCESSES = 12
ABORT_TEST_RUN = False

class TestCaseResult(object):
    """The actual or expected results of a test run.

        ie The math.round test contains ROUND(int), ROUND(num) etc test cases.

    """
    def __init__(self, name, id, sql, query_time, error_msg, error_type, table, tested_config):
        self.name = name
        self.id = id
        self.sql = sql
        self.table = table
        self.execution_time = query_time
        self.error_message = error_msg
        self.error_type = error_type
        self.diff_count = 0
        self.diff_string = ''
        self.tested_config = tested_config
        self.passed_sql = False
        self.passed_tuples = False

    def set_diff(self, diff_string, diff_count):
        self.diff_string = diff_string
        self.diff_count = diff_count

    def get_sql_text(self):
        return self.sql.text

    def get_tuples(self):
        tuple_list = []
        tuples = self.table.findall('tuple')
        for t in tuples:
            for v in t.findall('value'):
                tuple_list.append(v.text)

        return tuple_list

    def all_passed(self):
        """Return true if all aspects of the test passed."""
        passed = True
        if self.tested_config.tested_sql and not self.passed_sql:
            passed = False
        if self.tested_config.tested_tuples and not self.passed_tuples:
            passed = False

        return passed

    def table_to_json(self):
        json_str = 'tuple' 
        tuple_list = []
        tuples = self.table.findall('tuple')
        for t in tuples:
            for v in t.findall('value'):
                tuple_list.append(v.text)

        return {'tuples' : tuple_list}
    
    def __json__(self):
        return {'tested_sql' : self.tested_sql, 'tested_tuples' : self.tested_tuples, 'id' : self.id, 'name' : self.name, 'sql' : self.get_sql_text(), 'table' : self.table_to_json()}

class TdvtTestConfig(object):
    """Track how items were tested. This captures how tdvt was invoked."""
    def __init__(self, tested_sql = False, tested_tuples = False, tds = '', expected_dir = '', config = '', output_dir = '', logical = False, verbose = False, override = '', suite_name = '', from_args = None, thread_count = 4):
        self.tested_sql = tested_sql
        self.tested_tuples = tested_tuples
        self.expected_dir = expected_dir
        self.output_dir = output_dir
        self.logical = logical
        self.config_file = config
        self.suite_name = suite_name
        self.invocation_name = ''
        self.invocation_extra_args = ''
        self.d_override = override
        self.verbose = verbose
        self.tds = tds
        self.noheader = False
        self.thread_count = thread_count
        if from_args:
            self.init_from_args(from_args)

    def init_from_args(self, args):
        self.tested_sql = True if args.compare_sql else False
        self.tested_tuples = False if args.nocompare_tuples else True
        self.expected_dir = args.expected_dir if args.expected_dir else ''
        self.logical = True if args.logical_query_config else False
        self.suite_name = args.suite if args.suite else ''
        self.output_dir = args.output_dir if args.output_dir else ''
        self.d_override = args.d_override if args.d_override else ''
        self.invocation_name = ''
        self.invocation_extra_args = ''
        self.noheader = True if args.noheader else False
        self.thread_count = args.thread_count if args.thread_count else 4
        if args.expression_config:
            self.config_file = args.expression_config
        elif args.logical_query_config:
            self.config_file = args.logical_query_config

    def __str__(self):
        return "[{}]: suite [{}]: tested sql [{}]: tested tuples [{}]: expected dir [{}]: output dir [{}]: logical [{}]: invocation args [{}]: config file [{}]: override [{}]: tds [{}]: thread [{}]".format(self.invocation_name, self.suite_name, self.tested_sql, self.tested_tuples, self.expected_dir, self.output_dir, self.logical, self.invocation_extra_args, self.config_file, self.d_override, self.tds, self.thread_count)

    def set_invocation(self, args):
        """Strip out the known arguments and just save the 'extra' ones. This is used for logging/rerunning failed tests from the logs.
            The 'main' arguments like -tds and -e or -q are removed since they are captured elsewhere. The secondary arguments like --compare-sql
            are captured here and logged in the json file. This way tdvt -f will rerun those failed tests exactly as they were run orginally.
        """
        possible_config_args = EXPR_CONFIG_ARG, EXPR_CONFIG_ARG_SHORT, LOGICAL_CONFIG_ARG, LOGICAL_CONFIG_ARG_SHORT
        possible_tds_args = TDS_CONFIG_ARG, TDS_CONFIG_ARG_SHORT
        prog_name = args[0]
        config_index = 0
        #Go through all the valid config args and see if one is set.
        for config_arg in possible_config_args:
            try:
                config_index = args.index(config_arg)
            except:
                pass

        if config_index > 0:
            #Skip this and the next one (ie the value) since they will be replaced later by an individual file invocation.
            del args[config_index]
            del args[config_index]
        
        tds_index = 0
        for tds_arg in possible_tds_args:
            try:
                tds_index = args.index(tds_arg)
            except:
                pass

        if tds_index > 0:
            #Skip this and the next one since they will be replaced later by an individual file invocation.
            del args[tds_index]
            del args[tds_index]

        extra_args = ''
        for arg in args[1:]:
            extra_args += ' ' + arg

        self.invocation_name = prog_name
        self.invocation_extra_args = extra_args 
    
class TestOutput(object):
    """A collection of individual test case runs.
        
        ie All of the math.round results. See TestCaseResult above.

    """
    def __init__(self, test_xml, tested_config):
        """
            <results>
            <test name='blah'
            <sql>text</sql>
            <query-time> 2.96439e-323 </query-time>
            <error> Any query errors </error> --Optional
            <error-type> Interpreted Tableau error type </error-type> --Optional
            <table>
            <schema></schema>
            <tuple>
            <value></value>
            <value></value>
            </tuple>
            </table>
            </results>

        """
        self.test_case_map = []
        #Go through all the test nodes under 'results'.
        for i in range(0, len(list(test_xml))):
            test_child = test_xml[i]

            node= test_child.find('error')
            error_msg = node.text if node is not None else ''

            node = test_child.find('error-type')
            error_type = node.text.strip() if node is not None else ''

            node = test_child.find('query-time')
            query_time = node.text if node is not None else '0'

            test_result = TestCaseResult(test_child.get('name'), str(i), test_child.find('sql'), query_time, error_msg, error_type, test_child.find('table'), tested_config)
            self.test_case_map.append(test_result)

    def all_passed(self):
        """Return true if all aspects of the test passed."""
        passed = True
        for test_case in self.test_case_map:
            if test_case.all_passed() == False:
                return False
        return True

    def set_diff_counts(self, diff_counts):
        if len(diff_counts) != len(self.test_case_map):
            return
        for i in range(0, len(self.test_case_map)):
            self.test_case_map[i].diff_count = diff_counts[i]
    
    def get_error_messages(self):
        err_msgs = [ tc.error_message for tc in self.test_case_map if tc.error_message ]
        return err_msgs

    def get_exceptions(self):
        exceptions = [ tc.error_type for tc in self.test_case_map if tc.error_type ]
        return exceptions

    def __json__(self):
        return {'test_cases' : self.test_case_map}

class TestExecution(object):
    """Test execution information."""
    def __init__(self, repro_cmdline = '', tds = '', test_file = '', test_type = '', suite = '', other_args = ''):
        #A command line you could run to repro this test.
        self.cmdline = repro_cmdline
        self.tds = tds
        self.test_file = test_file
        self.test_type = test_type
        self.suite_name = suite
        self.other_args = other_args

class TestResult(object):
    """Information about a test suite run."""
    def __init__(self, base_name = '', test_env = TestExecution()):
        self.name = base_name
        self.test_execution = test_env
        self.matched_expected_version = 0
        self.test_failed_to_run = False
        self.test_timed_out = False
        self.actual_results = None
        self.diff_count = 0
        self.best_matching_expected_results = None
        self.path_to_expected = ''
        self.path_to_actual = ''

    def __json__(self):
        return {'all_passed' : self.all_passed(), 'name' : self.name, 
                'matched_expected' : self.matched_expected_version, 'expected_diffs' : self.diff_count,
                'actual_results' : self.actual_results, 'expected_results' : self.best_matching_expected_results}

    def add_actual_output(self, result_output, actual_path):
        self.actual_results = result_output
        self.path_to_actual = actual_path

    def get_failure_message(self):
        if self.test_failed_to_run:
            return "Test did not run."
        elif self.test_timed_out:
            return "Test timed out."

        if self.actual_results:
            msgs = self.actual_results.get_error_messages()
            if not msgs:
                return "Expected does not match any actual file."
            return ".".join(msgs)
        else:
            return "No results found."
        return "Unknown failure."

    def get_exceptions(self):
        if self.test_failed_to_run or not self.actual_results:
            return []
        return self.actual_results.get_exceptions()

    def set_best_matching_expected_output(self, expected_output, expected_path, expected_number, diff_counts):
        diff_count = sum(diff_counts)
        if self.best_matching_expected_results is None or self.diff_count > diff_count:
            self.best_matching_expected_results = expected_output
            self.matched_expected_version = expected_number
            self.actual_results.set_diff_counts(diff_counts)
            self.diff_count = diff_count
            self.path_to_expected = expected_path

    def get_name(self):
        """Chop off the end of the test file (extension) when getting the name."""
        regex = re.compile('setup\.(.*)\.[a-zA-Z]{3}')
        match = re.match(regex, self.name)
        if not match:
            return self.name
        return match.group(1)

    def all_passed(self):
        """Return true if all aspects of the test passed."""
        if self.test_failed_to_run:
            return False
        if not self.actual_results:
            return False
        return self.actual_results.all_passed()

class TestResultEncoder(json.JSONEncoder):
    """For writing JSON output."""
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)

class TestOutputJSONEncoder(json.JSONEncoder):
    """Simple wrapper to output expected JSON format."""
    def default(self, obj):
        if type(obj) is not TestResult:
            return "failed" + str(obj) 

        suite_name = '' if not obj.test_execution.suite_name else obj.test_execution.suite_name
        case_name = '' if not obj.get_name() else obj.get_name()
        json_output = {'suite' : suite_name, 
                'class' : 'TDVT',
                #This includes suite to differentiate the results for Narc.py.
                'case' : suite_name + '.' + case_name, 
                'test_file' : obj.test_execution.test_file, 
                'test_type' : obj.test_execution.test_type, 
                'tds' : obj.test_execution.tds, 
                'other_args' : obj.test_execution.other_args, 
                'repro' : obj.test_execution.cmdline,
                'expected' : obj.path_to_expected,
               }
        if obj.all_passed():
            return json_output

        failtype = ','.join(obj.get_exceptions())
        json_output['failtype'] = failtype if failtype else 'test_failure'
        json_output['message'] = obj.get_failure_message()
        json_output['actual'] = obj.path_to_actual
        return json_output

class test_thread(threading.Thread):
    def __init__(self, thread_num, tds_file, test_file, test_config, thread_lock, all_test_results):
        threading.Thread.__init__(self)
        self.tds_file = tds_file
        self.test_file = test_file
        self.test_config = test_config
        self.thread_lock = thread_lock
        self.all_test_results = all_test_results
        self.logical = test_config.logical
        self.name = "thread " + str(thread_num)
        self.daemon = True
        self.timeout_seconds = 1200

        self.start()

    def run(self):
        global ABORT_TEST_RUN
        self.thread_lock.acquire()

        LOG.log("\nRunning test:" + self.test_file)
        if not os.path.isfile(self.test_file):
            LOG.log("Error opening file:" + self.test_file)
            self.thread_lock.release()
            return

        cli_arg = "-q" if self.logical else "-e"

        cmdline = [TAB_CLI_EXE]
        cmdline_base = [cli_arg, self.test_file]
        cmdline.extend(cmdline_base)
        tds_arg = ["-d", self.tds_file]
        cmdline.extend(tds_arg)
        cmdline.extend(["--combined"])

        expected_output_dir = self.test_config.output_dir

        if self.logical:
            existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(self.test_file, self.test_config.output_dir)
            expected_output_dir = expected_output_dir if expected_output_dir else expected_dir

        if expected_output_dir:
            if not os.path.isdir(expected_output_dir):
                LOG.log("Making dir: {}".format(expected_output_dir))
                os.makedirs(expected_output_dir)
            cmdline.extend(["--output-dir", expected_output_dir])

        if self.test_config.d_override:
            cmdline.extend(["-D" + self.test_config.d_override])

        repro_cmdline = self.test_config.invocation_name + ' ' + ' '.join(cmdline_base) + ' '.join(tds_arg) + ' ' + self.test_config.invocation_extra_args
        test_execution = TestExecution(repro_cmdline, self.tds_file, self.test_file, cli_arg, self.test_config.suite_name, self.test_config.invocation_extra_args)

        if ABORT_TEST_RUN:
            #Do this here so we have to repro information from above.
            LOG.log("\nAborting test:" + self.test_file)
            result = TestResult(get_base_test(self.test_file), test_execution)
            result.test_failed_to_run = True
            self.all_test_results[self.test_file] = result
            self.thread_lock.release()
            return

        LOG.log(self.name + " calling " + ' '.join(cmdline))

        self.thread_lock.release()
        cmd_output = None
        try:
            cmd_output = subprocess.check_output(cmdline, stderr=subprocess.STDOUT, universal_newlines=True, timeout=self.timeout_seconds)
        except subprocess.CalledProcessError as e:
            cmd_output = e.output
        except subprocess.TimeoutExpired as e:
            self.thread_lock.acquire()
            LOG.log("Test timed out: " + self.test_file)
            result = TestResult(get_base_test(self.test_file), test_execution)
            result.test_timed_out = True
            self.all_test_results[self.test_file] = result
            if not VERBOSE:
                sys.stdout.write('F')
            self.thread_lock.release()
            exit()

            
        self.thread_lock.acquire()
        if cmd_output:
            LOG.log(str(cmd_output))

        if self.logical:
            existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(self.test_file, self.test_config.output_dir)
            if not os.path.isfile( existing_output_filepath ):
                LOG.log("Error: could not find test output file:" + existing_output_filepath)
                result = TestResult(base_test_name, test_execution)
                self.all_test_results[self.test_file] = result
                if not VERBOSE:
                    sys.stdout.write('F')
                self.thread_lock.release()
                exit()
            #Copy the test process filename to the actual. filename.
            LOG.log("Copying {0} to {1}".format(existing_output_filepath, actual_output_filepath))
            try_move(existing_output_filepath, actual_output_filepath)

            self.test_file = base_filepath

        result = compare_results(self.test_file, self.test_config)
        result.test_execution = test_execution

        if result == None:
            result = TestResult()
            result.test_failed_to_run = True

        if not VERBOSE:
            sys.stdout.write('.' if result.all_passed() else 'F')
            sys.stdout.flush()

        self.all_test_results[self.test_file] = result
        #If this failed with a password, connection error or similar then abort this entire test run (which uses the same tds file). This will prevent running hundreds of tests that have to wait for a timeout before failing.
        for ex in result.get_exceptions():
            if ex in ['BadPassword', 'Disconnect', 'NoDriver', 'UnableToConnect', 'Unlicensed', 'ExpiredPassword', 'NoPassword']:
                ABORT_TEST_RUN = True

        self.thread_lock.release()

    def __del__(self):
        # Make sure we're not still holding onto the lock for some reason
        try: self.thread_lock.release()
        except Exception: pass

class Logger(object):
    def __init__(self, root_dir, verbose, output_dir=None ):
        self.log_dir = output_dir if output_dir else root_dir
        self.log_file = open(os.path.join(self.log_dir, 'tdvt_log.txt'), 'w', encoding='utf8')
        self.verbose = verbose

    def log(self, msg):
        if self.verbose: print (msg)
        self.log_file.write(str(time.asctime()) + ":" + msg + "\n")

    def __delf__(self):
        self.log_file.close()

def try_move(srcfile, destfile):
    moved = False
    move_attempt = 0
    while not moved and move_attempt < 3:
        try:
            move_attempt += 1
            shutil.move(srcfile, destfile)
            return
        except:
            time.sleep(0.05)

def get_base_test(test_file):
    return os.path.split(test_file)[1]

def diff_sql_node(actual_sql, expected_sql, diff_string):
    if actual_sql == None and expected_sql == None:
        return (0, diff_string)
    
    diff_string += "SQL\n"
    if actual_sql == None or expected_sql == None or (actual_sql.text != expected_sql.text):
        diff_string += "<<<<\n" + actual_sql.text + "\n"
        diff_string += ">>>>\n" + expected_sql.text + "\n"
        return (1, diff_string)

    return (0, diff_string)

def diff_table_node(actual_table, expected_table, diff_string):
    actual_tuples = actual_table.findall('tuple')
    expected_tuples = expected_table.findall('tuple')

    if actual_tuples == None and expected_tuples == None:
        return (0, diff_string)
    if actual_tuples == None or expected_tuples == None:
        diff_string += "Tuples do not exist for one side.\n"
        return math.abs(len(actual_tuples) - len(expected_tuples))

    #Compare all the values for the tuples.
    if len(actual_tuples) != len(expected_tuples):
        diff_string += "Different number of tuples.\n"

    if not len(actual_tuples):
        diff_string += "No 'actual' file tuples.\n"
    
    diff_count = 0
    diff_string += "Tuples\n"

    expected_tuple_list = []
    for j in expected_tuples:
        for k in j.findall('value'):
            expected_tuple_list.append(k.text)

    actual_tuple_list = []
    for j in actual_tuples:
        for k in j.findall('value'):
            actual_tuple_list.append(k.text)

    diff_count = sum(a != b for a, b in zip(actual_tuple_list, expected_tuple_list))
    diff_count += abs(len(actual_tuple_list) - len(expected_tuple_list))

    for a, b in zip(actual_tuple_list, expected_tuple_list):
        if a != b:
            diff_string += " <<<< >>>> \n"
            diff_string += a + "\n"
            diff_string += b + "\n"

    return (diff_count , diff_string)


def diff_test_results(result, expected_output):
    """Compare the actual results to the expected test output based on the given rules."""

    test_case_count = len(result.actual_results.test_case_map)
    diff_counts = [0] * test_case_count
    diff_string = ''
    #Go through all test cases.
    for test_case in range(0, test_case_count):
        expected_testcase_result = expected_output.test_case_map[test_case]
        actual_testcase_result = result.actual_results.test_case_map[test_case]
        if expected_testcase_result is None:
            actual_testcase_result.passed_sql = False
            actual_testcase_result.passed_tuples = False
            continue

        config = actual_testcase_result.tested_config
        #Compare the SQL.
        if config.tested_sql:
            diff, diff_string = diff_sql_node(actual_testcase_result.sql, expected_testcase_result.sql, diff_string)
            actual_testcase_result.passed_sql = diff == 0
            diff_counts[test_case] = diff

        #Compare the tuples.
        if config.tested_tuples:
            diff, diff_string = diff_table_node(actual_testcase_result.table, expected_testcase_result.table, diff_string)
            actual_testcase_result.passed_tuples = diff == 0
            diff_counts[test_case] = diff

    result.diff_string = diff_string
    return diff_counts, diff_string

def save_results_diff(actual_file, diff_file, expected_file, diff_string):
    #Save a diff against the best matching file.
    LOG.log("Saving diff of actual and expected as [{}]".format(diff_file))
    try:
        f = open(diff_file, 'w')
        f.write("Diff of [{}] and [{}].\n".format(actual_file, expected_file))
        f.write(diff_string)
        f.close()
    except:
        pass

def compare_results(test_file, test_config):
    """Return a TestResult object that specifies what was tested and whether it passed.
       test_file is the full path to the test file (base test name).

    """
    #eg 'setup.math.txt'
    base_test_file = get_base_test(test_file)
    test_file_root = os.path.split(test_file)[0]
    actual_file, actual_diff_file, setup, expected_files = get_test_file_paths(test_file_root, base_test_file, test_config.expected_dir, test_config.output_dir)
    result = TestResult(base_test_file)

    #There should be an actual file at this point. eg actual.setup.math.txt.
    if not os.path.isfile(actual_file):
        LOG.log("Did not find actual file: " + actual_file)
        return result

    
    try:
        actual_xml = xml.etree.ElementTree.parse(actual_file).getroot()
        actual_output = TestOutput(actual_xml, test_config)
        result.add_actual_output(actual_output, actual_file)
    except xml.etree.ElementTree.ParseError as e:
        LOG.log("Exception parsing actual file: " + actual_file + " exception: " + str(e))
        return result

    expected_file_version = 0
    for expected_file in expected_files:
        if not os.path.isfile(expected_file):
            LOG.log("Copying actual [{}] to expected [{}]".format(actual_file, expected_file))
            #There is an actual but no expected, copy the actual to expected and return since there is nothing to compare against.
            try_move(actual_file, expected_file)
            return result
        #Try other possible expected files. These are numbered like 'expected.setup.math.1.txt', 'expected.setup.math.2.txt' etc.
        LOG.log(threading.current_thread().name + " Comparing " + actual_file + " to " + expected_file)
        expected_output = TestOutput(xml.etree.ElementTree.parse(expected_file).getroot(), test_config)
        
        diff_counts, diff_string = diff_test_results(result, expected_output)
        result.set_best_matching_expected_output(expected_output, expected_file, expected_file_version, diff_counts)

        if result.all_passed():
            LOG.log(threading.current_thread().name + " Results match expected number: " + str(expected_file_version))
            result.matched_expected_version = expected_file_version
            try:
                os.remove(actual_file)
                os.remove(actual_diff_file)
            except:
                pass # Mysterious problem deleting the file. Don't worry about it. It won't impact final results.
            return result

        #Try another possible expected file.
        expected_file_version = expected_file_version + 1

    #Exhausted all expected files. The test failed.
    #This will re-diff the results against the best expected file to ensure the test pass indicator and diff count is correct.
    diff_count, diff_string = diff_test_results(result, result.best_matching_expected_results)
    save_results_diff(actual_file, actual_diff_file, result.path_to_expected, diff_string) 

    return result

def write_json_results(all_test_results):
    """Write all the test result information to a json file."""
    all_results = []
    for name, res in all_test_results.items():
        all_results.append(res)
    json_str = json.dumps(all_results, cls=TestResultEncoder)
    json_file = open('test_results.json', 'w', encoding='utf8')
    json_file.write(json_str)
    json_file.close()

def write_standard_test_output(all_test_results, output_dir):
    """Write the standard (tube, teamcity, etc) output. """
    passed = [ x for x in all_test_results.values() if x.all_passed() == True ]
    failed = [ x for x in all_test_results.values() if x.all_passed() == False ]
    output = {  'harness_name' : 'TDVT',
                'actual_exp_paths_relative_to' : 'this',
                'successful_tests' : passed,
                'failed_tests' : failed
             }
    json_str = json.dumps(output, cls=TestOutputJSONEncoder)
    json_file_path = os.path.join(output_dir, 'tdvt_output.json')
    try:
        json_file = open(json_file_path, 'w', encoding='utf8')
        json_file.write(json_str)
        json_file.close()
    except Exception:
        LOG.log("Error writing ouput file [{0}].".format(json_file_path))

def get_csv_row_data(tds_name, test_name, passed, expected=None, diff_count=None, test_case=None, error_msg=None, error_type=None, time=None, generated_sql=None, actual_tuples=None, expected_tuples=None):
    return [tds_name, test_name, passed, expected, diff_count, test_case, error_msg, error_type, time, generated_sql, actual_tuples, expected_tuples]

def write_csv_test_output(all_test_results, tds_file, skip_header, output_dir):
    csv_file_path = os.path.join(output_dir, 'test_results.csv')
    try:
        file_out = open(csv_file_path, 'w', encoding='utf8')
    except IOError:
        LOG.log("Could not open output file [{0}].".format(csv_file_path))
        return
    
    #A few of the tests generate thousands of tuples. Limit how many to include in the csv since it makes it unweildly.
    TUPLE_DISPLAY_LIMIT = 100
    custom_dialect = csv.excel
    custom_dialect.lineterminator = '\n'
    custom_dialect.delimiter = ','
    custom_dialect.strict = True
    custom_dialect.skipinitialspace = True
    csv_out = csv.writer(file_out, dialect=custom_dialect, quoting=csv.QUOTE_MINIMAL)
    tupleLimitStr = '(' + str(TUPLE_DISPLAY_LIMIT) + ')tuples'
    actualTuplesHeader = 'Actual ' + tupleLimitStr
    expectedTuplesHeader = 'Expected ' + tupleLimitStr
    csvheader = ['TDSName','TestName','Passed','Closest Expected','Diff count','Test Case','Error Msg','Error Type','Query Time (ms)','Generated SQL', actualTuplesHeader, expectedTuplesHeader]
    if not skip_header:
        csv_out.writerow(csvheader)

    tdsname = os.path.splitext(os.path.split(tds_file)[1])[0]
    #Write the csv file.
    total_failed_tests = 0
    for path, test_result in all_test_results.items():
        generated_sql = ''
        test_name = test_result.get_name() if test_result.get_name() else path
        if test_result is None or test_result.actual_results is None:
            row_data = [tdsname, test_name, '0']
            if test_result is not None:
                row_data = get_csv_row_data(tdsname, test_name, '0', error_msg = test_result.get_failure_message(), error_type=test_result.get_failure_message())
            csv_out.writerow(row_data)
            total_failed_tests += 1
        else:
            matched = test_result.matched_expected_version
            test_case_index = 0
            for case in test_result.actual_results.test_case_map:
                diff_count = case.diff_count
                passed = 0
                if case.all_passed():
                    passed = 1
                else:
                    total_failed_tests += 1
                generated_sql = case.get_sql_text()
                test_case_name = case.name

                actual_tuples = "\n".join(case.get_tuples()[0:TUPLE_DISPLAY_LIMIT])
                if not test_result.best_matching_expected_results:
                    expected_tuples = ''
                else:
                    expected_tuples = "\n".join(test_result.best_matching_expected_results.test_case_map[test_case_index].get_tuples()[0:TUPLE_DISPLAY_LIMIT])

                error_msg = None
                if passed == 0:
                    error_msg = test_result.get_failure_message() if case.error_message is None or case.error_message is '' else case.error_message

                csv_out.writerow([tdsname, test_name, str(passed), str(matched), str(diff_count), test_case_name, str(error_msg), str(case.error_type), float(case.execution_time), generated_sql, actual_tuples, expected_tuples])
                test_case_index += 1

    file_out.close()

    return total_failed_tests

def process_test_results(all_test_results, tds_file, skip_header, output_dir):
    #Required for tube compatability.
    write_standard_test_output(all_test_results, output_dir)
    failed_test_count = write_csv_test_output(all_test_results, tds_file, skip_header, output_dir)
    return failed_test_count

def run_tests_parallel(test_names, test_config):
    all_test_results = {}
    tds_file = test_config.tds
    threads = []
    thread_lock = threading.Lock()

    thread_count = 0

    print ("LR Max threads: " + str(MAX_SUBPROCESSES))
    for test_file in test_names:
        while threading.activeCount() > (MAX_SUBPROCESSES):
            #print ("LR Sleeping: active threads " + str(threading.activeCount()))
            time.sleep(.05)

        thread_count += 1
        print ("LR starting thread : " + str(thread_count))
        threads.append(test_thread(thread_count, tds_file, test_file, test_config, thread_lock, all_test_results))

    for thread in threads:
        thread.join() #Wait until all threads are done executing
    
    return all_test_results

def generate_test_file_list_from_file(root_directory, config_file):
    """Read the config file and generate a list of tests."""
    allowed_tests = []
    exclude_tests = []
    exclude_tests.append('expected.')
    exclude_tests.append('actual.')

    reading_allowed = False
    reading_exclude = False
    for line in open(config_file, 'r', encoding='utf8'):
        if line[0] == '#':
            continue
        #Get rid of newline.
        line = line.strip()
        if line == '':
            continue
        elif line == 'allow:':
            reading_allowed = True
            reading_exclude = False
        elif line == 'exclude:':
            reading_allowed = False
            reading_exclude = True
        else:
            if reading_allowed:
                LOG.log("Allowing " + line)
                allowed_tests.append(line)
            elif reading_exclude:
                LOG.log("Excluding " + line)
                exclude_tests.append(line)
        

    #Allowed/exclude can be filenames or directory fragments.
    tests_to_run = []
    for a in allowed_tests:
        allowed_path = os.path.join(root_directory, a)
        if os.path.isfile(allowed_path):
            LOG.log("Adding file " + allowed_path)
            tests_to_run.append(allowed_path)
        elif os.path.isdir(allowed_path):
            LOG.log("Iterating directory " + allowed_path)
            for f in os.listdir(allowed_path):
                full_filename = os.path.join(allowed_path, f)
                if os.path.isfile(full_filename):
                    LOG.log("Adding file " + full_filename)
                    tests_to_run.append(full_filename)
        else:
            for f in glob.glob(allowed_path):
                full_filename = os.path.join(allowed_path, f)
                if os.path.isfile(full_filename):
                    LOG.log("Adding globbed file " + full_filename)
                    tests_to_run.append(full_filename)

    LOG.log("Found " + str(len(tests_to_run)) + " tests to run before exclusions.")

    final_test_list = list(tests_to_run)
    for test in tests_to_run:
        for ex in exclude_tests:
            try:
                regex = re.compile(ex)
                if re.search(regex, test) and test in final_test_list:
                    if VERBOSE: LOG.log("Removing test that matched: " + ex)
                    final_test_list.remove(test)
            except:
                print ("Error compiling regular expression for test file exclusions.")

    final_test_list = map(lambda x: os.path.normpath(x), final_test_list)
    return sorted(final_test_list)

def generate_test_file_list(root_directory, logical_query_config, combined_config, expected_dir):
    """The config can be either a file (*.cfg) or a path to a test. Take the config and expand it into the list of tests cases to run. These are fully qualified paths to test files.
       Return the sorted list of tests.

    """
    config_file = get_config_file_full_path(root_directory, combined_config)
    final_test_list = []
    if config_file == '':
        #Treat it as a path to one test file.
        if os.path.isfile(combined_config):
            final_test_list.append(combined_config)
        else:
            abs_path = os.path.join(root_directory, combined_config)
            if os.path.isfile( abs_path ):
                final_test_list.append(abs_path)
    else:
        final_test_list = generate_test_file_list_from_file(root_directory, config_file)

    expected_sub_dir = expected_dir
    #Make sure the expected output directories exist.
    if expected_sub_dir:
        dir_list = set([os.path.dirname(x) for x in final_test_list])
        if logical_query_config:
            dir_list = set()
            for x in final_test_list:
                t1, t2, t3, t4, expected_dir = get_logical_test_file_paths(x, expected_sub_dir)
                dir_list.add(expected_dir)
        for d in dir_list:
            d = os.path.join(d, expected_sub_dir)
            if not os.path.isdir(d):
                LOG.log("Making dir: {}".format(d))
                os.makedirs(d)

    LOG.log("Found final list of " + str(len(final_test_list)) + " tests to run.")
    for x in final_test_list:
        LOG.log("test " + x)

    return final_test_list

def find_file_path(root_directory, base_file, default_dir):
    """Return the full path to base_file using either the root_directory and base_file, or a default directory and base_file from there."""
    path_verbatim = os.path.join(root_directory, base_file)
    if os.path.isfile(path_verbatim):
        return path_verbatim

    path_inferred = os.path.join(root_directory, default_dir)
    path_inferred = os.path.join(path_inferred, base_file)
    return path_inferred

def get_config_file_full_path(root_directory, combined_config):
    """Return the full path to the config file to use for this test run."""
    config_file = combined_config
    
    if config_file[-4:] != '.cfg':
        return ''
    return find_file_path(root_directory, config_file, os.path.join("config", "gen"))

def get_tds_full_path(root_directory, tds):
    """Return the full path to the tds file to use for this test run."""
    return find_file_path(root_directory, tds, "tds")

def generate_files(force=False):
    """Generate the config files and logical query test permutations."""
    root_directory = get_root_dir()
    logical_input = get_path('logicaltests/generate/input/')
    logical_output = get_path('logicaltests/setup')
    generate_logical_files(logical_input, logical_output, force)
    LOG.log("Generating logical setup files...")
    generate_config_files(os.path.join(root_directory, os.path.join("config", "gen")), force)
    LOG.log("Generating config files...")
    return 0

def get_logical_test_file_paths(test_file, output_dir):
    """ Given the full path to logical test file, return all the paths to the expected output and gold result files.
        This depends on the logical tests main directory having 2 levels of subdirectories
        eg  tableau-tests/tdvt/logicaltests/setup/calcs
        and tableau-tests/tdvt/logicaltests/expected/calcs
    """
    #eg d:/dev/data-dev/tableau-tests/tdvt/logicaltests/setup/calcs
    expected_base_dir = os.path.split(test_file)[0]
    expected_base_dir, logical_subdir = os.path.split(expected_base_dir)
    #Split again to remove the 'setup' dir.
    expected_base_dir = os.path.split(expected_base_dir)[0]
    #eg d:/dev/data-dev/tableau-tests/tdvt/logicaltests/expected/calcs
    expected_base_dir = os.path.join(expected_base_dir, 'expected', logical_subdir)
    expected_output_dir = expected_base_dir

    #eg setup.bugs.b1713.dbo.xml
    expected_base_filename = os.path.split(test_file)[1]
    #Get the abstract test name without the datasource specific customization.
    #eg setup.bugs.b1713.xml
    new_base_filename = ".".join(expected_base_filename.split(".")[:-2]) + ".xml"
    #eg setup.bugs.b1713.dbo-combined.xml
    expected_output_filename = expected_base_filename.replace('.xml', '-combined.xml')
    
    temp_output_dir = output_dir if output_dir else expected_base_dir
    #eg full path to above file.
    existing_output_filepath = os.path.join(temp_output_dir, expected_output_filename)
    #if not os.path.isfile( existing_output_filepath ):
    #The filename and full path to the expected output from tabquery.
    new_output_filename = "actual." + new_base_filename
    new_output_filepath = os.path.join(temp_output_dir, new_output_filename)
    #Full path the expected file.
    new_base_filepath = os.path.join(expected_base_dir, new_base_filename)
    
    return existing_output_filepath, new_output_filepath, new_base_filename, new_base_filepath, expected_output_dir

def get_test_file_paths(root_directory, test_name, expected_sub_dir, output_dir):
    """Given a test name like 'exprtests/setup.calcs_data.txt', return full paths to the setup file its self, any actual file, and a list of any existing expected files (can be numbered)."""
    
    #d:\...\tdvt\exprtests
    test_path_base = os.path.join(root_directory, os.path.split(test_name)[0])
    test_name = os.path.split(test_name)[1]

    setupfile_path = os.path.join(test_path_base, test_name)
    actual_dir = output_dir if output_dir else test_path_base
    actualfile_path = os.path.join(actual_dir, test_name.replace('setup', 'actual.setup'))
    diff_file, diff_ext = os.path.splitext(actualfile_path)
    diff_file_path = diff_file + "_diff" + diff_ext

    expected_file_version = 0
    expected_filename = 'expected.' + test_name
    #Allow an expected subdir. This lets you run the standard set of tests with unique expected files (ie query timing or sql generation).
    expected_file_path = test_path_base
    if expected_sub_dir is not None and expected_sub_dir != '':
        expected_file_path = os.path.join(expected_file_path, expected_sub_dir)

    expected_file_path = os.path.join(expected_file_path, expected_filename)

    expected_file_list = []
    while os.path.isfile(expected_file_path):
        expected_file_list.append(expected_file_path)

        expected_file_version += 1
        #Everything but the ending.
        expected_file_parts = expected_filename.split(".")[:-1]
        #Put the number in.
        expected_file_parts.append( str(expected_file_version) )
        #Add the ending again.
        expected_file_parts.append( expected_filename.split(".")[-1] )
        expected_file = ".".join(expected_file_parts)

        expected_file_path = os.path.join(test_path_base, expected_file)

    if not expected_file_list:
        #Always add the base expected file even if it doesn't exist. The callers will use this to copy the actual.
        expected_file_list.append(expected_file_path)

    for filepath in expected_file_list:
        LOG.log("Found expected filepath " + filepath)

    return (actualfile_path, diff_file_path, setupfile_path, expected_file_list)

def run_diff(test_config, root_directory, diff):
    allowed_test_path = os.path.join(root_directory, diff)
    test_path_base = os.path.split(allowed_test_path)[0]
    test_name = os.path.split(allowed_test_path)[1]

    actual, actual_diff, setup, expected_files = get_test_file_paths(test_path_base, test_name, test_config.expected_dir, test_config.output_dir)

    LOG.log('actual_path: ' + actual)
    diff_count_map = {}

    for f in expected_files:
        LOG.log('expected_path: ' + f)
        if os.path.isfile(f) and os.path.isfile(actual):
            LOG.log("Diffing " + actual + " and " + f)
            actual_xml = xml.etree.ElementTree.parse(actual).getroot()
            expected_xml = xml.etree.ElementTree.parse(f).getroot()
            result = TestResult()
            result.add_actual_output(TestOutput(actual_xml, test_config), actual)
            expected_output = TestOutput(expected_xml, test_config)
            num_diffs, diff_string = diff_test_results(result, expected_output)
            LOG.log(diff_string)
            diff_count_map[f] = sum(num_diffs)

    for t in diff_count_map:
        LOG.log(t + ' Number of differences: ' + str(diff_count_map[t]))
    return 0

def run_failed_tests_impl(run_file, root_directory, parser):
    """Run the failed tests from the json output file."""
    tests = {}
    try:
        tests = json.load(open(run_file, 'r', encoding='utf8'))
    except:
        LOG.log("Error opening " + run_file)
        return

    test_to_run = {}
    test_to_run['logical'] = {}
    test_to_run['expression'] = {}
    expr_tests = test_to_run['expression']
    log_tests = test_to_run['logical']

    failed_tests = tests['failed_tests']
    for f in failed_tests:
        LOG.log("Found failed test: " + f['test_file'])
        tt = f['test_type']
        tds = f['tds']
        if tt in (EXPR_CONFIG_ARG, EXPR_CONFIG_ARG_SHORT):
            if tds not in expr_tests:
                expr_tests[tds] = []
            expr_tests[tds].append(f['test_file'])

        if tt in (LOGICAL_CONFIG_ARG, LOGICAL_CONFIG_ARG_SHORT):
            if tds not in log_tests:
                log_tests[tds] = []
            log_tests[tds].append(f['test_file'])

    all_test_results = {}
    for tds in expr_tests:
        if len(expr_tests[tds]) > 0:
            #Get the saved additional arguments.
            new_args = parser.parse_args(f['other_args'].split())
            test_config = TdvtTestConfig(from_args=new_args, tds_file=tds)
            test_config.logical = False
            results = run_tests_parallel(expr_tests[tds], test_config)
            all_test_results.update(results)
    
    for tds in log_tests:
        if len(log_tests[tds]) > 0:
            new_args = parser.parse_args(f['other_args'].split())
            test_config = TdvtTestConfig(from_args=new_args, tds_file=tds)
            test_config.logical = True
            results = run_tests_parallel(log_tests[tds], test_config)
            all_test_results.update(results)
    return all_test_results

def run_failed_tests(run_file, root_directory, parser):
    """Run the failed tests from the json output file."""
    #See if we need to generate test setup files.
    generate_files(False)
    all_test_results = run_failed_tests_impl(run_file, root_directory, parser)
    return process_test_results(all_test_results, '', False, root_directory)

def run_tests(test_config):
    #See if we need to generate test setup files.
    root_directory = get_root_dir()
    generate_files( False)

    tds_file = get_tds_full_path(root_directory, test_config.tds)
    test_config.tds = tds_file
    all_test_results = {}

    all_test_results = run_tests_parallel(generate_test_file_list(root_directory, test_config.logical, test_config.config_file, test_config.expected_dir), test_config)
    output_dir = test_config.output_dir if test_config.output_dir else root_directory
    return process_test_results(all_test_results, tds_file, test_config.noheader, output_dir)

def init_logging(root_directory=None, verbose=False, output_dir=''):
    global LOG
    if not root_directory:
        root_directory = get_root_dir()
    LOG = Logger(root_directory, verbose, output_dir)
    return LOG

def init_arg_parser():
    parser = argparse.ArgumentParser(description='Tableau Datasource Verification Tool. Return code is the number of failed tests.')
    parser.add_argument(EXPR_CONFIG_ARG, EXPR_CONFIG_ARG_SHORT, dest='expression_config', help='Config file (*.cfg) containing relative paths to expression tests or a path to a test file.', required=False)
    parser.add_argument(LOGICAL_CONFIG_ARG, LOGICAL_CONFIG_ARG_SHORT, dest='logical_query_config', help='Config file (*.cfg) containing relative paths to logical query files or a path to a test file.', required=False)
    parser.add_argument('-f', dest='run_file', help='Json file containing failed tests to run.', required=False)
    parser.add_argument(TDS_CONFIG_ARG, TDS_CONFIG_ARG_SHORT, dest='tds', help='TDS file to use when running the tests.', required=False)
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Verbose output.', required=False)
    parser.add_argument('--compare-sql', dest='compare_sql', action='store_true', help='Compare SQL.', required=False)
    parser.add_argument('--nocompare-tuples', dest='nocompare_tuples', action='store_true', help='Do not compare Tuples.', required=False)
    parser.add_argument('--noheader', dest='noheader', action='store_true', help='Do not write a header in the resulting csv file.', required=False)
    parser.add_argument('--generate', dest='generate', action='store_true', help='Generate the config and logical query files.', required=False)
    parser.add_argument('--diff-test', '-dd', dest='diff', help='Diff the results of the given test (ie exprtests/standard/setup.calcs_data.txt) against the expected files. Can be used with the sql and tuple options.', required=False)
    parser.add_argument('--threads', '-t', dest='thread_count', type=int, help='Max number of threads to use.', required=False)
    parser.add_argument('--expected-dir', dest='expected_dir', help='Unique subdirectory for expected files.', required=False)
    parser.add_argument('--output-dir', dest='output_dir', help='Absolute path to directory to store actual files.', required=False)
    parser.add_argument('--suite', dest='suite', help='Name of the test suite.', required=False)
    parser.add_argument('-DOverride', dest='d_override', help='Tableau override option. -D is prepended to the value and it is then passed to tabquerycli. For example [-DOverride ModifyDialect=1] becomes [-DModifyDialect=1] while [-DOverride Override=DrillConnector] becomes [-DOverride=DrillConnector]', required=False)
    return parser

def configure_tabquery_path():
    global TAB_CLI_EXE
    config = configparser.ConfigParser()
    
    config.read(get_ini_path('config/tdvt', 'tdvt'))

    if sys.platform.startswith("darwin"):
        TAB_CLI_EXE = config['DEFAULT']['TAB_CLI_EXE_MAC']
    elif sys.platform.startswith("linux"):
        TAB_CLI_EXE = config['DEFAULT']['TAB_CLI_EXE_LINUX']
    else:
        TAB_CLI_EXE = config['DEFAULT']['TAB_CLI_EXE_X64']

def get_root_dir():
    return get_path('')

def main():
    configure_tabquery_path()
    parser = init_arg_parser()
    global args
    args = parser.parse_args()
    VERBOSE = False
    if args.verbose:
        VERBOSE = True
    if args.diff:
        #Set verbose so the user sees something.
        VERBOSE = True

    root_directory = get_root_dir()
    return_code = 0

    args_copy = list(sys.argv)
    test_config = TdvtTestConfig(from_args=args)
    test_config.set_invocation(args_copy)

    LOG = init_logging(root_directory, VERBOSE, test_config.output_dir)
    LOG.log("Starting : " + str(test_config))
    LOG.log("Using root_dir: " + root_directory)

    if args.thread_count:
        MAX_SUBPROCESSES = args.thread_count
        LOG.log("Setting max thread count to: " + str(MAX_SUBPROCESSES))

    if args.generate:
        return_code = generate_files( True)
    elif args.diff:
        return_code = run_diff(test_config, root_directory, args.diff)
    elif args.run_file:
        return_code = run_failed_tests(args.run_file, root_directory, parser)
    elif args.combined_config:
        test_config.tds_file = args.tds
        return_code = run_tests(test_config)
    else:
        print ("No valid run options found.")

    sys.exit(return_code)

if __name__ == '__main__':
    main()
