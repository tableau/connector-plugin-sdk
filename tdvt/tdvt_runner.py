"""
    Test driver script for the Tableau Datasource Verification Tool

"""

import os
import sys
import argparse
import subprocess
import shutil
import tempfile
import threading
import time
import json
from zipfile import ZipFile
import glob
from .tdvt import generate_files, run_tests, init_logging, configure_tabquery_path, TdvtTestConfig

MAX_THREADS = 12
MAX_TDVT_THREADS = 4

#This contains the dictionary of configs you can run.
from .config_gen.datasource_list import WindowsRegistry,MacRegistry
from .config_gen.test_config import TestSet

class TestOutputFiles(object):
        output_actuals = 'tdvt_actuals_combined.zip'
        output_csv ="test_results_combined.csv"
        output_log ="tdvt_log_combined.txt"
        output_json = "tdvt_output_combined.json"
        all_output_files = [output_actuals, output_csv, output_log, output_json]

class TestRunner(threading.Thread):
    def __init__(self, logical, test_set, expected_sub_dir, verbose, d_override, suite, lock, clean_temp):
        threading.Thread.__init__(self)
        self.logical = logical
        self.verbose = verbose
        self.d_override = d_override
        self.tds_file = test_set.tds_name
        self.test_config = test_set.config_file_name
        self.expected_sub_dir = expected_sub_dir
        self.suite = suite
        self.error_code = 0
        self.thread_lock = lock
        self.temp_dir = tempfile.mkdtemp(prefix=suite)
        self.clean_temp = clean_temp
        self.sub_thread_count = MAX_TDVT_THREADS

    def copy_actual_files(self):
        dst = os.path.join(os.getcwd(), TestOutputFiles.output_actuals)
        mode = 'w' if not os.path.isfile(dst) else 'a'
        glob_path = os.path.join(self.temp_dir, 'actual.*')
        actual_files = glob.glob( glob_path )
        with ZipFile(dst, mode) as myzip:
            for actual in actual_files:
                myzip.write( actual )

    def copy_output_files(self):
        self.copy_output_file("test_results.csv", TestOutputFiles.output_csv, True)
        self.copy_output_file("tdvt_log.txt", TestOutputFiles.output_log, False)

    def copy_output_file(self, src, dst, trim_header):
        src = os.path.join(self.temp_dir, src)
        dst = os.path.join(os.getcwd(), dst)
        try:
            dst_exists = os.path.isfile(dst)
            src_file = open(src, 'r', encoding='utf8')
            mode = 'w' if not dst_exists else 'a'
            dst_file = open(dst, mode, encoding='utf8')

            line_count = 0
            for line in src_file:
                line_count += 1
                if line_count == 1 and trim_header and dst_exists:
                    continue
                dst_file.write(line)

            src_file.close()
            dst_file.close()
        except IOError:
            return

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

    def get_command_line(self):
        run_type = True if self.logical else False
        expected_sub_dir = self.expected_sub_dir if self.expected_sub_dir else ''
        override = self.d_override if self.d_override else ''
        test_cfg = TdvtTestConfig(False, True, output_dir = self.temp_dir, logical = run_type, suite_name = self.suite, expected_dir = expected_sub_dir, override = override, tds = self.tds_file, config = self.test_config, thread_count = self.sub_thread_count)
        return test_cfg

#    def get_command_line(self):
#        run_type = '-q' if self.logical else '-e'
#
#        cmdline = ["python", "tdvt.py", run_type, self.test_config, "-d", self.tds_file, '--suite', self.suite, '-t', str(self.sub_thread_count), '--output-dir', self.temp_dir]
#        if self.expected_sub_dir:
#            cmdline.append('--expected-dir')
#            cmdline.append(self.expected_sub_dir)
#        if self.verbose:
#            cmdline.append('--verbose')
#        if self.d_override:
#            cmdline.append('-DOverride')
#            cmdline.append(self.d_override)
#        return cmdline

    def run(self):
        #Send output to null.
        test_cfg = self.get_command_line()
        DEVNULL = open(os.devnull, 'wb')
        output = DEVNULL if not self.verbose else None
        self.thread_lock.acquire()
        print ("Calling " + str(test_cfg))
        self.thread_lock.release()

        start_time = time.time()
        #error_code = subprocess.call(cmdline, stdout=output)
        error_code = run_tests(test_cfg)
        self.thread_lock.acquire()
        run_type = 'logical' if self.logical else 'expression'
        print ("Ran " + self.suite + " " + run_type)
        print ("Run time: " + str(time.time() - start_time))
        if error_code > 0:
            print ("Test failed: " + str(error_code))
        try:
            self.copy_actual_files()
            self.copy_output_files()
            self.copy_test_result_file()
        except Exception as e:
            print (e)
            pass
        self.thread_lock.release()
        
        self.error_code = error_code

    def __del__(self):
        if self.clean_temp:
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass

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
        reg= MacRegistry()
    else:
        reg = WindowsRegistry()

    return reg

