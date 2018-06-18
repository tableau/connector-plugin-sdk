"""
    Tableau Datasource Verification Tool
    Run logical queiries and expression tests against datasources.

"""

import argparse
import copy
import csv
import glob
import json
import logging
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree
import zipfile
from .config_gen.genconfig import generate_config_files
from .config_gen.gentests import generate_logical_files
from .config_gen.test_config import TestFile
from .resources import *
from .test_results import *
from .tabquery import build_tabquery_command_line

EXPR_CONFIG_ARG = '--expression-config'
EXPR_CONFIG_ARG_SHORT = '-e'
LOGICAL_CONFIG_ARG = '--logical-query-config'
LOGICAL_CONFIG_ARG_SHORT = '-q'
TDS_CONFIG_ARG = '--tds'
TDS_CONFIG_ARG_SHORT = '-d'
ALWAYS_GENERATE_EXPECTED = False
abort_test_run = False


class QueueWork(object):
    def __init__(self, test_config, test_file):
        self.test_config = test_config
        self.results = {}
        self.thread_id = -1
        self.timeout_seconds = 1200
        self.cmd_output = None
        self.saved_error_message = None
        self.timeout = False
        self.relative_test_file = test_file.relative_test_path
        self.set_base_test_names(test_file.test_path)
        self.log_zip_file = ''
        self.verbose = test_config.verbose

    def set_base_test_names(self, test_file):
        self.test_name = get_base_test(test_file)
        self.test_file = test_file
        if self.test_config.logical:
            existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(self.test_file, self.test_config.output_dir)
            #Make sure to set the generic (ie non-templatized) test name.
            self.test_name = base_test_name
        
    def handle_test_failure(self, result=None, error_msg=None):
        if result == None:
            result = TestResult(self.test_name, self.test_config, self.test_file, self.relative_test_file)
            result.cmd_output = self.cmd_output

        err = error_msg if error_msg else self.saved_error_message
        if err:
            result.overall_error_message = err

        self.results[self.test_file] = result
           
    def handle_timeout_test_failure(self):
        result = TestResult(self.test_name, self.test_config, self.test_file, self.relative_test_file)
        result.error_status = TestErrorTimeout()
        self.handle_test_failure(result)
        self.timeout = True

    def handle_abort_test_failure(self):
        result = TestResult(self.test_name, self.test_config, self.test_file, self.relative_test_file)
        result.error_status = TestErrorAbort()
        self.handle_test_failure(result)

    def has_error(self):
        return self.saved_error_message is not None

    def is_timeout(self):
        return self.timeout

    def run(self, thread_id):
        self.thread_id = thread_id
        thread_msg = "Thread-[{0}] ".format(self.thread_id)

        #Setup a subdirectory for the log files.
        self.test_config.log_dir = os.path.join(self.test_config.output_dir, self.test_name.replace('.', '_'))
        os.makedirs(self.test_config.log_dir)
        cmdline = build_tabquery_command_line(self)
        logging.debug(thread_msg + " calling " + ' '.join(cmdline))

        start_time = time.perf_counter()
        try:
            self.cmd_output = str(subprocess.check_output(cmdline, stderr=subprocess.STDOUT, universal_newlines=True, timeout=self.timeout_seconds))
        except subprocess.CalledProcessError as e:
            logging.debug(thread_msg + "CalledProcessError for " + self.test_file + ". Error: "  + e.output)
            #Let processing continue so it can try and find any output file which will contain database error messages.
            #Save the error message in case there is no result file to get it from.
            self.saved_error_message = e.output
            self.cmd_output = e.output
        except subprocess.TimeoutExpired as e:
            logging.debug(thread_msg + "Test timed out: " + self.test_file)
            sys.stdout.write('T')
            self.handle_timeout_test_failure()
        except RuntimeError as e:
            logging.debug(thread_msg + "RuntimeError " + str(e) + " for " + work.test_file + " dsname " + work.test_config.dsnmae)

        total_time_ms = (time.perf_counter() - start_time) * 1000

        #Copy log files to a zip file for later optional use.
        self.log_zip_file = os.path.join(self.test_config.log_dir, 'all_logs.zip')
        logging.debug(thread_msg + "Creating log zip file: {0}".format(self.log_zip_file))
        mode = 'w' if not os.path.isfile(self.log_zip_file) else 'a'
        with zipfile.ZipFile(self.log_zip_file, mode, zipfile.ZIP_DEFLATED) as myzip:
            log_files = glob.glob(os.path.join(self.test_config.log_dir, 'log*.txt'))
            log_files.extend(glob.glob(os.path.join(self.test_config.log_dir, 'tabprotosrv*.txt')))
            log_files.extend(glob.glob(os.path.join(self.test_config.log_dir, 'crashdumps/*')))
            for log in log_files:
                myzip.write(log, os.path.basename(log))

        logging.debug(thread_msg + "Command line output for " + self.test_file + ". " + str(self.cmd_output))
        return total_time_ms


