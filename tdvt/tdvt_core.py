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
import queue
import time
import xml.etree.ElementTree
import glob
import json
import csv
import configparser
import logging
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
abort_test_run = False

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

class TdvtTestConfig(object):
    """Track how items were tested. This captures how tdvt was invoked."""
    def __init__(self, tested_sql = False, tested_tuples = True, tds = '', expected_dir = '', config = '', output_dir = '', logical = False, verbose = False, override = '', suite_name = '', from_args = None, thread_count = 4, from_json = None):
        self.tested_sql = tested_sql
        self.tested_tuples = tested_tuples
        self.expected_dir = expected_dir
        self.output_dir = output_dir
        self.logical = logical
        self.config_file = config
        self.suite_name = suite_name
        self.d_override = override
        self.verbose = verbose
        self.tds = tds
        self.command_line = ''
        self.noheader = False
        self.thread_count = thread_count
        if from_args:
            self.init_from_args(from_args)
        if from_json:
            self.init_from_json(from_json)

    def init_from_args(self, args):
        if args.compare_sql: 
            self.tested_sql = args.compare_sql 
        if args.nocompare_tuples:
            self.tested_tuples = False
        if args.expected_dir:
            self.expected_dir = args.expected_dir

        if args.thread_count_tdvt:
            self.thread_count = args.thread_count_tdvt

    def init_from_json(self, json):
        self.tested_sql = json['tested_sql']
        self.tested_tuples = json['tested_tuples']
        self.expected_dir = json['expected_dir']
        self.output_dir = json['output_dir']
        self.logical = json['logical']
        self.config_file = json['config_file']
        self.suite_name = json['suite_name']
        self.d_override = json['d_override']
        self.verbose = json['verbose']
        self.tds = json['tds']
        self.noheader = json['noheader']
        self.thread_count = json['thread_count']

    def __str__(self):
        return "suite [{}]: tested sql [{}]: tested tuples [{}]: expected dir [{}]: output dir [{}]: logical [{}]: config file [{}]: override [{}]: tds [{}]: thread [{}]".format(self.suite_name, self.tested_sql, self.tested_tuples, self.expected_dir, self.output_dir, self.logical, self.config_file, self.d_override, self.tds, self.thread_count)

    def __json__(self):
        return {
        'tested_sql' : self.tested_sql, 
        'tested_tuples' : self.tested_tuples, 
        'expected_dir' : self.expected_dir, 
        'output_dir' : self.output_dir, 
        'logical' : self.logical, 
        'config_file' : self.config_file, 
        'suite_name' : self.suite_name, 
        'd_override' : self.d_override, 
        'verbose' : self.verbose, 
        'tds' : self.tds, 
        'noheader' : self.noheader, 
        'thread_count' : self.thread_count }

class TestResult(object):
    """Information about a test suite run."""
    def __init__(self, base_name = '', test_config = TdvtTestConfig(), test_file = ''):
        self.name = base_name
        self.test_config = test_config
        self.matched_expected_version = 0
        self.test_failed_to_run = False
        self.test_timed_out = False
        self.actual_results = None
        self.diff_count = 0
        self.best_matching_expected_results = None
        self.test_file = test_file
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

        suite_name = '' if not obj.test_config.suite_name else obj.test_config.suite_name
        case_name = '' if not obj.get_name() else obj.get_name()
        test_type = '-q' if obj.test_config.logical else '-e' 
        json_output = {'suite' : suite_name, 
                'class' : 'TDVT',
                'case' : suite_name + '.' + case_name, 
                'test_file' : obj.test_file, 
                'test_type' : test_type, 
                'test_config' : obj.test_config.__json__(),
                'tds' : obj.test_config.tds, 
                'expected' : obj.path_to_expected,
               }
        if obj.all_passed():
            return json_output

        failtype = ','.join(obj.get_exceptions())
        json_output['failtype'] = failtype if failtype else 'test_failure'
        json_output['message'] = obj.get_failure_message()
        json_output['actual'] = obj.path_to_actual
        return json_output

    
class QueueWork(object):
    def __init__(self, test_config, test_file):
        self.test_config = test_config
        self.test_file = test_file
        self.results = {}
        self.timeout_seconds = 1200
        