def print_configurations(ds_reg, dsname):
    print ("\nAvailable datasources")
    ds_all = ds_reg.get_datasources('all')
    for ds in sorted(ds_all):
        print (ds)
    if dsname:
        ds_to_run = ds_reg.get_datasources(dsname)
        print ("\nDatasource set: " + dsname)
        for ds in ds_to_run:
            print ("\n\t" + ds)
            test_config = ds_reg.get_datasource_info(ds)
            if not test_config:
                continue
            print ("\tLogical tests:")
            for x in test_config.get_logical_tests():
                print ("\t"*2 + x.config_file_name)
            print ("\tExpression tests:")
            for x in test_config.get_expression_tests():
                print ("\t"*2 + x.config_file_name)
    print ("\nAvailable suites:")
    for suite in ds_reg.suite_map:
        print (suite)

class SingleTestConfig(object):
    """Maintain information about running a single test. This is different that running a test suite which has a premade config file."""
    def __init__(self, test_pattern, tds_pattern, exclude_pattern):
        self.valid = False
        if test_pattern and tds_pattern:
            try:
                fd, tmppath = tempfile.mkstemp(suffix='.cfg')
                tmpcfg = open(tmppath, 'w')
                tmpcfg.write("allow:\n")
                tmpcfg.write(test_pattern)
                tmpcfg.write("\n")
                if exclude_pattern:
                    tmpcfg.write("exclude:\n")
                    tmpcfg.write(exclude_pattern)
                    tmpcfg.write("\n")
                tmpcfg.close()
                os.close(fd)
            except:
                return

            self.temp_cfg_path = tmppath
            self.tds_pattern = tds_pattern
            self.valid = True

    def __del__(self):
        if not self.valid:
            return
        try:
            if VERBOSE: print ("Removing " + self.temp_cfg_path)
            os.remove(self.temp_cfg_path)
        except OSError:
            pass

def get_test_sets_to_run(function_call, test_pattern, single_test):
        test_sets_to_run = [] 
        if single_test.valid:
            tds_name = single_test.tds_pattern.replace('*', ds)
            test_sets_to_run.append(TestSet(single_test.temp_cfg_path, tds_name, '', ''))
        else:
            test_sets_to_run = function_call(test_pattern)

        return test_sets_to_run

def enqueue_tests(is_logical, ds_info, args, single_test, suite, lock, test_threads, test_run):
    tests = None
    if is_logical:
        tests = get_test_sets_to_run(ds_info.get_logical_tests, args.logical_only, single_test)
    else:
        tests = get_test_sets_to_run(ds_info.get_expression_tests, args.expression_only, single_test)

    if not tests:
        return

    for test_set in tests:
        runner = TestRunner(is_logical, test_set, args.expected_dir, args.verbose, ds_info.d_override, suite, lock, args.noclean)
        test_threads.append(runner)
        test_run += 1

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

    Run one test against many datasources.
        tdvt_runner --exp exprtests/standard/setup.date.datepart.second*.txt --tdp cast_calcs.*.tds --run sqlserver,vertica
    The 'exp' argument is a glob pattern that is used to find the test file. It is the same style as what you will find in the existing *.cfg files.
    The 'test-ex' argument can be used to exclude test files. This is a regular expression pattern.
    The tds pattern is used to find the tds. Use a '*' character where the tds name will be substituted, ie cast_calcs.*.tds for cast_calcs.sqlserver.tds etc.

    Run all the BUGS logical tests against sqlserver.
        tdvt_runner --logp logicaltests/setup/calcs/setup.BUGS.*.dbo.xml --tdp cast_calcs.*.tds --run sqlserver

    But skip 59740?
        tdvt_runner --logp logicaltests/setup/calcs/setup.BUGS.*.dbo.xml --tdp cast_calcs.*.tds --test-ex 59740 --run sqlserver

