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
import logging
from .config_gen.genconfig import generate_config_files
from .config_gen.gentests import generate_logical_files
from .resources import *
from .test_results import *
from .tabquery import *

EXPR_CONFIG_ARG = '--expression-config'
EXPR_CONFIG_ARG_SHORT = '-e'
LOGICAL_CONFIG_ARG = '--logical-query-config'
LOGICAL_CONFIG_ARG_SHORT = '-q'
TDS_CONFIG_ARG = '--tds'
TDS_CONFIG_ARG_SHORT = '-d'
ALWAYS_GENERATE_EXPECTED = False
VERBOSE = False
abort_test_run = False


    
class QueueWork(object):
    def __init__(self, test_config, test_file):
        self.test_config = test_config
        self.test_file = test_file
        self.results = {}
        self.timeout_seconds = 1200

    def handle_test_failure(self, result=None, error_msg=None):
        if result == None:
            result = TestResult(get_base_test(work.test_file), work.test_config, work.test_file)

        if error_msg:
            result.overall_error_message = error_msg

        self.results[work.test_file] = result
           
    def handle_timeout_test_failure(self):
        result = TestResult(get_base_test(work.test_file), work.test_config, work.test_file)
        result.error_status = TestErrorTimeout()
        self.handle_test_failure(result)

    def handle_abort_test_failure(self):
        result = TestResult(get_base_test(work.test_file), work.test_config, work.test_file)
        result.error_status = TestErrorAbort()
        self.handle_test_failure(result)


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

        cmdline = build_tabquery_command_line(work)

        if abort_test_run:
            #Do this here so we have the repro information from above.
            logging.debug("\nAborting test:" + work.test_file)
            if not VERBOSE: sys.stdout.write('A')
            work.handle_abort_test_failure()
            q.task_done()
            continue

        logging.debug(" calling " + ' '.join(cmdline))

        saved_error_message = None
        cmd_output = None
        try:
            cmd_output = subprocess.check_output(cmdline, stderr=subprocess.STDOUT, universal_newlines=True, timeout=work.timeout_seconds)
        except subprocess.CalledProcessError as e:
            logging.debug("CalledProcessError for " + work.test_file + ". Error: "  + e.output)
            #Let processing continue so it can try and find any output file which will contain database error messages.
            #Save the error message in case there is no result file to get it from.
            saved_error_message = e.output
        except subprocess.TimeoutExpired as e:
            logging.debug("Test timed out: " + work.test_file)
            if not VERBOSE: sys.stdout.write('T')
            work.handle_timeout_test_failure()
            q.task_done()
            continue

        if cmd_output:
            logging.debug("Command line output for " + work.test_file + ". " + str(cmd_output))

        test_name = get_base_test(work.test_file)
        new_test_file = work.test_file
        if work.test_config.logical:
            existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(work.test_file, work.test_config.output_dir)
            if not os.path.isfile( existing_output_filepath ):
                logging.debug("Error: could not find test output file:" + existing_output_filepath)
                if not VERBOSE: sys.stdout.write('?')
                work.handle_test_failure(error_msg = saved_error_message)
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
            result.error_case = TestErrorStartup()

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

    test_case_count = len(result.test_case_map)
    diff_counts = [0] * test_case_count
    diff_string = ''
    #Go through all test cases.
    for test_case in range(0, test_case_count):
        expected_testcase_result = expected_output.test_case_map[test_case]
        actual_testcase_result = result.test_case_map[test_case]
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
    actual_file, actual_diff_file, setup, expected_files = get_test_file_paths(test_file_root, base_test_file, test_config.expected_dir, test_config.output_dir)
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
            #logging.debug("Copying actual [{}] to expected [{}]".format(actual_file, expected_file))
            #There is an actual but no expected, copy the actual to expected and return since there is nothing to compare against.
            #Commenting this out for now since it can make tests pass when they should really fail. Might be a good command line option though.
            #try_move(actual_file, expected_file)
            return result
        #Try other possible expected files. These are numbered like 'expected.setup.math.1.txt', 'expected.setup.math.2.txt' etc.
        logging.debug(threading.current_thread().name + " Comparing " + actual_file + " to " + expected_file)
        expected_output = TestResult(test_config=test_config)
        expected_output.add_test_results(xml.etree.ElementTree.parse(expected_file).getroot(), '')
        
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

def get_tuple_display_limit():
    return 100

