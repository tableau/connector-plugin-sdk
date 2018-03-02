"""
    Test driver script for the Tableau Datasource Verification Tool

"""

import sys

if sys.version_info[0] < 3:
    raise EnvironmentError("TDVT requires Python 3 or greater.")

__version__ = '1.1.63'

import os
import argparse
import subprocess
import shutil
import tempfile
import threading
import time
import json
import queue
import logging
from zipfile import ZipFile
import glob
from .tdvt_core import generate_files, run_diff, run_failed_tests, run_tests, TdvtTestConfig, generate_test_file_list_from_config
from .config_gen.test_config import SingleLogicalTestSet, SingleExpressionTestSet
from .config_gen.gentests import list_configs, list_config
from .tabquery import *
from .setup_env import create_test_environment, add_datasource

#This contains the dictionary of configs you can run.
from .config_gen.datasource_list import WindowsRegistry,MacRegistry,LinuxRegistry
from .config_gen.test_config import TestSet

class TestOutputFiles(object):
    output_actuals = 'tdvt_actuals_combined.zip'
    output_csv ="test_results_combined.csv"
    output_json = "tdvt_output_combined.json"
    all_output_files = [output_actuals, output_csv, output_json]

    @staticmethod
    def copy_output_file(src_name, src_dir, dst, trim_header, append=True):
        src = os.path.join(src_dir, src_name)
        dst = os.path.join(os.getcwd(), dst)
        logging.debug("Copying {0} to {1}".format(src, dst))
        try:
            dst_exists = os.path.isfile(dst)
            src_file = open(src, 'r', encoding='utf8')
            mode = 'w' if not dst_exists or not append else 'a'
            dst_file = open(dst, mode, encoding='utf8')

            line_count = 0
            for line in src_file:
                line_count += 1
                if line_count == 1 and trim_header and dst_exists:
                    continue
                dst_file.write(line)

            src_file.close()
            dst_file.close()
        except IOError as e:
            logging.debug("Exception while copying files: " + str(e))
            return

def do_test_queue_work(i, q):
    """This will be called in a queue.join() context, so make sure to mark all work items as done and
    continue through the loop. Don't try and exit or return from here if there are still work items in the queue.
    See the python queue documentation."""

    abort_test_run = False
    while True:
        #This blocks if the queue is empty.
        work = q.get()

        work.run()

        q.task_done()



class TestRunner():
    def __init__(self, test_set, test_config, lock, verbose, thread_id):
        threading.Thread.__init__(self)
        self.test_set = test_set
        self.test_config = test_config
        self.error_code = 0
        self.thread_id = thread_id
        self.verbose = verbose
        self.thread_lock = lock
        self.temp_dir = tempfile.mkdtemp(prefix=self.test_config.suite_name)
        self.test_config.output_dir = self.temp_dir
        self.sub_thread_count = 1
        self.sub_thread_count_set = False

    def copy_actual_files(self):
        dst = os.path.join(os.getcwd(), TestOutputFiles.output_actuals)
        mode = 'w' if not os.path.isfile(dst) else 'a'
        glob_path = os.path.join(self.temp_dir, 'actual.*')
        actual_files = glob.glob( glob_path )
        with ZipFile(dst, mode) as myzip:
            for actual in actual_files:
                myzip.write( actual )

    def set_thread_count(self, threads):
        logging.debug("test suite " + self.test_config.suite_name + " subthread set to: " + str(threads))
        self.sub_thread_count = threads
        self.test_config.thread_count = threads
        self.sub_thread_count_set = True

    def get_thread_count(self):
        return self.sub_thread_count

    def has_set_thread_count(self):
        return self.sub_thread_count_set
    

    def copy_output_files(self):
        TestOutputFiles.copy_output_file("test_results.csv", self.temp_dir, TestOutputFiles.output_csv, True)

    def copy_test_result_file(self):
        src = os.path.join(self.temp_dir, "tdvt_output.json")
        dst = os.path.join(os.getcwd(), TestOutputFiles.output_json)
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
                
                dst_file = open(dst, 'w', encoding='utf8')
                json.dump(existing_results, dst_file)
                dst_file.close()
        except IOError:
            return

    def copy_files_and_cleanup(self):
        try:
            self.copy_actual_files()
            self.copy_output_files()
            self.copy_test_result_file()
        except Exception as e:
            print (e)
            pass

        try:
            if not self.test_config.leave_temp_dir:
                shutil.rmtree(self.temp_dir)
        except:
            pass

    def run(self):
        #Send output to null.
        DEVNULL = open(os.devnull, 'wb')
        output = DEVNULL if not self.verbose else None
        logging.debug( "\nRunning tdvt " + str(self.test_config) + " tdvt thread id: " + str(self.thread_id) + "\n")
        print ("\nRunning {0} {1} {2}\n".format( self.test_config.suite_name, self.test_config.config_file, str(self.thread_id)) )

        start_time = time.time()
        error_code = run_tests(self.test_config, self.test_set)
        logging.debug( "\nFinished tdvt " + str(self.test_config) + "\n")
        print ("\nFinished {0} {1} {2}\n".format( self.test_config.suite_name, self.test_config.config_file, str(self.thread_id)) )
        
        self.error_code = error_code


