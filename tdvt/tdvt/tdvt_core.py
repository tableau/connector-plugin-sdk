"""
    Tableau Datasource Verification Tool
    Run logical queries and expression tests against datasources.

"""

import argparse
import copy
import csv
import glob
import json
import logging
import os
import shutil
import subprocess
import sys
import time
import zipfile

from defusedxml.ElementTree import parse, ParseError
from typing import Dict, Optional, Tuple

from .config_gen.genconfig import generate_config_files
from .config_gen.gentests import generate_logical_files
from .config_gen.test_config import TestSet
from .resources import *
from .tabquery import build_connectors_test_tabquery_command_line
from .tabquery import build_tabquery_command_line
from .test_results import *

ALWAYS_GENERATE_EXPECTED = False


class ConnectorsTest(object):
    def __init__(self, conn_test_name, conn_test_file, conn_test_password_file):
        self.conn_test_name = conn_test_name
        self.conn_test_file = conn_test_file
        self.conn_test_password_file = conn_test_password_file
        self.timeout_seconds = 10

    def run_connectors_test(self):
        cmdline = build_connectors_test_tabquery_command_line(self.conn_test_name, self.conn_test_file, self.conn_test_password_file)
        self.cmd_output = str(subprocess.check_output(cmdline, stderr=subprocess.STDOUT, universal_newlines=True,
                                                      timeout=self.timeout_seconds))
        print(self.cmd_output)
        sys.exit(0)


class TestResultWork(object):
    def __init__(self, test_file, output_dir, logical):
        self.relative_test_file = test_file.relative_test_path
        self.output_dir = output_dir
        self.logical = logical
        self.set_base_test_names(test_file.test_path)

    def set_base_test_names(self, test_file):
        self.test_name = get_base_test(test_file)
        self.test_file = test_file
        if self.logical:
            existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(
                self.test_file, self.output_dir)
            # Make sure to set the generic (ie non-templatized) test name.
            self.test_name = base_test_name