def do_test_queue_work(i, q):
    """This will be called in a queue.join() context, so make sure to mark all work items as done and
    continue through the loop. Don't try and exit or return from here if there are still work items in the queue.
    See the python queue documentation."""

    abort_test_run = False
    while True:
        #This blocks if the queue is empty.
        work = q.get()

        thread_msg = "Thread-[{0}] ".format(i)
        logging.debug(thread_msg + "Running test:" + work.test_file)
        if not os.path.isfile(work.test_file):
            logging.debug(thread_msg + "Error opening file:" + work.test_file)
            q.task_done()
            continue


        if abort_test_run:
            #Do this here so we have the repro information from above.
            logging.debug(thread_msg + "Aborting test:" + work.test_file)
            sys.stdout.write('A')
            work.handle_abort_test_failure()
            q.task_done()
            continue

        total_time_ms = work.run(i)

        #Exit early if it is a timeout.
        if work.is_timeout():
            q.task_done()
            continue

        new_test_file = work.test_file
        if work.test_config.logical:
            existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(work.test_file, work.test_config.output_dir)
            if not os.path.isfile( existing_output_filepath ):
                logging.debug(thread_msg + "Error: could not find test output file:" + existing_output_filepath)
                sys.stdout.write('?')
                work.handle_test_failure()
                q.task_done()
                continue

            #Copy the test process filename to the actual. filename.
            logging.debug(thread_msg + "Copying test process output {0} to actual file {1}".format(existing_output_filepath, actual_output_filepath))
            try_move(existing_output_filepath, actual_output_filepath)

            new_test_file = base_filepath

        result = compare_results(work.test_name, new_test_file, work.test_file, work.test_config)
        result.relative_test_file = work.relative_test_file
        result.run_time_ms = total_time_ms
        result.test_config = work.test_config
        result.cmd_output = work.cmd_output

        if result == None:
            result = TestResult(test_file = work.test_file, relative_test_file = work.relative_test_file)
            result.error_case = TestErrorStartup()

        sys.stdout.write('.' if result.all_passed() else 'F')
        sys.stdout.flush()

        #If everything passed delete the log files so we don't collect a bunch of useless logs.
        if result.all_passed() and not work.verbose:
            try:
                os.remove(work.log_zip_file)
            except Exception as e:
                logging.debug(thread_msg + "got exception deleting zipped log file: " + str(e))
                pass

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

    test_case_count = result.get_test_case_count()
    diff_counts = [0] * test_case_count
    diff_string = ''
    #Go through all test cases.
    for test_case in range(0, test_case_count):
        expected_testcase_result = expected_output.get_test_case(test_case)
        actual_testcase_result = result.get_test_case(test_case)
        if not actual_testcase_result:
            continue
        if expected_testcase_result is None:
            actual_testcase_result.passed_sql = False
            actual_testcase_result.passed_tuples = False
            continue

        config = result.test_config
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
    actual_file, actual_diff_file, setup, expected_files, next_path = get_test_file_paths(test_file_root, base_test_file, test_config.expected_dir, test_config.output_dir)
    result = TestResult(test_name, test_config, full_test_file)
    #There should be an actual file at this point. eg actual.setup.math.txt.
    if not os.path.isfile(actual_file):
        logging.debug("Did not find actual file: " + actual_file)
        return result

    try:
        actual_xml = xml.etree.ElementTree.parse(actual_file).getroot()
        result.add_test_results(actual_xml, actual_file)
    except xml.etree.ElementTree.ParseError as e:
        logging.debug("Exception parsing actual file: " + actual_file + " exception: " + str(e))
        return result

    expected_file_version = 0
    for expected_file in expected_files:
        if not os.path.isfile(expected_file):
            logging.debug("Did not find expected file " + expected_file)
            if ALWAYS_GENERATE_EXPECTED:
                #There is an actual but no expected, copy the actual to expected and return since there is nothing to compare against.
                #This is off by default since it can make tests pass when they should really fail. Might be a good command line option though.
                logging.debug("Copying actual [{}] to expected [{}]".format(actual_file, expected_file))
                try_move(actual_file, expected_file)
            return result
        #Try other possible expected files. These are numbered like 'expected.setup.math.1.txt', 'expected.setup.math.2.txt' etc.
        logging.debug(threading.current_thread().name + " Comparing " + actual_file + " to " + expected_file)
        expected_output = TestResult(test_config=test_config)
        try:
            expected_output.add_test_results(xml.etree.ElementTree.parse(expected_file).getroot(), '')
        except xml.etree.ElementTree.ParseError as e:
            logging.debug("Exception parsing expected file: " + expected_file + " exception: " + str(e))
        
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
    if ALWAYS_GENERATE_EXPECTED:
        #This is off by default since it can make tests pass when they should really fail. Might be a good command line option though.
        actual_file, actual_diff_file, setup, expected_files, next_path = get_test_file_paths(test_file_root, base_test_file, test_config.expected_dir, test_config.output_dir)
        logging.debug("Copying actual [{}] to expected [{}]".format(actual_file, next_path))
        try_move(actual_file, next_path)
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