def get_csv_row_data(tds_name, test_name, test_result, test_case_index=0):
    #A few of the tests generate thousands of tuples. Limit how many to include in the csv since it makes it unweildly.
    passed = 0
    matched_expected=None
    diff_count=None
    test_case_name=None
    error_msg = None
    error_type = None
    time=None
    generated_sql=None
    actual_tuples=None
    expected_tuples=None
    suite = test_result.test_config.suite_name if test_result else ''

    if not test_result or not test_result.test_case_map:
        error_msg= test_result.get_failure_message() if test_result else None
        error_type= test_result.get_failure_message() if test_result else None
        return [suite, tds_name, test_name, passed, matched_expected, diff_count, test_case_name, error_msg, error_type, time, generated_sql, actual_tuples, expected_tuples]

    case = test_result.test_case_map[test_case_index]
    matched_expected = test_result.matched_expected_version
    diff_count = case.diff_count
    passed = 0
    if case.all_passed():
        passed = 1
    generated_sql = case.get_sql_text()
    test_case_name = case.name

    actual_tuples = "\n".join(case.get_tuples()[0:get_tuple_display_limit()])
    if not test_result.best_matching_expected_results:
        expected_tuples = ''
    else:
        expected_tuples = "\n".join(test_result.best_matching_expected_results.test_case_map[test_case_index].get_tuples()[0:get_tuple_display_limit()])

    if passed == 0:
        error_msg = case.get_error_message() if case and case.get_error_message() else test_result.get_failure_message()
        error_type= case.error_type if case else None

    return [suite, tds_name, test_name, str(passed), str(matched_expected), str(diff_count), test_case_name, str(error_msg), str(case.error_type), float(case.execution_time), generated_sql, actual_tuples, expected_tuples]

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
    csvheader = ['Suite','TDSName','TestName','Passed','Closest Expected','Diff count','Test Case','Error Msg','Error Type','Query Time (ms)','Generated SQL', actualTuplesHeader, expectedTuplesHeader]
    if not skip_header:
        csv_out.writerow(csvheader)

    tdsname = os.path.splitext(os.path.split(tds_file)[1])[0]
    #Write the csv file.
    total_failed_tests = 0
    for path, test_result in all_test_results.items():
        generated_sql = ''
        test_name = test_result.get_name() if test_result.get_name() else path
        if not test_result or not test_result.test_case_map:
            row_data = get_csv_row_data(tdsname, test_name, test_result)
            csv_out.writerow(row_data)
            total_failed_tests += 1
        else:
            test_case_index = 0
            total_failed_tests += test_result.get_failure_count()
            for case_index in range(0, len(test_result.test_case_map)):
                csv_out.writerow(get_csv_row_data(tdsname, test_name, test_result, case_index))

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

def generate_files(ds_registry, force=False):
    """Generate the config files and logical query test permutations."""
    root_directory = get_root_dir()
    logical_input = get_path('logicaltests/generate/input/')
    logical_output = get_path('logicaltests/setup')
    logging.debug("Checking generated logical setup files...")
    generate_logical_files(logical_input, logical_output, force)
    logging.debug("Checking generated config files...")
    generate_config_files(os.path.join(root_directory, os.path.join("config", "gen")), ds_registry, force)
    return 0

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

def run_failed_tests_impl(run_file, root_directory):
    """Run the failed tests from the json output file."""
    tests = {}
    try:
        tests = json.load(open(run_file, 'r', encoding='utf8'))
    except:
        logging.debug("Error opening " + run_file)
        return

    expr_tests = {}
    log_tests = {}

    failed_tests = tests['failed_tests']
    for f in failed_tests:
        logging.debug("Found failed test: " + f['test_file'] + " and tds " + f['tds'])
        tt = f['test_type']
        tds = f['tds']
        if tt in (EXPR_CONFIG_ARG, EXPR_CONFIG_ARG_SHORT):
            if tds not in expr_tests:
                expr_tests[tds] = []
            test_config = TdvtTestConfig(from_json=f['test_config'], tds=tds)
            test_config.logical = False
            expr_tests[tds].append( [f['test_file'], test_config] )

        if tt in (LOGICAL_CONFIG_ARG, LOGICAL_CONFIG_ARG_SHORT):
            if tds not in log_tests:
                log_tests[tds] = []
            test_config = TdvtTestConfig(from_json=f['test_config'], tds=tds)
            test_config.logical = True
            log_tests[tds].append( [f['test_file'], test_config] )

    all_test_results = {}
    for tds in expr_tests:
        for test_pair in expr_tests[tds]:
            if len(test_pair) == 2:
                test_files = test_pair[0]
                test_config = test_pair[1]
                results = run_tests_parallel([test_files], test_config)
                all_test_results.update(results)
    
    for tds in log_tests:
        for test_pair in log_tests[tds]:
            if len(test_pair) == 2:
                test_files = test_pair[0]
                test_config = test_pair[1]
                results = run_tests_parallel([test_files], test_config)
                all_test_results.update(results)
    return all_test_results

def run_failed_tests(run_file, output_dir):
    """Run the failed tests from the json output file."""
    #See if we need to generate test setup files.
    root_directory = get_root_dir()
    all_test_results = run_failed_tests_impl(run_file, root_directory)
    return process_test_results(all_test_results, '', False, output_dir)

def run_tests(test_config):
    #See if we need to generate test setup files.
    root_directory = get_root_dir()
    output_dir = test_config.output_dir if test_config.output_dir else root_directory

    tds_file = get_tds_full_path(root_directory, test_config.tds)
    test_config.tds = tds_file
    all_test_results = {}

    all_test_results = run_tests_parallel(generate_test_file_list(root_directory, test_config.logical, test_config.config_file, test_config.expected_dir), test_config)
    return process_test_results(all_test_results, tds_file, test_config.noheader, output_dir)