class BatchQueueWork(object):
    def __init__(self, test_config, test_set: TestSet):
        self.test_config = test_config
        self.test_set: TestSet = test_set
        self.results = {}
        self.thread_id = -1
        self.timeout_seconds = test_config.timeout_seconds
        self.cmd_output = None
        self.saved_error_message = None
        self.log_zip_file = ''
        self.verbose = test_config.verbose
        self.test_name = self.test_set.config_name
        self.setup_logs_and_tests()
        self.error_state = None
        self.metadata_map = {}

    def get_thread_msg(self):
        return "Thread-[{0}] ".format(self.thread_id)

    def setup_logs_and_tests(self):
        log_dir = self.test_name.replace('.', '_')
        log_dir = self.test_name.replace('*', '_')
        self.test_config.log_dir = os.path.join(self.test_config.output_dir, log_dir)
        self.test_list_path = os.path.join(self.test_config.log_dir, 'tests.txt')

    def load_test_metadata(self):
        metadata_file_path = os.path.join(get_metadata_dir(), 'test_metadata.csv')
        try:
            with open(metadata_file_path, 'r') as metadata_file:
                reader = csv.DictReader(metadata_file, delimiter='\t')
                for row in reader:
                    test = row['Test Name Categorized']
                    if test not in self.metadata_map:
                        self.metadata_map[test] = TestMetadata(row['Priority'])
                    entry = self.metadata_map[test]
                    entry.add_function(row['Function Categorized'])
                    entry.add_category(row['Test Category'])
        except IOError as e:
            logging.debug("Error loading test metadata: " + str(e))

    def add_test_result(self, test_file, result):
        self.results[test_file] = result

    def add_test_result_error(self, test_file, result, is_first=True):
        if self.saved_error_message:
            result.saved_error_message = self.saved_error_message
            # Remove the saved error message so it only shows up once. Tests are run in batch and you can't
            # tell which test this error really corresponds to (ie timeout, or no driver or something) so
            # just associate it with the first failure.
            if not is_first:
                result.saved_error_message = "Error. Previous error message is: " + self.saved_error_message
        self.add_test_result(test_file, result)

    def create_test_result(self, test_result_file, test_category):
        result = TestResult(test_result_file.test_name, self.test_config, test_result_file.test_file,
                          test_result_file.relative_test_file, self.test_set, test_category, TestMetadata('Unknown'))
        test_name = result.get_name()
        if test_name in self.metadata_map:
            result.test_metadata = self.metadata_map[test_name]
        return result

    def add_timeout_test_failure(self, test_result_file):
        result = self.create_test_result(test_result_file, TestErrorTimeout())
        self.add_test_result_error(test_result_file.test_file, result)
        self.timeout = True

    def add_aborted_test_failure(self, test_result_file):
        result = self.create_test_result(test_result_file, TestErrorAbort())
        self.add_test_result_error(test_result_file.test_file, result)

    def add_other_test_failure(self, test_result_file, test_count):
        result = self.create_test_result(test_result_file, TestErrorOther())
        self.add_test_result_error(test_result_file.test_file, result, test_count == 0)

    def add_expected_test_failure(self, test_result_file):
        result = self.create_test_result(test_result_file, TestErrorExpected())
        self.add_test_result_error(test_result_file.test_file, result)

    def add_missing_test_failure(self, test_result_file):
        result = self.create_test_result(test_result_file, TestErrorMissingActual())
        self.add_test_result_error(test_result_file.test_file, result, False)

    def handle_skipped_test_failure(self, test_result_file):
        result = self.create_test_result(test_result_file, TestErrorSkippedTest())
        self.add_test_result_error(test_result_file.test_file, result, False)

    def handle_disabled_test_failure(self, test_result_file):
        result = self.create_test_result(test_result_file, TestErrorDisabledTest())
        self.add_test_result_error(test_result_file.test_file, result, False)

    def is_timeout(self):
        return isinstance(self.error_state, TestErrorTimeout)

    def is_error(self):
        return isinstance(self.error_state, TestErrorState)

    def is_expected_error(self):
        return isinstance(self.error_state, TestErrorExpected)

    def is_aborted(self):
        return isinstance(self.error_state, TestErrorAbort)

    def is_skipped(self):
        return isinstance(self.error_state, TestErrorSkippedTest)

    def is_disabled(self):
        return isinstance(self.error_state, TestErrorDisabledTest)

    def process_test_results(self, test_list):
        # Check the output files.
        test_count = -1
        for f in test_list:
            test_count += 1
            t = TestResultWork(f, self.test_config.output_dir, self.test_config.logical)

            actual_filepath = t.test_file
            base_test_filepath = t.test_file
            existing_output_filepath = self.test_set.get_expected_output_file_path(t.test_file, self.test_config.output_dir)

            # First check for systemic errors and set all the test results to that error.
            if not os.path.isfile(existing_output_filepath):
                if self.is_timeout():
                    self.add_timeout_test_failure(t)
                    sys.stdout.write('T')
                    continue
                elif self.is_aborted():
                    self.add_aborted_test_failure(t)
                    sys.stdout.write('A')
                    continue
                elif self.is_expected_error():
                    self.add_expected_test_failure(t)
                    sys.stdout.write('.')
                    continue
                elif self.is_skipped():
                    self.handle_skipped_test_failure(t)
                    sys.stdout.write('S')
                    continue
                elif self.is_disabled():
                    self.handle_disabled_test_failure(t)
                    sys.stdout.write('D')
                    continue
                elif self.is_error():
                    self.add_other_test_failure(t, test_count)
                    sys.stdout.write('E')
                    continue
                else:
                    logging.debug(self.get_thread_msg() + "Error: could not find test output file:" + existing_output_filepath)
                    sys.stdout.write('?')
                    self.add_missing_test_failure(t)
                    continue

            if self.test_config.logical:
                # Copy the test process filename to the actual. filename.
                actual_output_filepath, base_filepath = self.test_set.get_actual_and_base_file_path(t.test_file,
                                                                                                    self.test_config.output_dir)
                logging.debug(self.get_thread_msg() + "Copying test process output {0} to actual file {1}".format(
                    existing_output_filepath, actual_output_filepath))
                try_move(existing_output_filepath, actual_output_filepath)
                base_test_filepath = base_filepath
                actual_filepath = actual_output_filepath


            result = compare_results(t.test_name, base_test_filepath, t.test_file, self)
            result.relative_test_file = t.relative_test_file
            result.cmd_output = self.cmd_output

            sys.stdout.write('.' if result.all_passed() else 'F')
            sys.stdout.flush()

            if result.get_name() in self.metadata_map:
                result.test_metadata = self.metadata_map[result.get_name()]
            self.add_test_result(t.test_file, result)

    def setup_files(self, test_list):
        # Setup a subdirectory for the log files.
        self.test_config.log_dir = os.path.join(self.test_config.output_dir, self.test_name.replace('.', '_'))
        os.makedirs(self.test_config.log_dir)
        # Write the file that contains the tests to run.
        self.test_list_path = os.path.join(self.test_config.log_dir, 'tests.txt')
        with open(self.test_list_path, 'w') as test_list_file:
            for t in test_list:
                test_list_file.write(str(t) + "\n")
        self.load_test_metadata()

    def run_process(self, cmdline):
        self.cmd_output = str(subprocess.check_output(cmdline, stderr=subprocess.STDOUT, universal_newlines=True,
                                                      timeout=self.timeout_seconds))
    def run(self, test_list):

        if self.test_set.test_is_enabled is False:
            return 0
        if self.test_set.test_is_skipped is True:
            return 0

        try:
            self.setup_files(test_list)
        except IOError as e:
            logging.debug(self.get_thread_msg() + "Output dir IOError " + str(e))
            return 0

        cmdline = build_tabquery_command_line(self)
        logging.debug(self.get_thread_msg() + " calling " + ' '.join(cmdline))

        start_time = time.perf_counter()
        try:
            self.run_process(cmdline)
        except subprocess.CalledProcessError as e:
            error_output = str(e.output)
            logging.debug(
                self.get_thread_msg() + "CalledProcessError: Return code: " + str(e.returncode) + " " + error_output)
            # Let processing continue so it can try and find any output file which will contain database error messages.
            # Save the error message in case there is no result file to get it from.
            self.saved_error_message = error_output
            self.cmd_output = error_output
            if self.test_set.expected_message and self.test_set.expected_message in self.saved_error_message:
                self.error_state = TestErrorExpected()
            elif e.returncode == 18:
                logging.debug(self.get_thread_msg() + "Tests aborted")
                sys.stdout.write('A')
                self.error_state = TestErrorAbort()
            else:
                self.error_state = TestErrorOther()
        except subprocess.TimeoutExpired as e:
            logging.debug(self.get_thread_msg() + "Test timed out")
            sys.stdout.write('T')
            self.error_state = TestErrorTimeout()
            self.timeout = True
        except RuntimeError as e:
            logging.debug(self.get_thread_msg() + "RuntimeError: " + str(e))
            self.saved_error_message = str(e)
            self.error_state = TestErrorOther()

        total_time_ms = (time.perf_counter() - start_time) * 1000

        logging.debug(self.get_thread_msg() + "Command line output:" + str(self.cmd_output))
        return total_time_ms