def do_test_queue_work(i, q):
    """This will be called in a queue.join() context, so make sure to mark all work items as done and
    continue through the loop. Don't try and exit or return from here if there are still work items in the queue.
    See the python queue documentation."""

    abort_test_run = False
    while True:
        #This blocks if the queue is empty.
        work = q.get()

        logging.debug("\nRunning test:" + work.test_file)
        if not os.path.isfile(work.test_file):
            logging.debug("Error opening file:" + work.test_file)
            q.task_done()
            continue

        cli_arg = "-q" if work.test_config.logical else "-e"

        cmdline = [TAB_CLI_EXE]
        cmdline_base = [cli_arg, work.test_file]
        cmdline.extend(cmdline_base)
        tds_arg = ["-d", work.test_config.tds]
        cmdline.extend(tds_arg)
        cmdline.extend(["--combined"])

        expected_output_dir = work.test_config.output_dir

        if work.test_config.logical:
            existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(work.test_file, work.test_config.output_dir)
            expected_output_dir = expected_output_dir if expected_output_dir else expected_dir

        if expected_output_dir:
            if not os.path.isdir(expected_output_dir):
                logging.debug("Making dir: {}".format(expected_output_dir))
                try:
                    os.makedirs(expected_output_dir)
                except FileExistsError:
                    pass
            cmdline.extend(["--output-dir", expected_output_dir])

        if work.test_config.d_override:
            cmdline.extend(["-D" + work.test_config.d_override])

        work.test_config.command_line = cmdline

        if abort_test_run:
            #Do this here so we have the repro information from above.
            logging.debug("\nAborting test:" + work.test_file)
            result = TestResult(get_base_test(work.test_file), work.test_config, work.test_file)
            result.test_failed_to_run = True
            work.results[work.test_file] = result
            q.task_done()
            continue

        logging.debug(" calling " + ' '.join(cmdline))

        cmd_output = None
        try:
            cmd_output = subprocess.check_output(cmdline, stderr=subprocess.STDOUT, universal_newlines=True, timeout=work.timeout_seconds)
        except subprocess.CalledProcessError as e:
            cmd_output = e.output
            if not VERBOSE: sys.stdout.write('F')
        except subprocess.TimeoutExpired as e:
            logging.debug("Test timed out: " + work.test_file)
            result = TestResult(get_base_test(work.test_file), work.test_config, work.test_file)
            result.test_timed_out = True
            work.results[work.test_file] = result
            if not VERBOSE: sys.stdout.write('F')
            q.task_done()
            continue

        if cmd_output:
            logging.debug(str(cmd_output))

        test_name = get_base_test(work.test_file)
        new_test_file = work.test_file
        if work.test_config.logical:
            existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(work.test_file, work.test_config.output_dir)
            if not os.path.isfile( existing_output_filepath ):
                logging.debug("Error: could not find test output file:" + existing_output_filepath)
                result = TestResult(base_test_name, work.test_config, work.test_file)
                work.results[work.test_file] = result
                if not VERBOSE: sys.stdout.write('F')
                q.task_done()
                continue

            #Copy the test process filename to the actual. filename.
            logging.debug("Copying {0} to {1}".format(existing_output_filepath, actual_output_filepath))
            try_move(existing_output_filepath, actual_output_filepath)

            #Make sure to set the generic (ie non-templatized) test name.
            test_name = get_base_test(base_filepath)
            new_test_file = base_filepath

        result = compare_results(test_name, new_test_file, work.test_file, work.test_config)
        result.test_config = work.test_config

        if result == None:
            result = TestResult(test_file = work.test_file)
            result.test_failed_to_run = True

        if not VERBOSE:
            sys.stdout.write('.' if result.all_passed() else 'F')
            sys.stdout.flush()

        work.results[work.test_file] = result
        #If this failed with a password, connection error or similar then abort this entire test run (which uses the same tds file). This will prevent running hundreds of tests that have to wait for a timeout before failing.
        for ex in result.get_exceptions():
            if ex in ['BadPassword', 'Disconnect', 'NoDriver', 'UnableToConnect', 'Unlicensed', 'ExpiredPassword', 'NoPassword']:
                abort_test_run = True

        q.task_done()

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
    logging.debug("Saving diff of actual and expected as [{}]".format(diff_file))
    try:
        f = open(diff_file, 'w')
        f.write("Diff of [{}] and [{}].\n".format(actual_file, expected_file))
        f.write(diff_string)
        f.close()
    except:
        pass