'''

parser = argparse.ArgumentParser(description='TDVT Driver.', usage=usage_text())
parser.add_argument('--list', dest='list_ds', help='List datasource config.', required=False, default=None, const='', nargs='?')
parser.add_argument('--generate', dest='generate', action='store_true', help='Force config file generation.', required=False)
parser.add_argument('--run', '-r', dest='ds', help='Comma separated list of Datasource names to test or \'all\'.', required=False)
parser.add_argument('--logical', '-q', dest='logical_only', help='Only run logical tests whose config file name matches the supplied string, or all if blank.', required=False, default=None, const='', nargs='?')
parser.add_argument('--expression', '-e', dest='expression_only', help='Only run expression tests whose config file name matches the suppled string, or all if blank.', required=False, default=None, const='', nargs='?')
parser.add_argument('--expected-dir', dest='expected_dir', help='Unique subdirectory for expected files.', required=False)
parser.add_argument('--threads', '-t', dest='thread_count', type=int, help='Max number of threads to use.', required=False)
parser.add_argument('--threads_tdvt', '-tt', dest='thread_count_tdvt', type=int, help='Max number of threads to use for the TDVT subprocess calls.', required=False)
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Verbose output.', required=False)
parser.add_argument('--no-clean', dest='noclean', action='store_true', help='Leave temp dirs.', required=False)
parser.add_argument('--exp', dest='expression_pattern', help='Only run expression tests whose name and path matches the suppled string. This is a glob pattern. Also set the tds-pattern to use when running the test.', required=False, default=None, const='', nargs='?')
parser.add_argument('--logp', dest='logical_pattern', help='Only run logical tests whose name and path matches the suppled string. this is a glob pattern. Also set the tds-pattern to use when running the test.', required=False, default=None, const='', nargs='?')
parser.add_argument('--tdp', dest='tds_pattern', help='The datasource tds pattern to use when running the test. See exp and logp arguments.', required=False, default=None, const='', nargs='?')
parser.add_argument('--test-ex', dest='test_pattern_exclude', help='Exclude tests whose name matches the suppled string. This is a regular expression pattern. Can be used with exp and logp arguments. Also set the tds-pattern to use when running the test.', required=False, default=None, const='', nargs='?')

args = parser.parse_args()

VERBOSE = args.verbose
ds_reg = get_datasource_registry(sys.platform)

if args.list_ds is not None:
    print_configurations(ds_reg, args.list_ds)
    sys.exit(0)

init_logging(verbose=VERBOSE)
configure_tabquery_path()
if args.generate:
    print ("Generating config files...")
    generate_files(True)
    print ("Done")

lock = threading.Lock()
ds_to_run = ds_reg.get_datasources(args.ds)
if not ds_to_run:
    sys.exit(0)

if len(ds_to_run) > 0:
    delete_output_files(os.getcwd())

#Check if the user wants to run a single test file. If so then create a temporary cfg file to hold that config.
test_pattern = args.expression_pattern if args.expression_pattern is not None else args.logical_pattern
tds_pattern = args.tds_pattern
single_test = SingleTestConfig(test_pattern, tds_pattern, args.test_pattern_exclude)

test_threads = []
start_time = time.time()
error_code = 0
test_run = 0
for ds in ds_to_run:
    ds_info = ds_reg.get_datasource_info(ds)
    if not ds_info:
        continue

    print ("Testing " + ds)

    suite = ds
    run_expr_tests = True if args.logical_only is None and args.logical_pattern is None else False
    run_logical_tests = True if args.expression_only is None and args.expression_pattern is None else False

    if VERBOSE: print("Run expression tests? " + str(run_expr_tests))
    if VERBOSE: print("Run logical tests? " + str(run_logical_tests))

        
    if run_logical_tests:
        enqueue_tests(True, ds_info, args, single_test, suite, lock, test_threads, test_run)

    if run_expr_tests:
        enqueue_tests(False, ds_info, args, single_test, suite, lock, test_threads, test_run)

#Adjust the max threads for this process and the tdvt.
if args.thread_count:
    MAX_THREADS = args.thread_count
    MAX_TDVT_THREADS = args.thread_count_tdvt
else:
    total_procs = len(test_threads)
    if total_procs < MAX_THREADS and total_procs > 0:
        #There are fewer procs than available threads, so increase the tdvt threads.
        tdvt_threads = int((MAX_THREADS * MAX_TDVT_THREADS)/total_procs)
        #Keep it reasonable.
        MAX_TDVT_THREADS = min(tdvt_threads, 16)

for test_thread in test_threads:
    test_thread.sub_thread_count = MAX_TDVT_THREADS

print ("Setting tdvt_runner thread count to: " + str(MAX_THREADS))
print ("Setting tdvt threads to : " + str(MAX_TDVT_THREADS))

if not test_threads:
    print ("No tests found. Check arguments.")
    sys.exit()

for test_thread in test_threads:
    while threading.activeCount() > MAX_THREADS:
        time.sleep(0.05)
    test_thread.daemon = True
    print ("LR STarting thread")
    test_thread.start()

for test_thread in test_threads:
    test_thread.join()

for test_thread in test_threads:
    if args.noclean:
        print ("Left temp dir: " + test_thread.temp_dir)
    error_code += test_thread.error_code

print ("Total time: " + str(time.time() - start_time))
print ("Total failed tests " + str(error_code))

sys.exit(error_code)