def do_work(work):
    logging.debug(work.get_thread_msg() + "Running test:" + work.test_name)
    if work.test_set.test_is_enabled is False:
        work.error_state = TestErrorDisabledTest()

    if work.test_set.test_is_skipped is True:
        work.error_state = TestErrorSkippedTest()

    final_test_list = work.test_set.generate_test_file_list()
    work.run(final_test_list)
    work.process_test_results(final_test_list)

    # If everything passed delete the log files so we don't collect a bunch of useless logs.
    passed = True
    for v in work.results:
        if work.results[v].all_passed() == False:
            passed = False
            break

    if passed and not work.verbose:
        try:
            os.remove(work.log_zip_file)
        except Exception as e:
            logging.debug(work.get_thread_msg() + "got exception deleting zipped log file: " + str(e))
            pass


def try_move(srcfile, destfile):
    move_attempt = 0
    while move_attempt < 3:
        try:
            move_attempt += 1
            shutil.move(srcfile, destfile)
            return
        except:
            time.sleep(0.05)





def save_results_diff(actual_file, diff_file, expected_file, diff_string):
    # Save a diff against the best matching file.
    logging.debug("Saving diff of actual and expected as [{}]".format(diff_file))
    try:
        f = open(diff_file, 'w')
        f.write("Diff of [{}] and [{}].\n".format(actual_file, expected_file))
        f.write(diff_string)
        f.close()
    except:
        pass