def delete_output_files(root_dir):
    for f in TestOutputFiles.all_output_files:
        out_file = os.path.join(root_dir, f)
        if os.path.exists(out_file):
            try:
                os.unlink(out_file)
            except Exception as e:
                print (e)
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

def print_logical_configurations(ds_registry, config_name=None):
    if config_name:
        for config in list_config(ds_registry, config_name):
            print(config)
    else:
        print ("Available logical query configurations: \n")
        for config in list_configs(ds_registry):
            print (config)

def print_ds(ds, ds_reg):
    print ("\n\t" + ds)
    test_config = ds_reg.get_datasource_info(ds)
    if not test_config:
        return
    print ("\tLogical tests:")
    for x in test_config.get_logical_tests():
        print ("\t"*2 + str(x))
        root_directory = get_root_dir()
        tests = generate_test_file_list_from_config(root_directory, x)
        for test in tests:
            print ("\t"*3 + test.test_path)

    print ("\tExpression tests:")
    for x in test_config.get_expression_tests():
        print ("\t"*2 + str(x))
        root_directory = get_root_dir()
        tests = generate_test_file_list_from_config(root_directory, x)
        for test in tests:
            print ("\t"*3 + test.test_path)

def print_configurations(ds_reg, dsname):
    if dsname:
        ds_to_run = ds_reg.get_datasources(dsname)
        if len(ds_to_run) == 1:
            print_ds(ds_to_run[0], ds_reg)
        elif len(ds_to_run) == 0:
            pass
        else:
            print ("\nDatasource suite " + dsname + " is "  + ",".join(ds_to_run)) 
            if VERBOSE:
                for ds in ds_to_run:
                    print_ds(ds, ds_reg)
                    
    else:
        print ("\nAvailable datasources:")
        ds_all = ds_reg.get_datasources('all')
        for ds in sorted(ds_all):
            print (ds)
        print ("\nAvailable suites:")
        for suite in ds_reg.suite_map:
            print (suite)
            print ("\t" + ','.join(ds_reg.suite_map[suite]))
            print ('\n')

def get_single_test_config(is_logical, test_pattern, tds_pattern, exclude_pattern, ds_info):
        if not test_pattern or not tds_pattern:
            return None
        single_test = None
        if is_logical:
            single_test = SingleLogicalTestSet(test_pattern, tds_pattern, exclude_pattern, ds_info)
        else:
            single_test = SingleExpressionTestSet(test_pattern, tds_pattern, exclude_pattern, ds_info)
        return single_test

def get_test_sets_to_run(function_call, test_pattern, single_test):
        test_sets_to_run = [] 
        if single_test:
            test_sets_to_run.append(single_test)
        else:
            test_sets_to_run = function_call(test_pattern)

        return test_sets_to_run