def get_tuple_display_limit():
    return 100

def get_csv_row_data(tds_name, test_name, test_path, test_result, test_case_index=0):
    #A few of the tests generate thousands of tuples. Limit how many to include in the csv since it makes it unweildly.
    passed = False
    matched_expected=None
    diff_count=None
    test_case_name=None
    error_msg = None
    error_type = None
    time=None
    expected_time = None
    generated_sql=None
    expected_sql = None
    actual_tuples=None
    expected_tuples=None
    suite = test_result.test_config.suite_name if test_result else ''
    test_set_name = test_result.test_config.config_file if test_result else ''
    cmd_output = test_result.cmd_output if test_result else ''
    test_type = 'unknown'
    if test_result and test_result.test_config:
        test_type = 'logical' if test_result.test_config.logical else 'expression'

    if not test_result or not test_result.get_test_case_count() or not test_result.get_test_case(test_case_index):
        error_msg= test_result.get_failure_message() if test_result else None
        error_type= test_result.get_failure_message() if test_result else None
        columns = [suite, test_set_name, tds_name, test_name, test_path, passed, matched_expected, diff_count, test_case_name, test_type, cmd_output, error_msg, error_type, time, generated_sql, actual_tuples, expected_tuples]
        if test_result.test_config.tested_sql:
            columns.extend([expected_sql, expected_time])
        return columns

    case = test_result.get_test_case(test_case_index)
    matched_expected = test_result.matched_expected_version
    diff_count = case.diff_count
    passed = False
    if case.all_passed():
        passed = True
    generated_sql = case.get_sql_text()
    test_case_name = case.name

    actual_tuples = "\n".join(case.get_tuples()[0:get_tuple_display_limit()])
    if not test_result.best_matching_expected_results:
        expected_tuples = ''
        expected_sql = ''
    else:
        expected_case = test_result.best_matching_expected_results.get_test_case(test_case_index)
        expected_tuples = expected_case.get_tuples() if expected_case else ""
        expected_tuples = "\n".join(expected_tuples[0:get_tuple_display_limit()])
        expected_sql = expected_case.get_sql_text() if expected_case else ""
        expected_time = expected_case.execution_time if expected_case else ""

    if not passed:
        error_msg = case.get_error_message() if case and case.get_error_message() else test_result.get_failure_message()
        error_msg = test_result.overall_error_message if test_result.overall_error_message else error_msg
        error_type = case.error_type if case else None

    columns = [suite, test_set_name, tds_name, test_name, test_path, str(passed), str(matched_expected), str(diff_count), test_case_name, test_type, cmd_output, str(error_msg), str(case.error_type), float(case.execution_time), generated_sql, actual_tuples, expected_tuples]
    if test_result.test_config.tested_sql:
        columns.extend([expected_sql, float(expected_time)])
    return columns