def compare_results(test_name, test_file, full_test_file, work):
    """Return a TestResult object that specifies what was tested and whether it passed.
       test_file is the full path to the test file (base test name without any logical specification).
       full_test_file is the full path to the actual test file.

    """
    test_config = work.test_config
    base_test_file = get_base_test(test_file)
    test_file_root = os.path.split(test_file)[0]
    actual_file, actual_diff_file, setup, expected_files, next_path = get_test_file_paths(test_file_root,
                                                                                          base_test_file,
                                                                                          test_config.output_dir)
    result = TestResult(test_name, test_config, full_test_file, '', work.test_set)
    # There should be an actual file at this point. eg actual.setup.math.txt.
    if not os.path.isfile(actual_file):
        logging.debug(work.get_thread_msg() + "Did not find actual file: " + actual_file)
        result.error_status = TestErrorMissingActual()
        return result

    try:
        actual_xml = parse(actual_file).getroot()
        result.add_test_results(actual_xml, actual_file)
    except ParseError as e:
        logging.debug(work.get_thread_msg() + "Exception parsing actual file: " + actual_file + " exception: " + str(e))
        result.error_status = TestErrorMissingActual()
        return result

    expected_file_version = 0
    for expected_file in expected_files:
        if not os.path.isfile(expected_file):
            logging.debug(work.get_thread_msg() + "Did not find expected file " + expected_file)
            if ALWAYS_GENERATE_EXPECTED:
                # There is an actual but no expected, copy the actual to expected and return since there is nothing to compare against.
                # This is off by default since it can make tests pass when they should really fail. Might be a good command line option though.
                logging.debug(
                    work.get_thread_msg() + "Copying actual [{}] to expected [{}]".format(actual_file, expected_file))
                try_move(actual_file, expected_file)
            result.error_status = TestErrorOther()
            return result
        # Try other possible expected files. These are numbered like 'expected.setup.math.1.txt', 'expected.setup.math.2.txt' etc.
        logging.debug(work.get_thread_msg() + " Comparing " + actual_file + " to " + expected_file)
        expected_output = TestResult(test_config=test_config)
        try:
            expected_output.add_test_results(parse(expected_file).getroot(), '')
        except ParseError as e:
            logging.debug(
                work.get_thread_msg() + "Exception parsing expected file: " + expected_file + " exception: " + str(e))

        diff_counts, diff_string = result.diff_test_results(expected_output)
        result.set_best_matching_expected_output(expected_output, expected_file, expected_file_version, diff_counts)

        if result.all_passed():
            logging.debug(work.get_thread_msg() + " Results match expected number: " + str(expected_file_version))
            result.matched_expected_version = expected_file_version
            try:
                if not work.verbose:
                    if not hasattr(work, 'keep_actual_file'):
                        os.remove(actual_file)
                    os.remove(actual_diff_file)
            except:
                pass  # Mysterious problem deleting the file. Don't worry about it. It won't impact final results.
            return result
        else:
            result.error_status = TestErrorResults()

        # Try another possible expected file.
        expected_file_version = expected_file_version + 1

    # Exhausted all expected files. The test failed.
    if ALWAYS_GENERATE_EXPECTED:
        # This is off by default since it can make tests pass when they should really fail. Might be a good command line option though.
        actual_file, actual_diff_file, setup, expected_files, next_path = get_test_file_paths(test_file_root,
                                                                                              base_test_file,
                                                                                              test_config.output_dir)
        logging.debug(work.get_thread_msg() + "Copying actual [{}] to expected [{}]".format(actual_file, next_path))
        try_move(actual_file, next_path)
    # This will re-diff the results against the best expected file to ensure the test pass indicator and diff count is correct.
    diff_count, diff_string = result.diff_test_results(result.best_matching_expected_results)
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