def compare_results(test_name, test_file, full_test_file, test_config):
    """Return a TestResult object that specifies what was tested and whether it passed.
       test_file is the full path to the test file (base test name without any logical specification).
       full_test_file is the full path to the actual test file.

    """
    base_test_file = get_base_test(test_file)
    test_file_root = os.path.split(test_file)[0]
    actual_file, actual_diff_file, setup, expected_files = get_test_file_paths(test_file_root, base_test_file, test_config.expected_dir, test_config.output_dir)
    result = TestResult(test_name, test_file = full_test_file)
    #There should be an actual file at this point. eg actual.setup.math.txt.
    if not os.path.isfile(actual_file):
        logging.debug("Did not find actual file: " + actual_file)
        return result

    try:
        actual_xml = xml.etree.ElementTree.parse(actual_file).getroot()
        actual_output = TestOutput(actual_xml, test_config)
        result.add_actual_output(actual_output, actual_file)
    except xml.etree.ElementTree.ParseError as e:
        logging.debug("Exception parsing actual file: " + actual_file + " exception: " + str(e))
        return result

    expected_file_version = 0
    for expected_file in expected_files:
        if not os.path.isfile(expected_file):
            logging.debug("Copying actual [{}] to expected [{}]".format(actual_file, expected_file))
            #There is an actual but no expected, copy the actual to expected and return since there is nothing to compare against.
            try_move(actual_file, expected_file)
            return result
        #Try other possible expected files. These are numbered like 'expected.setup.math.1.txt', 'expected.setup.math.2.txt' etc.
        logging.debug(threading.current_thread().name + " Comparing " + actual_file + " to " + expected_file)
        expected_output = TestOutput(xml.etree.ElementTree.parse(expected_file).getroot(), test_config)
        
        diff_counts, diff_string = diff_test_results(result, expected_output)
        result.set_best_matching_expected_output(expected_output, expected_file, expected_file_version, diff_counts)

        if result.all_passed():
            logging.debug(threading.current_thread().name + " Results match expected number: " + str(expected_file_version))
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
        logging.debug("Error writing ouput file [{0}].".format(json_file_path))

def get_csv_row_data(tds_name, test_name, passed, expected=None, diff_count=None, test_case=None, error_msg=None, error_type=None, time=None, generated_sql=None, actual_tuples=None, expected_tuples=None):
    return [tds_name, test_name, passed, expected, diff_count, test_case, error_msg, error_type, time, generated_sql, actual_tuples, expected_tuples]

def write_csv_test_output(all_test_results, tds_file, skip_header, output_dir):
    csv_file_path = os.path.join(output_dir, 'test_results.csv')
    try:
        file_out = open(csv_file_path, 'w', encoding='utf8')
    except IOError:
        logging.debug("Could not open output file [{0}].".format(csv_file_path))
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
    if not all_test_results:
        return
    #Required for tube compatability.
    write_standard_test_output(all_test_results, output_dir)
    failed_test_count = write_csv_test_output(all_test_results, tds_file, skip_header, output_dir)
    return failed_test_count

def run_tests_parallel(test_names, test_config):
    all_test_results = {}
    tds_file = test_config.tds
    test_queue = queue.Queue()
    all_work = []

    #Create the worker threads.
    logging.debug("Running " + str(test_config.thread_count) + " worker threads.")
    for i in range(0, test_config.thread_count):
        worker = threading.Thread(target=do_test_queue_work, args=(i, test_queue))
        worker.setDaemon(True)
        worker.start()

    #Build the queue of work.
    for test_file in test_names:
        work = QueueWork(test_config, test_file)
        test_queue.put(work)
        all_work.append(work)

    #Do the work.
    test_queue.join()
    
    #Analyze the results of the work.
    for work in all_work:
        all_test_results.update(work.results)

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
                logging.debug("Allowing " + line)
                allowed_tests.append(line)
            elif reading_exclude:
                logging.debug("Excluding " + line)
                exclude_tests.append(line)
        

    #Allowed/exclude can be filenames or directory fragments.
    tests_to_run = []
    for a in allowed_tests:
        allowed_path = os.path.join(root_directory, a)
        if os.path.isfile(allowed_path):
            logging.debug("Adding file " + allowed_path)
            tests_to_run.append(allowed_path)
        elif os.path.isdir(allowed_path):
            logging.debug("Iterating directory " + allowed_path)
            for f in os.listdir(allowed_path):
                full_filename = os.path.join(allowed_path, f)
                if os.path.isfile(full_filename):
                    logging.debug("Adding file " + full_filename)
                    tests_to_run.append(full_filename)
        else:
            for f in glob.glob(allowed_path):
                full_filename = os.path.join(allowed_path, f)
                if os.path.isfile(full_filename):
                    logging.debug("Adding globbed file " + full_filename)
                    tests_to_run.append(full_filename)

    logging.debug("Found " + str(len(tests_to_run)) + " tests to run before exclusions.")

    final_test_list = list(tests_to_run)
    for test in tests_to_run:
        for ex in exclude_tests:
            try:
                regex = re.compile(ex)
                if re.search(regex, test) and test in final_test_list:
                    if VERBOSE: logging.debug("Removing test that matched: " + ex)
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
                logging.debug("Making dir: {}".format(d))
                os.makedirs(d)

    logging.debug("Found final list of " + str(len(final_test_list)) + " tests to run.")
    if len(final_test_list) == 0:
        logging.warn("Did not find any tests to run.")
        print("Did not find any tests to run.")

    for x in final_test_list:
        logging.debug("test " + x)

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
    #First look for a local tds file (in the place you ran this module, not in the module installation dir).
    local_file = find_file_path(os.getcwd(), tds, "tds")
    if os.path.isfile(local_file):
        return local_file
    return find_file_path(root_directory, tds, "tds")

