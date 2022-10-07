"""
    Test driver script for the Tableau Datasource Verification Tool

"""
import sys

if sys.version_info[0] < 3:
    raise EnvironmentError("TDVT requires Python 3 or greater.")

import argparse
import csv
import glob
import json
import pathlib
import os
import queue
import shutil
import threading
import time
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple, Union

from .config_gen.datasource_list import print_ds, print_configurations, print_logical_configurations
from .config_gen.tdvtconfig import TdvtInvocation
from .config_gen.test_config import TestSet, SingleLogicalTestSet, SingleExpressionTestSet, FileTestSet, TestConfig, RunTimeTestConfig
from .setup_env import create_test_environment, add_datasource
from .tabquery import *
from .tdvt_core import generate_files, run_diff, run_tests, run_connectors_test_core
from .version import __version__

# This contains the dictionary of configs you can run.
from .config_gen.datasource_list import WindowsRegistry, MacRegistry, LinuxRegistry


TDVT_LOG_FILE_NAME = 'tdvt_log_combined.txt'


class TestOutputFiles(object):
    output_actuals = 'tdvt_actuals_combined.zip'
    output_tabquery_log = 'tabquery_logs.zip'
    output_csv = "test_results_combined.csv"
    output_json = "tdvt_output_combined.json"
    all_output_files = [output_actuals, output_csv, output_json, output_tabquery_log]
    combined_output = []

    @classmethod
    def copy_output_file(c, src_name, src_dir):
        src = os.path.join(src_dir, src_name)
        logging.debug("Copying {0} to output".format(src))
        try:
            with open(src, 'r', encoding='utf8') as src_file:
                reader = csv.DictReader(src_file, dialect='tdvt')
                for row in reader:
                    c.combined_output.append(row)

        except IOError as e:
            logging.debug("Exception while copying files: " + str(e))
            return

    @classmethod
    def write_test_results_csv(c, custom_output_dir: str=''):
        if not c.combined_output:
            logging.debug("write_test_results_csv called with no test output")
            return

        logging.debug("Copying output to {0}".format(c.output_csv))
        # Sort combined_output on the number of distinct functions (order of complexity)
        sort_by_complexity = lambda row: len(row['Functions'].split(','))
        try:
            c.combined_output.sort(key=sort_by_complexity)
        except KeyError as e:
            logging.debug("Tried to sort output on a key that doesn't exist. Leaving output unsorted.")

        dst = os.path.join(os.getcwd(), c.output_csv)
        if custom_output_dir != '':
            dst = os.path.join(Path(custom_output_dir), c.output_csv)
        try:
            dst_exists = os.path.isfile(dst)
            with open(dst, 'w', encoding='utf8') as dst_file:
                writer = csv.DictWriter(dst_file, fieldnames=c.combined_output[0],
                    dialect='tdvt', quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for row in c.combined_output:
                    writer.writerow(row)
        except IOError as e:
            logging.debug("Exception while writing to file: " + str(e))
            return

def do_test_queue_work(i, q):
    """This will be called in a queue.join() context, so make sure to mark all work items as done and
    continue through the loop. Don't try and exit or return from here if there are still work items in the queue.
    See the python queue documentation."""

    abort_test_run = False
    while True:
        # This blocks if the queue is empty.
        work = q.get()

        work.run()

        q.task_done()


class TestRunner():
    def __init__(self, test_set: TestSet, test_config: TdvtInvocation, lock, verbose, thread_id):
        threading.Thread.__init__(self)
        self.test_set = test_set
        self.test_config = test_config
        self.error_code = 0
        self.thread_id = thread_id
        self.verbose = verbose
        self.thread_lock = lock
        self.temp_dir = make_temp_dir([self.test_config.suite_name, str(thread_id)])
        self.test_config.output_dir = self.temp_dir

    def copy_files_to_zip(self, dst_file_name, src_dir, is_logs):
        dst = os.path.join(os.getcwd(), dst_file_name)
        custom_dir = self.test_config.custom_output_dir
        if custom_dir != '':
            dst = os.path.join(custom_dir, dst_file_name)
        mode = 'w' if not os.path.isfile(dst) else 'a'
        optional_dir_name = self.test_config.config_file.replace('.', '_')
        if is_logs is True:
            log_dir = os.path.join(src_dir, optional_dir_name)
            glob_path = glob.glob(os.path.join(log_dir, '*.txt'))
            glob_path.extend(glob.glob(os.path.join(log_dir, '*.log')))
            glob_path.extend(glob.glob(os.path.join(log_dir, 'crashdumps/*')))
        else:
            glob_path = glob.glob(os.path.join(src_dir, 'actual.*'))
        with zipfile.ZipFile(dst, mode, zipfile.ZIP_DEFLATED) as myzip:
            for actual in glob_path:
                path = pathlib.PurePath(actual)
                file_to_be_zipped = path.name
                inner_output = os.path.join(optional_dir_name, file_to_be_zipped)
                myzip.write(actual, inner_output)

    def copy_output_files(self):
        TestOutputFiles.copy_output_file("test_results.csv", self.temp_dir)

    def copy_test_result_file(self):
        src = os.path.join(self.temp_dir, "tdvt_output.json")
        dst = os.path.join(os.getcwd(), TestOutputFiles.output_json)
        custom_dir = self.test_config.custom_output_dir
        if custom_dir != '':
            dst = os.path.join(custom_dir, TestOutputFiles.output_json)
        try:
            if not os.path.isfile(dst):
                shutil.copyfile(src, dst)
            else:
                src_file = open(src, 'r', encoding='utf8')
                results = json.load(src_file)
                src_file.close()

                dst_file = open(dst, 'r', encoding='utf8')
                existing_results = json.load(dst_file)
                dst_file.close()

                existing_results['failed_tests'].extend(results['failed_tests'])

                existing_results['successful_tests'].extend(results['successful_tests'])

                existing_results['skipped_tests'].extend(results['skipped_tests'])

                existing_results['disabled_tests'].extend(results['disabled_tests'])

                # Check the newly succeeding tests, and if they are in the existing failed
                # test list, remove them from the failed test list since they now succeed
                for element in results['successful_tests']:
                    for failed in existing_results['failed_tests']:
                        if element['test_name'] == failed['test_name']:
                            existing_results['failed_tests'].remove(failed)

                dst_file = open(dst, 'w', encoding='utf8')
                json.dump(existing_results, dst_file)
                dst_file.close()
        except IOError:
            return

    def copy_files_and_cleanup(self):
        left_temp_dir = False
        try:
            self.copy_files_to_zip(TestOutputFiles.output_actuals, self.temp_dir, is_logs=False)
            self.copy_files_to_zip(TestOutputFiles.output_tabquery_log, self.temp_dir, is_logs=True)
            self.copy_output_files()
            self.copy_test_result_file()
        except Exception as e:
            print(e)
            pass

        try:
            if not self.test_config.leave_temp_dir:
                shutil.rmtree(self.temp_dir)
            else:
                left_temp_dir = True
        except:
            pass

        return left_temp_dir

    def run(self):
        # Send output to null.
        DEVNULL = open(os.devnull, 'wb')
        output = DEVNULL if not self.verbose else None
        logging.debug("\nRunning tdvt " + str(self.test_config) + " tdvt thread id: " + str(self.thread_id) + "\n")
        print("Running {0} {1} {2}\n".format(self.test_config.suite_name, self.test_config.config_file,
                                             str(self.thread_id)))

        start_time = time.time()
        self.test_config.thread_id = self.thread_id
        failed_tests, skipped_tests, disabled_tests, total_tests = run_tests(self.test_config, self.test_set)
        logging.debug("\nFinished tdvt " + str(self.test_config) + "\n")
        print("\nFinished {0} {1} {2}\n".format(self.test_config.suite_name, self.test_config.config_file,
                                                str(self.thread_id)))

        self.failed_tests = failed_tests
        self.skipped_tests = skipped_tests
        self.disabled_tests = disabled_tests
        self.total_tests = total_tests


def delete_output_files(root_dir):
    for f in TestOutputFiles.all_output_files:
        out_file = os.path.join(root_dir, f)
        for f in glob.glob(out_file):
            if os.path.exists(out_file):
                try:
                    os.unlink(out_file)
                except Exception as e:
                    print(e)
                    continue


def get_datasource_registry(platform):
    """Get the datasources to run based on the suite parameter."""
    if sys.platform.startswith("darwin"):
        reg = MacRegistry()
    elif sys.platform.startswith("linux"):
        reg = LinuxRegistry()
    else:
        reg = WindowsRegistry()

    return reg


def enqueue_single_test(args, ds_info: TestConfig, suite) -> Union[Tuple[None, None], Tuple[Union[SingleLogicalTestSet, SingleExpressionTestSet], TdvtInvocation]]:  # noqa: E501
    if not args.command == 'run-pattern' or not args.tds_pattern or (args.logical_pattern and args.expression_pattern):
        return None, None

    test_set = None
    if args.logical_pattern:
        test_set = SingleLogicalTestSet(suite, get_root_dir(), args.logical_pattern, args.tds_pattern,
                                        args.test_pattern_exclude, ds_info)
    else:
        test_set = SingleExpressionTestSet(suite, get_root_dir(), args.expression_pattern, args.tds_pattern,
                                           args.test_pattern_exclude, ds_info)

    #Only try and run tests if there are some.
    if not test_set.generate_test_file_list():
        return None, None

    tdvt_invocation = TdvtInvocation(from_args=args, test_config=ds_info)
    tdvt_invocation.tds = test_set.tds_name
    tdvt_invocation.logical = test_set.is_logical
    tdvt_invocation.config_file = test_set.config_name

    return test_set, tdvt_invocation


def enqueue_failed_tests(run_file: Path, root_directory, args, rt: RunTimeTestConfig = None):
    try:
        with run_file.open('r', encoding='utf8') as file:
            tests = json.load(file)
    except IOError as e:
        logging.error("Error opening " + str(run_file) + " error: " + str(e))
        return

    delete_output_files(os.getcwd())
    all_test_configs = {}
    all_tdvt_test_configs = {}
    all_test_pairs = []
    failed_tests = tests['failed_tests']
    # Go through the failed tests and group the ones that can be run together in a FileTestSet.
    for f in failed_tests:
        test_file_path = f['test_file']
        expected_message = f['expected_message'] if 'expected_message' in f else ''
        test_root_dir = root_directory

        tds_base = os.path.split(f['tds'])[1]
        tds = get_tds_full_path(root_directory, tds_base)
        logging.debug("Found failed test: " + test_file_path + " and tds " + tds)
        tdvt_invocation = TdvtInvocation(from_json=f['test_config'])
        if rt:
            tdvt_invocation.set_run_time_test_config(rt)
        tdvt_invocation.tds = tds
        tdvt_invocation.leave_temp_dir = is_test(args) and args.noclean if args else False
        suite_name = f['test_config']['suite_name']
        password_file = f['password_file'] if 'password_file' in f else ''
        # Use a hash of the test file path to distinguish unique test runs (since the config only supports one test path).
        # other wise two tests with the same name could show up and the first result file would overwrite the second.
        tt = "L" if tdvt_invocation.logical else "E"
        test_set_unique_id = hashlib.sha224(
            (os.path.split(test_file_path)[0] + "_" + tds_base + "_" + tt).replace("-", "_").encode())
        test_set_unique_id = test_set_unique_id.hexdigest()
        test_set_config = None
        if not suite_name in all_test_configs:
            all_test_configs[suite_name] = {}

        if not test_set_unique_id in all_test_configs[suite_name]:
            tdvt_invocation.output_dir = make_temp_dir([test_set_unique_id])
            all_tdvt_test_configs[test_set_unique_id] = tdvt_invocation
            run_time_config = RunTimeTestConfig(60*60, 1)
            test_set_config = TestConfig(suite_name, '', run_time_config)
            all_test_configs[suite_name][test_set_unique_id] = test_set_config
        else:
            test_set_config = all_test_configs[suite_name][test_set_unique_id]

        current_test_set = None
        if tdvt_invocation.logical:
            current_test_set = test_set_config.get_logical_tests(test_set_unique_id)
        else:
            current_test_set = test_set_config.get_expression_tests(test_set_unique_id)
        if current_test_set and len(current_test_set) == 1:
            current_test_set = current_test_set[0]

        if not current_test_set:
            current_test_set = FileTestSet(suite_name, test_root_dir, test_set_unique_id, tds, tdvt_invocation.logical, suite_name,
                                           password_file, expected_message)
            if tdvt_invocation.logical:
                test_set_config.add_logical_testset(current_test_set)
            else:
                test_set_config.add_expression_testset(current_test_set)

        current_test_set.append_test_file(test_file_path)

    for suite_names in all_test_configs:
        for test_set_id in all_test_configs[suite_names]:
            test_set_config = all_test_configs[suite_names][test_set_id]
            for each_test_set in test_set_config.get_logical_tests() + test_set_config.get_expression_tests():
                tdvt_invocation = all_tdvt_test_configs[test_set_id]
                all_test_pairs.append((each_test_set, tdvt_invocation))
                logging.debug("Queuing up tests: " + str(tdvt_invocation))

    return all_test_pairs


def enqueue_tests(ds_info, args, suite):
    tests = []
    test_set_configs = []
    if not is_test(args):
        return test_set_configs

    logging.debug("Enqueing tests for " + ds_info.dsname)
    if args.logical_only or args.expression_only:
        if args.logical_only:
            tests.extend(ds_info.get_logical_tests(args.logical_only))
        if args.expression_only:
            tests.extend(ds_info.get_expression_tests(args.expression_only))

    else:
        tests.extend(ds_info.get_logical_tests(args.logical_only))
        tests.extend(ds_info.get_expression_tests(args.expression_only))

    # Make sure there are tests.
    if not tests:
        logging.error("No tests found")
        return test_set_configs

    for x in tests:
        if not x.generate_test_file_list():
            logging.error("No tests found for config " + str(x))
            return test_set_configs

    for test_set in tests:
        tdvt_invocation = TdvtInvocation(from_args=args, test_config = ds_info)
        tdvt_invocation.logical = test_set.is_logical_test()
        tdvt_invocation.tds = test_set.tds_name
        tdvt_invocation.config_file = test_set.config_name

        test_set_configs.append((test_set, tdvt_invocation))

    return test_set_configs


def get_level_of_parallelization(args):
    # This indicates how many database/test suite combinations to run at once
    max_threads = 6

    if is_test(args) and args.thread_count:
        max_threads = args.thread_count

    max_threads = get_max_process_level_of_parallelization(max_threads)

    print("Setting tdvt thread count to: " + str(max_threads))
    return max_threads

list_usage_text = '''
    Show all test suites or list the contents of a specific suite.
'''

list_logical_usage_text = '''
    Show logical configs. The argument can be empty to list all, or you can specify a config by name.
'''

run_usage_text = '''
    The 'run' argument can take a single datasource, a list of data sources, or a test suite name in any combination.
        run postgres_odbc,postgres_jdbc

    The 'run' argument can also take the --verify flag to run a connection test against tests with SmokeTest = True set.
        run postgres_odbc --verify

    Both logical and expression tests are run by default.
    Run all expression tests
       run postgres_odbc -e

    Run all logical tests
        run postgres_odbc -q

    There are multiple suites of expression tests, for example, standard and LOD (level of detail). The config files that drive the tests
    are named expression_test.sqlserver.cfg and expression.lod.sqlserver.cfg.
    To run just one of those try entering part of the config name as an argument:
        run postgres_odbc -e lod

'''

run_pattern_usage_text = '''
    Run one expression test against many datasources
        run-pattern postgres_odbc --exp exprtests/standard/setup.date.datepart.second*.txt --tdp cast_calcs.*.tds

    Run one logical query test against many datasources
        run-pattern postgres_odbc --logp logicaltests/setup/calcs/setup.BUGS.B1713.?.xml --tdp cast_calcs.*.tds

    The 'exp' argument is a glob pattern that is used to find the test file using the relative test path.
    The 'test-ex' argument can be used to exclude test files. This is a regular expression pattern.
    The tds pattern is used to find the tds. Use a '*' character where the tds name will be substituted,
    ie cast_calcs.*.tds

    This can be combined with * to run an arbitrary set of 'correct' logical query tests against a datasources
        run-pattern postgres_odbc --logp logicaltests/setup/calcs/setup.BUGS.*.?.xml --tdp cast_calcs.*.tds
    Alternatively
        run-pattern postgres_odbc --logp logicaltests/setup/calcs/setup.BUGS.*.dbo.xml --tdp cast_calcs.*.tds

    But skip 59740?
        run-pattern postgres_odbc --logp logicaltests/setup/calcs/setup.BUGS.*.dbo.xml --tdp cast_calcs.*.tds --test-ex 59740

    '''
run_connectors_test_usage_text = '''
    The commands below can be used to run the connectors tests.
    'filename.xml' in the below commands is the path of the xml test file used to run the tests.
    'passwordfilepath.password' in the below commands is the path of the password file used for the ServerVersionTest.

    Run ConnectionBuilderTest
        run-connectors-test --conn-test connectionBuilder --conn-test-file filepath.xml
    Run NormalizeConnectionAttributes Test
        run-connectors-test --conn-test normalizeConnectionAttributes --conn-test-file filepath.xml
    Run MatchesConnectionAttributesTest
         run-connectors-test --conn-test matchesConnectionAttributes --conn-test-file filepath.xml
    Run PropertiesBuilderTest
        run-connectors-test --conn-test propertiesBuilder --conn-test-file filepath.xml
    Run ServerVersionTest
        run-connectors-test --conn-test serverVersion --conn-test-file filepath.xml --conn-test-password-file passwordfilepath.password

'''

action_usage_text = '''
'''
run_file_usage_text = '''
'''

def create_parser():
    parser = argparse.ArgumentParser(description='TDVT - Tableau Datasource Verification Tool.')
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Verbose output.', required=False)

    #Common run test options.
    run_test_common_parser = argparse.ArgumentParser(description='Common test run options.', add_help=False)

    run_test_common_parser.add_argument('--threads', '-t', dest='thread_count', type=int, help='Max number of threads to use.', required=False)
    run_test_common_parser.add_argument('--no-clean', dest='noclean', action='store_true', help='Leave temp dirs.', required=False)
    run_test_common_parser.add_argument('--generate', dest='generate', action='store_true', help='Generate logical query test files.', required=False)
    run_test_common_parser.add_argument('--compare-sql', dest='compare_sql', action='store_true', help='Compare SQL.', required=False)
    run_test_common_parser.add_argument('--nocompare-tuples', dest='nocompare_tuples', action='store_true', help='Do not compare Tuples.', required=False)
    run_test_common_parser.add_argument('--compare-error', dest='compare_error', action='store_true', help='Compare error.', required=False)
    run_test_common_parser.add_argument('--output-dir', '-o', dest='custom_output_dir',
                                        help='Writes log files to a specified directory. The directory must exist.',
                                        required=False, default=None, const='*', nargs='?')
    subparsers = parser.add_subparsers(help='commands', dest='command')

    #Get information.
    list_parser = subparsers.add_parser('list', help='List information about datasource tests and suites.', usage=list_usage_text)
    list_parser.add_argument(dest='list_ds', help='List datasource config.', default='', nargs='?')

    list_logical_parser = subparsers.add_parser('list-logical-configs', help='List information about logical configurations.', usage=list_logical_usage_text)
    list_logical_parser.add_argument(dest='list_logical_configs', help='List available logical configs.', default='', nargs='?')

    #Actions.
    action_group = subparsers.add_parser('action', help='Various non-test actions.', usage=action_usage_text)
    action_group.add_argument('--setup', dest='setup', action='store_true', help='Create setup directory structure.', required=False)
    action_group.add_argument('--add_ds', dest='add_ds', help='Add a new datasource.', required=False)
    action_group.add_argument('--diff-test', '-dd', dest='diff', help='Diff the results of the given test (ie exprtests/standard/setup.calcs_data.txt) against the expected files. Can be used with the sql and tuple options.', required=False)
    action_group.add_argument('--generate', dest='action_generate', action='store_true', help='Generate logical query test files.', required=False)

    #Run tests.
    run_test_parser = subparsers.add_parser('run', help='Run tests.', parents=[run_test_common_parser], usage=run_usage_text)
    run_test_parser.add_argument('ds', help='Comma separated list of Datasource names or groups to test. See the \'list\' command.', nargs='+')
    run_test_parser.add_argument('--verify', dest='smoke_test', action='store_true', help='Verifies the connection to a data source against tests in your .ini file with SmokeTest = True.', required=False)  # noqa: E501
    run_test_parser.add_argument('--force-run', dest='force_run', action='store_true', help='Attempts to run the tests for a data source, even if its smoke tests fail.')
    run_test_parser.add_argument('--logical', '-q', dest='logical_only', help='Only run logical tests whose config file name matches the supplied string, or all if blank.', required=False, default=None, const='*', nargs='?')
    run_test_parser.add_argument('--expression', '-e', dest='expression_only', help='Only run expression tests whose config file name matches the suppled string, or all if blank.', required=False, default=None, const='*', nargs='?')


    #Run test pattern.
    run_test_pattern_parser = subparsers.add_parser('run-pattern', help='Run individual tests using a pattern.', parents=[run_test_common_parser], usage=run_pattern_usage_text)
    run_test_pattern_parser.add_argument('ds', help='Comma separated list of Datasource names or groups to test. See the \'list\' command.', nargs='+')
    run_test_group = run_test_pattern_parser.add_mutually_exclusive_group(required=True)

    run_test_group.add_argument('--exp', dest='expression_pattern', help='Only run expression tests whose name and path matches the supplied string. This is a glob pattern. Also you must set the tds-pattern to use when running the test.', required=False, default=None, const='', nargs='?')
    run_test_group.add_argument('--logp', dest='logical_pattern', help='Only run logical tests whose name and path matches the supplied string. this is a glob pattern. Also you must set the tds-pattern to use when running the test. Use a ? to replace the logical query config component of the test name.', required=False, default=None, const='', nargs='?')

    run_test_pattern_parser.add_argument('--tdp', dest='tds_pattern', help='The datasource tds pattern to use when running the test. See exp and logp arguments.', required=True, default=None, const='', nargs='?')
    run_test_pattern_parser.add_argument('--test-ex', dest='test_pattern_exclude', help='Exclude tests whose name matches the supplied string. This is a regular expression pattern. Can be used with exp and logp arguments. Also set the tds-pattern to use when running the test.', required=False, default=None, const='', nargs='?')

    #Run file.
    run_file_parser = subparsers.add_parser('run-file', help='Run tests from a file.', parents=[run_test_common_parser], usage=run_file_usage_text)
    run_file_parser.add_argument('run_file', help='Json file containing failed tests to run.')

    #Run Connectors Test
    run_connectors_test_parser = subparsers.add_parser('run-connectors-test', help='Run a connectors test using a file', parents=[run_test_common_parser], usage=run_connectors_test_usage_text)
    run_connectors_test_parser.add_argument('--conn-test', dest='conn_test', help='Name of the Connectors Test to run.',  required=True)
    run_connectors_test_parser.add_argument('--conn-test-file', dest='conn_test_file', help='Path to the setup-expected file to run the connectors test',  required=True)
    run_connectors_test_parser.add_argument('--conn-test-password-file', dest='conn_test_password_file', help='Path to the password file used for the ServerVersionTest')

    return parser


def register_tdvt_dialect():
    custom_dialect = csv.excel
    custom_dialect.lineterminator = '\n'
    custom_dialect.delimiter = ','
    custom_dialect.strict = True
    custom_dialect.skipinitialspace = True
    csv.register_dialect('tdvt', custom_dialect)

def check_if_custom_output_dir_exists(custom_output_dir: str) -> bool:
    return Path(custom_output_dir).is_dir()


def return_logging_path(args: argparse.ArgumentParser) -> str:
    if hasattr(args, 'custom_output_dir'):
        if args.custom_output_dir is not None and check_if_custom_output_dir_exists(args.custom_output_dir):
            return os.path.join(args.custom_output_dir, TDVT_LOG_FILE_NAME)
        elif args.custom_output_dir is not None:
            sys.exit("The specified output directory doesn't exist: %s" % Path(args.custom_output_dir))
        else:
            pass
    return TDVT_LOG_FILE_NAME


def init():
    parser = create_parser()
    args = parser.parse_args()
    # Create logger.
    logging.basicConfig(filename=return_logging_path(args), level=logging.DEBUG, filemode='w',
                        format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    ch = logging.StreamHandler()
    if 'verbose' in args and args.verbose:
        # Log to console also.
        ch.setLevel(logging.DEBUG)
    else:
        args.verbose = False
        ch.setLevel(logging.WARNING)
    logger.addHandler(ch)

    logging.debug('TDVT version: ' + str(__version__))
    logging.debug('TDVT Arguments: ' + str(args))
    ds_reg = get_datasource_registry(sys.platform)
    configure_tabquery_path()
    register_tdvt_dialect()

    return parser, ds_reg, args

def is_test(args):
    return args.command in ['run', 'run-pattern', 'run-file', 'run-connectors-test']

def active_thread_count(threads):
    active = 0
    for t in threads:
        if t.is_alive():
            active += 1
    return active


def test_runner(all_tests, test_queue, max_threads):
    for i in range(0, max_threads):
        worker = threading.Thread(target=do_test_queue_work, args=(i, test_queue))
        worker.setDaemon(True)
        worker.start()
    test_queue.join()
    failed_tests = 0
    skipped_tests = 0
    disabled_tests = 0
    total_tests = 0
    for work in all_tests:
        if work.copy_files_and_cleanup():
            print("Left temp dir: " + work.temp_dir)
        failed_tests += work.failed_tests if work.failed_tests else 0
        skipped_tests += work.skipped_tests if work.skipped_tests else 0
        disabled_tests += work.disabled_tests if work.disabled_tests else 0
        total_tests += work.total_tests if work.total_tests else 0
    TestOutputFiles.write_test_results_csv(work.test_config.custom_output_dir)
    return failed_tests, skipped_tests, disabled_tests, total_tests


def run_tests_impl(tests: List[Tuple[TestSet, TestConfig]], max_threads: int, args) -> Optional[Tuple[int, int, int, int]]:
    if not tests:
        print("No tests found. Check arguments.")
        sys.exit()

    smoke_test_queue = queue.Queue()
    smoke_tests = []
    test_queue = queue.Queue()
    all_work = []
    lock = threading.Lock()

    for test_set, test_config in tests:
        runner = TestRunner(test_set, test_config, lock, args.verbose, len(all_work) + 1)
        if test_set.smoke_test:
            smoke_tests.append(runner)
            smoke_test_queue.put(runner)
        else:
            all_work.append(runner)

    logging.debug("smoke test queue size is: " + str(len(smoke_tests)))
    logging.debug("test queue size is: " + str(len(all_work)))

    require_smoke_test = args.command == 'run' and args.smoke_test
    force_run = args.command == 'run' and args.force_run

    if not smoke_tests:
        logging.warning("No smoke tests detected.")
        if require_smoke_test:
            sys.exit(1)
        else:
            logging.warning("Tests will run without verifying the data source connection.")

    if not all_work and not smoke_tests:
        sys.exit("No tests found. Check arguments.")

    failing_ds = set()
    failed_smoke_tests = 0
    skipped_smoke_tests = 0
    disabled_smoke_tests = 0
    total_smoke_tests = 0
    smoke_tests_run = 0

    absolute_start_time = time.time()
    smoke_test_run_time = 0

    if smoke_tests:
        smoke_test_threads = min(len(smoke_tests), max_threads)
        print("Starting smoke tests. Creating", str(smoke_test_threads), "worker threads.\n")

        failed_smoke_tests, skipped_smoke_tests, disabled_smoke_tests, total_smoke_tests = test_runner(
            smoke_tests, smoke_test_queue, smoke_test_threads)

        smoke_tests_run = total_smoke_tests - disabled_smoke_tests

        print("{} smoke test(s) ran. {} smoke tests disabled.".format(smoke_tests_run, disabled_smoke_tests))

        smoke_test_run_time = round(time.time() - absolute_start_time, 2)
        print("Smoke tests ran in {} seconds.".format(smoke_test_run_time))

        if failed_smoke_tests > 0:
            print("{} smoke test(s) failed. Please check logs for information.".format(failed_smoke_tests))
            failing_ds = set(item.test_set.ds_name for item in smoke_tests if item.failed_tests > 0)
            if require_smoke_test:
                print("\nSmoke tests failed, exiting.")
                sys.exit(1)

        if require_smoke_test:
            print("\nSmoke tests finished. Exiting.")
            sys.exit(0)

        if failing_ds and not force_run:
            print("Tests for the following data source(s) will not be run: {}".format(', '.join(failing_ds)))

    final_work = []

    for item in all_work:
        if not force_run:
            if item.test_set.ds_name in failing_ds:
                item.test_set.test_is_skipped = True
        final_work.append(item)
        test_queue.put(item)

    print("\nStarting tests. Creating " + str(max_threads) + " worker threads.")
    start_time = time.time()
    failed_tests, skipped_tests, disabled_tests, total_tests = test_runner(final_work, test_queue, max_threads)

    failed_tests += failed_smoke_tests
    skipped_tests += skipped_smoke_tests
    disabled_tests += disabled_smoke_tests
    total_tests += total_smoke_tests
    total_tests_run = total_tests - disabled_tests - skipped_tests
    total_passed_tests = total_tests_run - failed_tests
    now_time = time.time()
    main_test_time = round(now_time - start_time, 2)
    total_run_time = round(now_time - absolute_start_time, 2)

    print('\nTest Count: {} tests'.format(total_tests))
    print("\tPassed tests: {}".format(total_passed_tests))
    print("\tFailed tests: " + str(failed_tests))
    print("\tTests run: " + str(total_tests_run))
    print("\tDisabled tests: " + str(disabled_tests))
    print("\tSkipped tests: " + str(skipped_tests))
    print("\nOther information:")
    print("\tSmoke test time: {} seconds".format(smoke_test_run_time))
    print("\tMain test time: {} seconds".format(main_test_time))
    print("\tTotal time: {} seconds".format(total_run_time))

    return failed_tests, skipped_tests, disabled_tests, total_tests

def get_ds_list(ds):
    if not ds:
        return []
    ds_list = ds[0].split(',')
    ds_list = [x.strip() for x in ds_list]
    return ds_list

def run_desired_tests(args, ds_registry):
    generate_files(ds_registry, False)
    ds_to_run = ds_registry.get_datasources(get_ds_list(args.ds))
    if not ds_to_run:
        sys.exit(0)

    if len(ds_to_run) > 0:
        directory_to_delete = os.getcwd()
        if args.custom_output_dir:
            directory_to_delete = args.custom_output_dir
        delete_output_files(directory_to_delete)

    if not tabquerycli_exists():
        print("Could not find Tabquerycli.")
        sys.exit(0)

    max_threads = get_level_of_parallelization(args)
    test_sets: List[TestSet] = []

    for ds in ds_to_run:
        ds_info = ds_registry.get_datasource_info(ds)
        if not ds_info:
            continue

        print("Testing " + ds)
        max_threads_per_datasource = ds_info.run_time_config.maxthread;
        # if has multi datasource to run, then max_threads_per_datasource can not apply.
        if max_threads_per_datasource > 0:
            print("thread setting in " + ds + ".ini = " + str(max_threads_per_datasource))
            if len(ds_to_run) == 1:
                max_threads = max_threads_per_datasource
            else:
                print("Setting cannot apply since you are running multiple datasources.")

        suite = ds
        if args.command == 'run-pattern':
            single_test, single_test_config = enqueue_single_test(args, ds_info, suite)
            if single_test:
                test_sets.extend([(single_test, single_test_config)])
        else:
            test_sets.extend(enqueue_tests(ds_info, args, suite))

    failed_tests, skipped_tests, disabled_tests, total_tests = run_tests_impl(test_sets, max_threads, args)
    return failed_tests

def run_connectors_test(args):
    if not tabquerycli_exists():
        print("Could not find Tabquerycli.")
        sys.exit(0)

    if not args.conn_test or not args.conn_test_file:
        print("Missing arguments. Not running Connectors Test")
        sys.exit(0)

    if args.conn_test_password_file:
        print(run_connectors_test_core( args.conn_test, args.conn_test_file, args.conn_test_password_file))
    else:
         print(run_connectors_test_core( args.conn_test, args.conn_test_file))

def run_file(run_file: Path, output_dir: Path, threads: int, args) -> int:
    """Rerun all the failed tests listed in the json file."""

    logging.debug("Running failed tests from : " + str(run_file))
    # See if we need to generate test setup files.
    root_directory = get_root_dir()

    failed_tests, skipped_tests, disabled_tests, total_tests = \
        run_tests_impl(enqueue_failed_tests(run_file, root_directory, args), threads, args)

    # This can be a retry-step.
    return 0

def run_generate(ds_registry):
    start_time = time.time()
    generate_files(ds_registry, True)
    end_time = time.time() - start_time
    print("Done: " + str(end_time))


def main():
    parser, ds_registry, args = init()

    if args.command == 'action':
        if args.setup:
            print("Creating setup files...")
            create_test_environment()
            sys.exit(0)
        elif args.add_ds:
            add_datasource(args.add_ds, ds_registry)
            generate_files(ds_registry, True)
            sys.exit(0)
        elif args.action_generate:
            run_generate(ds_registry)
            sys.exit(0)
    elif is_test(args):
        if args.generate:
            run_generate(ds_registry)
            # It's ok to call generate and then run some tests, so don't exit here.
        if args.command == 'run-file':
            output_dir = os.getcwd()
            max_threads = get_level_of_parallelization(args)
            sys.exit(run_file(Path(args.run_file), Path(output_dir), max_threads, args))
        if args.command == 'run-connectors-test':
            run_connectors_test(args)
            sys.exit(0)
        error_code = run_desired_tests(args, ds_registry)
        sys.exit(error_code)
    elif args.command == 'action' and args.diff:
        tdvt_invocation = TdvtInvocation(from_args=args)
        run_diff(tdvt_invocation, args.diff)
        sys.exit(0)
    elif args.command == 'list-logical-configs':
        print_logical_configurations(ds_registry, args.list_logical_configs)
        sys.exit(0)
    elif args.command == 'list':
        print_configurations(ds_registry, [args.list_ds], args.verbose)
        sys.exit(0)

    logging.error("Could not interpret arguments. Nothing done.")
    parser.print_help()
    sys.exit(-1)

if __name__ == '__main__':
    main()