def write_standard_test_output(all_test_results: Dict, output_dir: str):
    """Write the standard output. """
    passed = [x for x in all_test_results.values()
              if x.all_passed() is True
              and x.test_set.test_is_enabled
              and x.test_set.test_is_skipped is False]
    failed = [x for x in all_test_results.values()
              if x.all_passed() is False]
    disabled = [x for x in all_test_results.values()
                if x.test_set.test_is_enabled is False
                and x.test_set.test_is_skipped is False]
    skipped = [x for x in all_test_results.values()
               if x.test_set.test_is_skipped
               and x.test_set.test_is_enabled]
    output = {'harness_name': 'TDVT',
              'actual_exp_paths_relative_to': 'this',
              'successful_tests': passed,
              'disabled_tests': disabled,
              'skipped_tests': skipped,
              'failed_tests': failed
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


def get_csv_row_data(tds_name, test_name, test_path, test_result: TestResult, test_case_index=0):
    # A few of the tests generate thousands of tuples. Limit how many to include in the csv since it makes it unweildly.
    passed = False
    skipped = False
    disabled = False
    matched_expected = None
    diff_count = None
    test_case_name = None
    error_msg = None # A description on why the test failed. This may or may not the query error in test output.
    error_type = None
    time = None
    expected_time = None
    generated_sql = None
    expected_sql = None
    actual_tuples = None
    expected_tuples = None
    actual_error = None # The query error in test output, which may be expected. Not to be confused with error_msg.
    expected_error = None
    suite = test_result.test_config.suite_name if test_result else ''
    test_set_name = test_result.test_config.config_file if test_result else ''
    cmd_output = test_result.cmd_output if test_result else ''
    test_type = 'unknown'
    if test_result and test_result.test_config:
        test_type = 'logical' if test_result.test_config.logical else 'expression'

    # Truncate long process outputs to keep size of csv down
    if cmd_output and len(cmd_output) > 4096:
        cmd_output = cmd_output[:4096] + "<output_truncated>"

    priority = test_result.test_metadata.get_priority() if test_result and test_result.test_metadata else 'unknown'
    categories = test_result.test_metadata.concat_categories() if test_result and test_result.test_metadata else 'unknown'
    functions = test_result.test_metadata.concat_functions() if test_result and test_result.test_metadata else 'unknown'

    if not test_result or not test_result.get_test_case_count() or not test_result.get_test_case(test_case_index):
        error_msg = test_result.get_failure_message() if test_result else None
        error_type = test_result.get_failure_message() if test_result else None
        if test_result.all_passed():
            passed = True
        columns = [suite, test_set_name, tds_name, test_name, test_path, passed, matched_expected, diff_count,
                   test_case_name, test_type, priority, categories, functions, cmd_output, error_msg, error_type,
                   time, generated_sql, actual_tuples, expected_tuples]
        if test_result.test_config.tested_sql:
            columns.extend([expected_sql, expected_time])
        if test_result.test_config.tested_error:
            columns.extend([actual_error, expected_error])
        return columns

    case = test_result.get_test_case(test_case_index)
    matched_expected = test_result.matched_expected_version
    diff_count = case.diff_count
    passed = False
    if case.all_passed():
        passed = True
    if case.is_skipped():
        skipped = True
    if case.is_disabled():
        disabled = True
    generated_sql = case.get_sql_text()
    test_case_name = case.name

    actual_tuples = "\n".join(case.get_tuples()[0:get_tuple_display_limit()])
    actual_error = case.error_message
    if test_result.best_matching_expected_results:
        expected_case = test_result.best_matching_expected_results.get_test_case(test_case_index)
        expected_tuples = expected_case.get_tuples() if expected_case else ""
        expected_tuples = "\n".join(expected_tuples[0:get_tuple_display_limit()])
        expected_sql = expected_case.get_sql_text() if expected_case else ""
        expected_time = expected_case.execution_time if expected_case else ""
        expected_error = expected_case.error_message if expected_case else ""
    else:
        expected_tuples = ''
        expected_sql = ''
        expected_error = ''


    if skipped or disabled or not passed:
        error_msg = case.get_error_message() if case and case.get_error_message() else test_result.get_failure_message()
        error_msg = test_result.saved_error_message if test_result.saved_error_message else error_msg
        error_type = test_result.get_error_type()

    columns = [suite, test_set_name, tds_name, test_name, test_path, str(passed), str(matched_expected),
               str(diff_count), test_case_name, test_type, priority, categories, functions, cmd_output,
               str(error_msg), str(error_type), float(case.execution_time), generated_sql, actual_tuples,
               expected_tuples]
    if test_result.test_config.tested_sql:
        columns.extend([expected_sql, float(expected_time)])
    if test_result.test_config.tested_error:
        columns.extend([actual_error, expected_error])
    return columns

def write_csv_test_output(all_test_results, tds_file, skip_header, output_dir) -> Optional[Tuple[int, int, int, int]]:
    csv_file_path = os.path.join(output_dir, 'test_results.csv')
    try:
        file_out = open(csv_file_path, 'w', encoding='utf8')
    except IOError:
        logging.debug("Could not open output file [{0}].".format(csv_file_path))
        return

    csv_out = csv.writer(file_out, dialect='tdvt', quoting=csv.QUOTE_MINIMAL)
    tupleLimitStr = '(' + str(get_tuple_display_limit()) + ')tuples'
    actualTuplesHeader = 'Actual ' + tupleLimitStr
    expectedTuplesHeader = 'Expected ' + tupleLimitStr
    # Suite is the datasource name (ie mydb).
    # Test Set is the grouping that defines related tests. run tdvt --list mydb to see them.
    csvheader = ['Suite', 'Test Set', 'TDSName', 'TestName', 'TestPath', 'Passed', 'Closest Expected', 'Diff count',
                 'Test Case', 'Test Type', 'Priority', 'Categories', 'Functions', 'Process Output', 'Error Msg', 'Error Type', 'Query Time (ms)',
                 'Generated SQL', actualTuplesHeader, expectedTuplesHeader]
    results_values = list(all_test_results.values())
    if results_values:
        if results_values[0].test_config.tested_sql:
            csvheader.extend(['Expected SQL', 'Expected Query Time (ms)'])
        if results_values[0].test_config.tested_error:
            csvheader.extend(['Actual Error', 'Expected Error'])
    if not skip_header:
        csv_out.writerow(csvheader)

    tdsname = os.path.splitext(os.path.split(tds_file)[1])[0]
    # Write the csv file.
    total_failed_tests = 0
    total_skipped_tests = 0
    total_disabled_tests = 0
    total_tests = 0
    for path, test_result in all_test_results.items():
        generated_sql = ''
        test_name = test_result.get_name() if test_result.get_name() else path
        if not test_result or not test_result.get_test_case_count():
            csv_out.writerow(get_csv_row_data(tdsname, test_name, path, test_result))
            if not test_result.all_passed():
                total_failed_tests += 1
            total_tests += 1
        else:
            test_case_index = 0
            total_failed_tests += test_result.get_failure_count()
            total_skipped_tests += test_result.get_skipped_count()
            total_disabled_tests += test_result.get_disabled_count()
            total_tests += test_result.get_test_case_count()
            for case_index in range(0, test_result.get_test_case_count()):
                csv_out.writerow(get_csv_row_data(tdsname, test_name, path, test_result, case_index))

    file_out.close()

    return total_failed_tests, total_skipped_tests, total_disabled_tests, total_tests


def process_test_results(all_test_results, tds_file, skip_header, output_dir):
    if not all_test_results:
        return 0, 0, 0, 0
    write_standard_test_output(all_test_results, output_dir)
    return write_csv_test_output(all_test_results, tds_file, skip_header, output_dir)


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

    actual, actual_diff, setup, expected_files, next_path = get_test_file_paths(test_path_base, test_name,
                                                                                test_config.output_dir)

    logging.debug('actual_path: ' + actual)
    diff_count_map = {}

    for f in expected_files:
        logging.debug('expected_path: ' + f)
        if os.path.isfile(f) and os.path.isfile(actual):
            logging.debug("Diffing " + actual + " and " + f)
            actual_xml = None
            expected_xml = None
            try:
                actual_xml = parse(actual).getroot()
            except ParseError as e:
                logging.debug("Exception parsing actual file: " + actual + " exception: " + str(e))
                continue
            try:
                expected_xml = parse(f).getroot()
            except ParseError as e:
                logging.debug("Exception parsing expected file: " + f + " exception: " + str(e))
                continue

            result = TestResult(test_config=test_config)
            result.add_test_results(actual_xml, actual)
            expected_output = TestResult(test_config=test_config)
            expected_output.add_test_results(expected_xml, '')
            num_diffs, diff_string = result.diff_test_results(expected_output)
            logging.debug(diff_string)
            diff_count_map[f] = sum(num_diffs)

    for t in diff_count_map:
        logging.debug(t + ' Number of differences: ' + str(diff_count_map[t]))
    return 0


def run_tests_impl(test_set: TestSet, test_config: TdvtInvocation):
    all_test_results = {}
    all_work = []

    # Build the queue of work.
    work = BatchQueueWork(copy.deepcopy(test_config), test_set)
    work.thread_id = test_config.thread_id

    # Do the work.
    do_work(work)

    # Analyze the results of the work.
    all_test_results.update(work.results)

    return all_test_results


def run_tests_serial(tests):
    all_test_results = {}

    for test_set, tdvt_test_config in tests:
        all_test_results.update(run_tests_impl(test_set, tdvt_test_config))

    return all_test_results


def run_tests(tdvt_test_config: TdvtInvocation, test_set: TestSet):
    # See if we need to generate test setup files.
    root_directory = get_root_dir()
    output_dir = tdvt_test_config.output_dir if tdvt_test_config.output_dir else root_directory

    tds_file = get_tds_full_path(root_directory, tdvt_test_config.tds)
    tdvt_test_config.tds = tds_file

    tds_file = tdvt_test_config.tds

    all_test_results = run_tests_impl(test_set, tdvt_test_config)

    return process_test_results(all_test_results, tds_file, tdvt_test_config.noheader, output_dir)

def run_connectors_test_core(conn_test_name, conn_test_file, conn_test_password_file = None):
    connectors_test = ConnectorsTest(conn_test_name, conn_test_file, conn_test_password_file)
    connectors_test.run_connectors_test()