def enqueue_tests(is_logical, ds_info, args, single_test, suite, lock, test_queue, all_work, test_run, max_threads):

    tests = None
    if is_logical:
        tests = get_test_sets_to_run(ds_info.get_logical_tests, args.logical_only, single_test)
    else:
        tests = get_test_sets_to_run(ds_info.get_expression_tests, args.expression_only, single_test)

    if not tests:
        print ("Did not find any tests for " + suite)
        return

    for test_set in tests:
        test_config = TdvtTestConfig(from_args=args)
        test_config.suite_name = suite
        test_config.logical = is_logical
        test_config.d_override = ds_info.d_override
        test_config.run_as_perf = ds_info.run_as_perf
        test_config.tds = test_set.tds_name
        test_config.config_file = test_set.config_name

        runner = TestRunner(test_set, test_config, lock, VERBOSE, test_run)
        logging.debug("Queing up tests: " + str(test_config))
        #if ini file has subthread setting, set it now.
        if ds_info.maxsubthread > 0 and ds_info.maxsubthread < max_threads:
            runner.set_thread_count(ds_info.maxsubthread);
        else:
            runner.set_thread_count(max_threads)

        all_work.append(runner)
        test_queue.put(runner)


        test_run += 1
    return test_run

def get_level_of_parallelization(args):
    #This indicates how many database/test suite combinations to run at once
    max_threads = 6
    #This indicates how many tests in each test suite thread to run at once. Each test is a database connection.
    max_sub_threads = 4

    #arg thread setting has first priority.

    if args.thread_count or args.thread_count_tdvt:
        if args.thread_count:
            max_threads = args.thread_count
        if args.thread_count_tdvt:
            max_sub_threads = args.thread_count_tdvt

    print ("Setting tdvt thread count to: " + str(max_threads))
    print ("Setting sub thread count to : " + str(max_sub_threads))
    return max_threads, max_sub_threads

def usage_text():
    return '''
    TDVT Driver. Run groups of logical and expression tests against one or more datasources.

    Show all test suites
        tdvt_runner --list

    See what a test suite consists of
        tdvt_runner --list sqlserver
        tdvt_runner --list standard

    The 'run' argument can take a single datasource, a list of data sources, or a test suite name. in any combination.
        tdvt_runner --run vertica
        tdvt_runner --run sqlserver,vertica
        tdvt_runner --run standard

    Both logical and expression tests are run by default.
    Run all sqlserver expression tests
        tdvt_runner -e --run sqlserver

    Run all vertica logical tests
        tdvt_runner -q --run vertica

    There are two groups of expression tests, standard and LOD (level of detail). The config files that drive the tests are named expression_test.sqlserver.cfg and expression.lod.sqlserver.cfg.
    To run just one of those try entering part of the config name as an argument:
        tdvt_runner -e lod --run sqlserver
    This will run all the LOD tests against sqlserver.

    And you can run all the LOD tests against the standard datasources like
        tdvt_runner -e lod --run standard

    Run one test against many datasources
        tdvt_runner --exp exprtests/standard/setup.date.datepart.second*.txt --tdp cast_calcs.*.tds --run sqlserver,vertica

    The 'exp' argument is a glob pattern that is used to find the test file. It is the same style as what you will find in the existing *.cfg files.
    The 'test-ex' argument can be used to exclude test files. This is a regular expression pattern.
    The tds pattern is used to find the tds. Use a '*' character where the tds name will be substituted, ie cast_calcs.*.tds for cast_calcs.sqlserver.tds etc.

    Run one logical query test against many datasources
        tdvt_runner --logp logicaltests/setup/calcs/setup.BUGS.B1713.?.xml --tdp cast_calcs.*.tds --run postgres

    This can be combined with * to run an arbitrary set of 'correct' logical query tests against a datasources
        tdvt_runner --logp logicaltests/setup/calcs/setup.BUGS.*.?.xml --tdp cast_calcs.*.tds --run postgres
    Alternatively
        tdvt_runner --logp logicaltests/setup/calcs/setup.BUGS.*.dbo.xml --tdp cast_calcs.*.tds --run sqlserver

    But skip 59740?
        tdvt_runner --logp logicaltests/setup/calcs/setup.BUGS.*.dbo.xml --tdp cast_calcs.*.tds --test-ex 59740 --run sqlserver

    '''