def write_csv_test_output(all_test_results, tds_file, skip_header, output_dir):
    csv_file_path = os.path.join(output_dir, 'test_results.csv')
    try:
        file_out = open(csv_file_path, 'w', encoding='utf8')
    except IOError:
        logging.debug("Could not open output file [{0}].".format(csv_file_path))
        return
   
    custom_dialect = csv.excel
    custom_dialect.lineterminator = '\n'
    custom_dialect.delimiter = ','
    custom_dialect.strict = True
    custom_dialect.skipinitialspace = True
    csv_out = csv.writer(file_out, dialect=custom_dialect, quoting=csv.QUOTE_MINIMAL)
    tupleLimitStr = '(' + str(get_tuple_display_limit()) + ')tuples'
    actualTuplesHeader = 'Actual ' + tupleLimitStr
    expectedTuplesHeader = 'Expected ' + tupleLimitStr
    #Suite is the datasource name (ie mydb).
    #Test Set is the grouping that defines related tests. run tdvt --list mydb to see them.
    csvheader = ['Suite','Test Set','TDSName','TestName','TestPath','Passed','Closest Expected','Diff count','Test Case','Test Type','Process Output','Error Msg','Error Type','Query Time (ms)','Generated SQL', actualTuplesHeader, expectedTuplesHeader]
    results_values = list(all_test_results.values())
    if results_values and results_values[0].test_config.tested_sql:
        csvheader.extend(['Expected SQL', 'Expected Query Time (ms)']) 
    if not skip_header:
        csv_out.writerow(csvheader)

    tdsname = os.path.splitext(os.path.split(tds_file)[1])[0]
    #Write the csv file.
    total_failed_tests = 0
    for path, test_result in all_test_results.items():
        generated_sql = ''
        test_name = test_result.get_name() if test_result.get_name() else path
        if not test_result or not test_result.get_test_case_count():
            csv_out.writerow(get_csv_row_data(tdsname, test_name, path, test_result))
            total_failed_tests += 1
        else:
            test_case_index = 0
            total_failed_tests += test_result.get_failure_count()
            for case_index in range(0, test_result.get_test_case_count()):
                csv_out.writerow(get_csv_row_data(tdsname, test_name, path, test_result, case_index))

    file_out.close()

    return total_failed_tests

def process_test_results(all_test_results, tds_file, skip_header, output_dir):
    if not all_test_results:
        return
    #Required for tube compatability.
    write_standard_test_output(all_test_results, output_dir)
    failed_test_count = write_csv_test_output(all_test_results, tds_file, skip_header, output_dir)
    return failed_test_count

def run_tests_parallel_list(test_data, thread_count):
    all_test_results = {}
    test_queue = queue.Queue()
    all_work = []

    #Create the worker threads.
    logging.debug("Running " + str(thread_count) + " worker threads.")
    for i in range(0, thread_count):
        thread_name = "tdvt_core_thread-" + str(i)
        worker = threading.Thread(target=do_test_queue_work, args=(i, test_queue), name=thread_name)
        worker.setDaemon(True)
        worker.start()

    #Build the queue of work.
    for tds, test_file, test_config in test_data:
        #for test_file in test_files:
        work = QueueWork(copy.deepcopy(test_config), test_file)
        test_queue.put(work)
        all_work.append(work)

    #Do the work.
    test_queue.join()
    
    #Analyze the results of the work.
    for work in all_work:
        all_test_results.update(work.results)

    return all_test_results

def run_tests_parallel(test_files, test_config):
    all_test_results = {}
    tds_file = test_config.tds
    test_queue = queue.Queue()
    all_work = []

    test_data = []
    for test_file in test_files:
        test_data.append([tds_file, test_file, test_config])

    return run_tests_parallel_list(test_data, test_config.thread_count)