def generate_files(force=False):
    """Generate the config files and logical query test permutations."""
    root_directory = get_root_dir()
    logical_input = get_path('logicaltests/generate/input/')
    logical_output = get_path('logicaltests/setup')
    generate_logical_files(logical_input, logical_output, force)
    logging.debug("Generating logical setup files...")
    generate_config_files(os.path.join(root_directory, os.path.join("config", "gen")), force)
    logging.debug("Generating config files...")
    return 0

def get_logical_test_file_paths(test_file, output_dir):
    """ Given the full path to logical test file, return all the paths to the expected output and gold result files.
        This depends on the logical tests main directory having 2 levels of subdirectories
        eg  tdvt/logicaltests/setup/calcs
        and tdvt/logicaltests/expected/calcs
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
        logging.debug("Found expected filepath " + filepath)
    return (actualfile_path, diff_file_path, setupfile_path, expected_file_list)

def run_diff(test_config, diff):
    root_directory = get_root_dir()
    allowed_test_path = os.path.join(root_directory, diff)
    test_path_base = os.path.split(allowed_test_path)[0]
    test_name = os.path.split(allowed_test_path)[1]

    actual, actual_diff, setup, expected_files = get_test_file_paths(test_path_base, test_name, test_config.expected_dir, test_config.output_dir)

    logging.debug('actual_path: ' + actual)
    diff_count_map = {}

    for f in expected_files:
        logging.debug('expected_path: ' + f)
        if os.path.isfile(f) and os.path.isfile(actual):
            logging.debug("Diffing " + actual + " and " + f)
            actual_xml = xml.etree.ElementTree.parse(actual).getroot()
            expected_xml = xml.etree.ElementTree.parse(f).getroot()
            result = TestResult()
            result.add_actual_output(TestOutput(actual_xml, test_config), actual)
            expected_output = TestOutput(expected_xml, test_config)
            num_diffs, diff_string = diff_test_results(result, expected_output)
            logging.debug(diff_string)
            diff_count_map[f] = sum(num_diffs)

    for t in diff_count_map:
        logging.debug(t + ' Number of differences: ' + str(diff_count_map[t]))
    return 0

def run_failed_tests_impl(run_file, root_directory):
    """Run the failed tests from the json output file."""
    tests = {}
    try:
        tests = json.load(open(run_file, 'r', encoding='utf8'))
    except:
        logging.debug("Error opening " + run_file)
        return

    test_to_run = {}
    test_to_run['logical'] = {}
    test_to_run['expression'] = {}
    expr_tests = test_to_run['expression']
    log_tests = test_to_run['logical']

    failed_tests = tests['failed_tests']
    for f in failed_tests:
        logging.debug("Found failed test: " + f['test_file'])
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
            test_config = TdvtTestConfig(from_json=f['test_config'], tds=tds)
            test_config.logical = False
            results = run_tests_parallel(expr_tests[tds], test_config)
            all_test_results.update(results)
    
    for tds in log_tests:
        if len(log_tests[tds]) > 0:
            test_config = TdvtTestConfig(from_json=f['test_config'], tds=tds)
            test_config.logical = True
            results = run_tests_parallel(log_tests[tds], test_config)
            all_test_results.update(results)
    return all_test_results

def run_failed_tests(run_file):
    """Run the failed tests from the json output file."""
    #See if we need to generate test setup files.
    root_directory = get_root_dir()
    all_test_results = run_failed_tests_impl(run_file, root_directory)
    return process_test_results(all_test_results, '', False, root_directory)

def run_tests(test_config):
    #See if we need to generate test setup files.
    root_directory = get_root_dir()
    output_dir = test_config.output_dir if test_config.output_dir else root_directory

    tds_file = get_tds_full_path(root_directory, test_config.tds)
    test_config.tds = tds_file
    all_test_results = {}

    all_test_results = run_tests_parallel(generate_test_file_list(root_directory, test_config.logical, test_config.config_file, test_config.expected_dir), test_config)
    return process_test_results(all_test_results, tds_file, test_config.noheader, output_dir)

def configure_tabquery_path():
    global TAB_CLI_EXE
    config = configparser.ConfigParser()
    
    tdvt_cfg = get_ini_path_local_first('config/tdvt', 'tdvt')
    logging.debug("Reading tdvt ini file [{}]".format(tdvt_cfg))
    config.read(tdvt_cfg)

    if sys.platform.startswith("darwin"):
        TAB_CLI_EXE = config['DEFAULT']['TAB_CLI_EXE_MAC']
    elif sys.platform.startswith("linux"):
        TAB_CLI_EXE = config['DEFAULT']['TAB_CLI_EXE_LINUX']
    else:
        TAB_CLI_EXE = config['DEFAULT']['TAB_CLI_EXE_X64']

def get_root_dir():
    return get_path('')