def create_parser():
    parser = argparse.ArgumentParser(description='TDVT Driver.', usage=usage_text())
    parser.add_argument('--list', dest='list_ds', help='List datasource config.', required=False, default=None, const='', nargs='?')
    parser.add_argument('--list_logical_configs', dest='list_logical_configs', help='List available logical configs.', required=False, default=None, const='', nargs='?')
    parser.add_argument('--generate', dest='generate', action='store_true', help='Force config file generation.', required=False)
    parser.add_argument('--setup', dest='setup', action='store_true', help='Create setup directory structure.', required=False)
    parser.add_argument('--add_ds', dest='add_ds', help='Add a new datasource.', required=False)
    parser.add_argument('--run', '-r', dest='ds', help='Comma separated list of Datasource names to test or \'all\'.', required=False)
    parser.add_argument('--logical', '-q', dest='logical_only', help='Only run logical tests whose config file name matches the supplied string, or all if blank.', required=False, default=None, const='', nargs='?')
    parser.add_argument('--expression', '-e', dest='expression_only', help='Only run expression tests whose config file name matches the suppled string, or all if blank.', required=False, default=None, const='', nargs='?')
    parser.add_argument('--expected-dir', dest='expected_dir', help='Unique subdirectory for expected files.', required=False)
    parser.add_argument('--threads', '-t', dest='thread_count', type=int, help='Max number of threads to use.', required=False)
    parser.add_argument('--threads_sub', '-tt', dest='thread_count_tdvt', type=int, help='Max number of threads to use for the subprocess calls. There is one database connection per subprocess call.', required=False)
    parser.add_argument('--verbose', dest='verbose', action='store_true', help='Verbose output.', required=False)
    parser.add_argument('--no-clean', dest='noclean', action='store_true', help='Leave temp dirs.', required=False)
    parser.add_argument('--exp', dest='expression_pattern', help='Only run expression tests whose name and path matches the suppled string. This is a glob pattern. Also set the tds-pattern to use when running the test.', required=False, default=None, const='', nargs='?')
    parser.add_argument('--logp', dest='logical_pattern', help='Only run logical tests whose name and path matches the suppled string. this is a glob pattern. Also set the tds-pattern to use when running the test. Use a ? to replace the logical query config component of the test name.', required=False, default=None, const='', nargs='?')
    parser.add_argument('--tdp', dest='tds_pattern', help='The datasource tds pattern to use when running the test. See exp and logp arguments.', required=False, default=None, const='', nargs='?')
    parser.add_argument('--test-ex', dest='test_pattern_exclude', help='Exclude tests whose name matches the suppled string. This is a regular expression pattern. Can be used with exp and logp arguments. Also set the tds-pattern to use when running the test.', required=False, default=None, const='', nargs='?')
    parser.add_argument('--compare-sql', dest='compare_sql', action='store_true', help='Compare SQL.', required=False)
    parser.add_argument('--nocompare-tuples', dest='nocompare_tuples', action='store_true', help='Do not compare Tuples.', required=False)
    parser.add_argument('--diff-test', '-dd', dest='diff', help='Diff the results of the given test (ie exprtests/standard/setup.calcs_data.txt) against the expected files. Can be used with the sql and tuple options.', required=False)
    parser.add_argument('-f', dest='run_file', help='Json file containing failed tests to run.', required=False)
    return parser