def generate_test_file_list_from_config(root_directory, test_config_set):
    """Read the config file and generate a list of tests."""
    allowed_tests = []
    exclude_tests = test_config_set.get_exclusions()
    exclude_tests.append('expected.')
    exclude_tests.append('actual.')

    #Allowed/exclude can be filenames or directory fragments.
    tests_to_run = []
    added_test = len(tests_to_run)
    allowed_path = ''

    #Check local dir first then the root package directory.
    test_dirs = (root_directory, get_local_test_dir())
    checked_paths = []
    for test_dir in test_dirs:
        allowed_path = os.path.join(test_dir, test_config_set.allow_pattern)
        checked_paths.append(allowed_path)
        if os.path.isfile(allowed_path):
            logging.debug("Adding file " + allowed_path)
            tests_to_run.append(TestFile(test_dir, allowed_path))
        elif os.path.isdir(allowed_path):
            logging.debug("Iterating directory " + allowed_path)
            for f in os.listdir(allowed_path):
                full_filename = os.path.join(allowed_path, f)
                if os.path.isfile(full_filename):
                    logging.debug("Adding file " + full_filename)
                    tests_to_run.append(TestFile(test_dir, full_filename))
        else:
            for f in glob.glob(allowed_path):
                full_filename = os.path.join(allowed_path, f)
                if os.path.isfile(full_filename):
                    logging.debug("Adding globbed file " + full_filename)
                    tests_to_run.append(TestFile(test_dir, full_filename))
        if tests_to_run:
            break

    if added_test == len(tests_to_run):
        logging.debug("Could not find any tests for [" + "] or [".join(checked_paths)  + "]. Check the path.")

    logging.debug("Found " + str(len(tests_to_run)) + " tests to run before exclusions.")

    final_test_list = list(tests_to_run)
    for test in tests_to_run:
        for ex in exclude_tests:
            try:
                regex = re.compile(ex)
                if re.search(regex, test.test_path) and test in final_test_list:
                    logging.debug("Removing test that matched: " + ex)
                    final_test_list.remove(test)
            except:
                print ("Error compiling regular expression for test file exclusions.")

    return sorted(final_test_list, key = lambda x: x.test_path)

def generate_test_file_list(root_directory, test_set, expected_sub_dir):
    """Take the config and expand it into the list of tests cases to run. These are fully qualified paths to test files.
       Return the sorted list of tests.

    """
    final_test_list = generate_test_file_list_from_config(root_directory, test_set)

    logging.debug("Found final list of " + str(len(final_test_list)) + " tests to run.")
    if len(final_test_list) == 0:
        logging.warn("Did not find any tests to run.")
        print("Did not find any tests to run.")
        return final_test_list

    for x in final_test_list:
        logging.debug("final test path " + x.test_path)

    create_expected_directories(test_set, expected_sub_dir, final_test_list)
    return final_test_list

def generate_files(ds_registry, force=False):
    """Generate the config files and logical query test permutations."""
    logical_input = get_path('logicaltests/generate/input/')
    logical_output = get_path('logicaltests/setup')
    logging.debug("Checking generated logical setup files...")
    generate_logical_files(logical_input, logical_output, ds_registry, force)

    root_directory = get_local_logical_test_dir()
    if os.path.isdir(root_directory):
        logical_input = os.path.join(root_directory, 'generate/input/')
        logical_output = os.path.join(root_directory, 'setup/')
        logging.debug("Checking generated logical setup files...")
        generate_logical_files(logical_input, logical_output, ds_registry, force)
    return 0

def run_diff(test_config, diff):
    root_directory = get_root_dir()
    allowed_test_path = os.path.join(root_directory, diff)
    test_path_base = os.path.split(allowed_test_path)[0]
    test_name = os.path.split(allowed_test_path)[1]

    actual, actual_diff, setup, expected_files, next_path = get_test_file_paths(test_path_base, test_name, test_config.expected_dir, test_config.output_dir)

    logging.debug('actual_path: ' + actual)
    diff_count_map = {}

    for f in expected_files:
        logging.debug('expected_path: ' + f)
        if os.path.isfile(f) and os.path.isfile(actual):
            logging.debug("Diffing " + actual + " and " + f)
            actual_xml = None
            expected_xml = None
            try:
                actual_xml = xml.etree.ElementTree.parse(actual).getroot()
            except xml.etree.ElementTree.ParseError as e:
                logging.debug("Exception parsing actual file: " + actual + " exception: " + str(e))
                continue
            try:
                expected_xml = xml.etree.ElementTree.parse(f).getroot()
            except xml.etree.ElementTree.ParseError as e:
                logging.debug("Exception parsing expected file: " + f + " exception: " + str(e))
                continue

            result = TestResult(test_config=test_config)
            result.add_test_results(actual_xml, actual)
            expected_output = TestResult(test_config=test_config)
            expected_output.add_test_results(expected_xml, '')
            num_diffs, diff_string = diff_test_results(result, expected_output)
            logging.debug(diff_string)
            diff_count_map[f] = sum(num_diffs)

    for t in diff_count_map:
        logging.debug(t + ' Number of differences: ' + str(diff_count_map[t]))
    return 0

def create_expected_directories(test_set, expected_sub_dir, final_test_list):
    #Make sure the expected output directories exist.
    if expected_sub_dir:
        dir_list = set([os.path.dirname(x.test_path) for x in final_test_list])
        if test_set.is_logical:
            dir_list = set()
            for x in final_test_list:
                t1, t2, t3, t4, expected_dir = get_logical_test_file_paths(x.test_path, expected_sub_dir)
                dir_list.add(expected_dir)
        for d in dir_list:
            d = os.path.join(d, expected_sub_dir)
            if not os.path.isdir(d):
                logging.debug("Making dir: {}".format(d))
                os.makedirs(d)

def run_failed_tests_impl(run_file, root_directory, sub_threads):
    """Run the failed tests from the json output file."""
    logging.debug("Running failed tests from : " + run_file)
    tests = {}
    try:
        tests = json.load(open(run_file, 'r', encoding='utf8'))
    except:
        logging.debug("Error opening " + run_file)
        return

    all_test_pairs = []
    failed_tests = tests['failed_tests']
    for f in failed_tests:
        test_file_path = f['test_file']
        test_root_dir = root_directory
        if os.path.isfile(os.path.join(get_local_test_dir(), test_file_path)):
            test_file_path = os.path.join(get_local_test_dir(), test_file_path)
            test_root_dir = get_local_test_dir()
        if os.path.isfile(os.path.join(root_directory, test_file_path)):
            test_file_path = os.path.join(root_directory, test_file_path)

        tds = f['tds']
        tds = get_tds_full_path(root_directory, os.path.split(tds)[1])
        logging.debug("Found failed test: " + test_file_path + " and tds " + tds)
        tt = f['test_type']
        test_config = TdvtTestConfig(from_json=f['test_config'], tds=tds)
        if tt in (EXPR_CONFIG_ARG, EXPR_CONFIG_ARG_SHORT):
            test_config.logical = False
        elif tt in (LOGICAL_CONFIG_ARG, LOGICAL_CONFIG_ARG_SHORT):
            test_config.logical = True

        all_test_pairs.append([tds, TestFile(test_root_dir, test_file_path), test_config])


    all_test_results = {}
    results = run_tests_parallel_list(all_test_pairs, sub_threads)
    all_test_results.update(results)

    return all_test_results

def run_failed_tests(run_file, output_dir, sub_threads):
    """Run the failed tests from the json output file."""
    #See if we need to generate test setup files.
    root_directory = get_root_dir()
    all_test_results = run_failed_tests_impl(run_file, root_directory, sub_threads)
    return process_test_results(all_test_results, '', False, output_dir)

def run_tests(tdvt_test_config, test_set):
    #See if we need to generate test setup files.
    root_directory = get_root_dir()
    output_dir = tdvt_test_config.output_dir if tdvt_test_config.output_dir else root_directory

    tds_file = get_tds_full_path(root_directory, tdvt_test_config.tds)
    tdvt_test_config.tds = tds_file
    all_test_results = {}

    all_test_results = run_tests_parallel(generate_test_file_list(root_directory, test_set, tdvt_test_config.expected_dir), tdvt_test_config)
    return process_test_results(all_test_results, tds_file, tdvt_test_config.noheader, output_dir)