def init():
    parser = create_parser()
    args = parser.parse_args()
    global VERBOSE
    VERBOSE = args.verbose
    #Create logger.
    logging.basicConfig(filename='tdvt_log_combined.txt',level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
    logger = logging.getLogger()
    if VERBOSE:
        #Log to console also.
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
    
    logging.debug('TDVT version: ' + str(__version__))
    ds_reg = get_datasource_registry(sys.platform)
    configure_tabquery_path()

    return parser, ds_reg, args

def active_thread_count(threads):
    active = 0
    for t in threads:
        if t.is_alive():
            active += 1
    return active

def run_file(run_file, output_dir, sub_threads):

    result_code = run_failed_tests(run_file, output_dir, sub_threads)
    TestOutputFiles.copy_output_file("test_results.csv", '', TestOutputFiles.output_csv, False, False)
    TestOutputFiles.copy_output_file("tdvt_output.json", '', TestOutputFiles.output_json, False, False)
    
    #This can be a retry-step.
    return 0

def run_desired_tests(args, ds_registry):
    generate_files(ds_registry, False)
    lock = threading.Lock()
    ds_to_run = ds_registry.get_datasources(args.ds)
    if not ds_to_run:
        sys.exit(0)

    if len(ds_to_run) > 0:
        delete_output_files(os.getcwd())

    if not tabquerycli_exists():
        print ("Could not find Tabquerycli.")
        sys.exit(0)

    error_code = 0
    test_run = 0
    start_time = time.time()
    test_queue = queue.Queue()
    all_work = []

    max_threads, max_sub_threads = get_level_of_parallelization(args)

    for ds in ds_to_run:
        ds_info = ds_registry.get_datasource_info(ds)
        if not ds_info:
            continue

        print ("Testing " + ds)
        max_threads_per_datasource = ds_info.maxthread;
        max_sub_threads_per_datasource = ds_info.maxsubthread;
        #if has multi datasource to run, then max_threads_per_datasource can not apply.
        if max_threads_per_datasource > 0:
            print ("thread setting in " + ds +".ini = " + str(max_threads_per_datasource))
            if len(ds_to_run) == 1:
                max_threads = max_threads_per_datasource
            else:
                print ("Setting cannot apply since you are running multiple datasources.")
        if max_sub_threads_per_datasource > 0:
            print ("subthread setting in " + ds + ".ini = " + str(max_sub_threads_per_datasource))

        suite = ds
        run_expr_tests = True if args.logical_only is None and args.logical_pattern is None else False
        run_logical_tests = True if args.expression_only is None and args.expression_pattern is None else False

        if VERBOSE: print("Run expression tests? " + str(run_expr_tests))
        if VERBOSE: print("Run logical tests? " + str(run_logical_tests))

            
        if run_logical_tests:
            single_test = get_single_test_config(True, args.logical_pattern, args.tds_pattern, args.test_pattern_exclude, ds_info)
            test_run = enqueue_tests(True, ds_info, args, single_test, suite, lock, test_queue, all_work, test_run, max_sub_threads)

        if run_expr_tests:
            single_test = get_single_test_config(False, args.expression_pattern, args.tds_pattern, args.test_pattern_exclude, ds_info)
            test_run = enqueue_tests(False, ds_info, args, single_test, suite, lock, test_queue, all_work, test_run, max_sub_threads)

    if not all_work:
        print ("No tests found. Check arguments.")
        sys.exit()

    print ("Creating " + str(max_threads) + " worker threads.")
    for i in range(0, max_threads):
        worker = threading.Thread(target=do_test_queue_work, args=(i, test_queue))
        worker.setDaemon(True)
        worker.start()

    test_queue.join()



    for work in all_work:
        work.copy_files_and_cleanup()
        if args.noclean:
            print ("Left temp dir: " + work.temp_dir)
        error_code += work.error_code if work.error_code else 0

    print ('\n')
    print ("Total time: " + str(time.time() - start_time))
    print ("Total failed tests " + str(error_code))
    
    return error_code

def main():

    parser, ds_registry, args = init()

    if args.setup:
        print ("Creating setup files...")
        create_test_environment()
        sys.exit(0)
    if args.add_ds:
        print ("Make sure you have already saved the appropriate TDS files in the tds directory.")
        print ("Adding a new datasource [" + args.add_ds + "] ...")
        password = input("Enter the datasource password:")
        picked = False
        logical = None
        while not picked:
            logical = input("Enter the logical config to use or type 'list' to see the options or 's' to skip selecting one now:")
            if logical == 'list':
                print_logical_configurations(ds_registry)
            else:
                logical = logical.replace("\"", "")
                logical = logical.replace("\'", "")
                logical = logical.strip()
                picked = True
            if logical == 's':
                logical = None

        add_datasource(args.add_ds, password, logical)
        generate_files(ds_registry, True)
        sys.exit(0)
    elif args.generate:
        start_time = time.time()
        generate_files(ds_registry, True)
        end_time = time.time() - start_time
        print ("Done: " + str(end_time))
        
        #It's ok to call generate and then run some tests, so don't exit here.
    elif args.diff:
        #Set verbose so the user sees something from the diff.
        VERBOSE = True
        test_config = TdvtTestConfig(from_args=args)
        run_diff(test_config, args.diff)
        sys.exit(0)
    elif args.run_file:
        output_dir = os.getcwd()
        max_threads, max_subthreads = get_level_of_parallelization(args)
        sys.exit(run_file(args.run_file, output_dir, max_subthreads))
    elif args.list_logical_configs is not None:
        print_logical_configurations(ds_registry, args.list_logical_configs)
        sys.exit(0)
    elif args.list_ds is not None:
        print_configurations(ds_registry, args.list_ds)
        sys.exit(0)

    error_code = run_desired_tests(args, ds_registry)

    sys.exit(error_code)

if __name__ == '__main__':
    main()
