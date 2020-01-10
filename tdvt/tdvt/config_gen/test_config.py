"""
    TestConfig defines how to run tests with TDVT runner.

"""

import glob
import re
from ..resources import *
from ..tabquery_path import TabQueryPath

class TestFile(object):
    """
        Information about the location of a test file.
    """
    def __init__(self, root_dir, full_test_path):
        self.root_dir = root_dir
        self.test_path = full_test_path
        self.relative_test_path = self.test_path.replace(self.root_dir,'')
        if self.relative_test_path and (self.relative_test_path[0] == '\\' or self.relative_test_path[0] == '/'):
            self.relative_test_path = self.relative_test_path[1:]

    def __str__(self):
        return self.test_path

class TestSet(object):
    """
        Represents everything needed to run a set of tests. This includes a path to the test files, which tds etc.
    """
    def __init__(self, ds_name, root_dir, config_name, tds_name, exclusions, test_pattern, is_logical, suite_name, password_file,
                 expected_message: str = '', smoke_test: bool = False, test_is_enabled: bool = True,
                 test_is_skipped: bool = False):
        self.ds_name = ds_name
        self.suite_name = suite_name
        self.config_name = config_name
        self.tds_name = tds_name
        self.exclusions = exclusions
        self.test_pattern = test_pattern
        self.is_logical = is_logical
        self.root_dir = root_dir
        self.password_file = password_file
        self.expected_message = expected_message
        self.smoke_test = smoke_test
        self.test_is_enabled = test_is_enabled
        self.test_is_skipped = test_is_skipped
        self.test_list_cached = None
        self.test_list_checked = False


    def is_logical_test(self):
        return self.is_logical

    def get_password_file_name(self):
        return get_resource_full_path(self.root_dir, self.suite_name + ".password", "tds") if not self.password_file else get_resource_full_path(self.root_dir, self.password_file, "tds")

    def get_expected_message(self):
        return self.expected_message

    def get_expected_output_file_path(self, test_file, output_dir):
        return ''

    def get_actual_and_base_file_path(self, test_file, output_dir):
        return '', ''

    def generate_test_file_list(self):
        """Take the config and expand it into the list of tests cases to run. These are fully qualified paths to test files.
           Return the sorted list of tests.

        """
        if self.test_list_checked:
            return self.test_list_cached

        final_test_list = self.__generate_test_file_list()

        self.test_list_cached = final_test_list
        self.test_list_checked = True
        return self.test_list_cached

    def get_test_dirs(self):
        return (self.root_dir, get_local_test_dir())

    def __generate_test_file_list(self):
        """Private function to generate the list of tests."""
        allowed_tests = []
        exclude_tests = self.get_exclusions()
        exclude_tests.append('expected.')
        exclude_tests.append('actual.')

        #Allowed/exclude can be filenames or directory fragments.
        tests_to_run = []
        added_test = len(tests_to_run)
        allowed_path = ''

        #Check local dir first then the root package directory.
        checked_paths = []
        for test_dir in self.get_test_dirs():
            allowed_path = os.path.join(test_dir, self.test_pattern)
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

        regexes = []
        for ex in exclude_tests:
            try:
                ex = ex.strip()
                if not ex:
                    continue
                regex = re.compile(ex)
                regexes.append(regex)
            except BaseException as e:
                print ("Error compiling regular expression for test file exclusions: '" + str(ex) + "' exception: " +
                       str(e))

        final_test_list = list(tests_to_run)
        for test in tests_to_run:
            for regex in regexes:
                if re.search(regex, test.test_path) and test in final_test_list:
                    logging.debug("Removing test that matched: " + str(regex))
                    final_test_list.remove(test)

        logging.debug("Found " + str(len(final_test_list)) + " tests to run after exclusions.")
        return sorted(final_test_list, key = lambda x: x.test_path)

    def get_exclusions(self):
        return [] if not self.exclusions else self.exclusions.split(',')

    def __str__(self):
        return "[name={0}] [tds={1}] [exclusions={2}] [test pattern={3}] [is_logical={4}] [root_dir={5}]".format(self.config_name, self.tds_name, self.exclusions, self.test_pattern, self.is_logical, self.root_dir)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

class FileTestSet(TestSet):
    """Used to run previously failed tests. Supports appending test files rather than using a search pattern like the
       other test sets."""

    def __init__(self, ds_name, root_dir, config_name, tds_name, logical, suite, password_file='',
                 expected_message='', smoke_test=False, test_is_enabled=True, test_is_skipped=False):
        self.test_paths = []
        self.logical = logical
        if logical:
            self.delegator = LogicalTestSet(ds_name, root_dir, config_name, tds_name, '', '', suite, password_file,
                                            expected_message, smoke_test, test_is_enabled, test_is_skipped)
        else:
            self.delegator = ExpressionTestSet(ds_name, root_dir, config_name, tds_name, '', '', suite, password_file,
                                               expected_message, smoke_test, test_is_enabled, test_is_skipped)
        super(FileTestSet, self).__init__(ds_name, root_dir, config_name, tds_name, '', '', logical, suite,
                                          password_file, expected_message, smoke_test, test_is_enabled, test_is_skipped)

    def get_expected_output_file_path(self, test_file, output_dir):
        return self.delegator.get_expected_output_file_path(test_file, output_dir)

    def get_actual_and_base_file_path(self, test_file, output_dir):
        if self.logical:
            return self.delegator.get_actual_and_base_file_path(test_file, output_dir)
        else:
            return ("", "")

    def append_test_file(self, file_path):
        self.test_paths.append(file_path)

    def generate_test_file_list(self):
        tests_to_run = []
        for test_file in self.test_paths:
            added_test = False
            for test_dir in self.get_test_dirs():
                if added_test:
                    continue
                allowed_path = os.path.join(test_dir, test_file)
                logging.debug("Looking for file " + allowed_path)
                if os.path.isfile(allowed_path):
                    logging.debug("Adding file " + allowed_path)
                    tests_to_run.append(TestFile(test_dir, allowed_path))
                    added_test = True
        return sorted(tests_to_run, key = lambda x: x.test_path)

class LogicalTestSet(TestSet):
    def __init__(self, ds_name, root_dir, config_name, tds_name, exclusions, test_pattern, suite, password_file='',
                 expected_message='', smoke_test=False, test_is_enabled=True, test_is_skipped=False):
        super(LogicalTestSet, self).__init__(ds_name, root_dir, config_name, tds_name, exclusions, test_pattern, True,
                                             suite, password_file, expected_message, smoke_test, test_is_enabled,
                                             test_is_skipped)

    def get_expected_output_file_path(self, test_file, output_dir):
        existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(test_file, output_dir)
        return existing_output_filepath

    def get_actual_and_base_file_path(self, test_file, output_dir):
        existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(test_file, output_dir)
        return actual_output_filepath, base_filepath

class ExpressionTestSet(TestSet):
    def __init__(self, ds_name, root_dir, config_name, tds_name, exclusions, test_pattern, suite, password_file='',
                 expected_message='', smoke_test=False, test_is_enabled=True, test_is_skipped=False):
        super(ExpressionTestSet, self).__init__(ds_name, root_dir, config_name, tds_name,
                                                exclusions, test_pattern, False, suite, password_file, expected_message,
                                                smoke_test, test_is_enabled, test_is_skipped)

    def get_expected_output_file_path(self, test_file, output_dir):
        base_test_file = get_base_test(test_file)
        test_file_root = os.path.split(test_file)[0]
        existing_output_filepath, actual_diff_file, setup, expected_files, next_path = get_test_file_paths(test_file_root, base_test_file, output_dir)
        return existing_output_filepath

class SingleLogicalTestSet(LogicalTestSet):
    def __init__(self, ds_name, root_dir, test_pattern, tds_pattern, exclude_pattern, ds_info, password_file='',
                 expected_message='', smoke_test=False, test_is_enabled=True, test_is_skipped=False):
        super(SingleLogicalTestSet, self).__init__(ds_name, root_dir, 'temp' + ds_info.dsname, tds_pattern,
                                                   exclude_pattern, test_pattern, ds_info.dsname,
                                                   password_file, expected_message, smoke_test, test_is_enabled,
                                                   test_is_skipped)
        self.test_pattern = self.test_pattern.replace('?', ds_info.logical_config_name)
        self.tds_name = tds_pattern.replace('*', ds_info.dsname)

class SingleExpressionTestSet(ExpressionTestSet):
    def __init__(self, ds_name, root_dir, test_pattern, tds_pattern, exclude_pattern, ds_info, password_file='',
                 expected_message='', smoke_test=False, test_is_enabled=True, test_is_skipped=False):
        super(SingleExpressionTestSet, self).__init__(ds_name, root_dir, 'temp' + ds_info.dsname, tds_pattern,
                                                      exclude_pattern, test_pattern, ds_info.dsname,
                                                      password_file, expected_message, smoke_test, test_is_enabled,
                                                      test_is_skipped)
        self.tds_name = tds_pattern.replace('*', ds_info.dsname)

def build_config_name(prefix, dsname):
    return prefix + dsname + '.cfg'

def build_tds_name(prefix, dsname):
    return prefix + dsname + '.tds'

class RunTimeTestConfig(object):
    """
        Tracks specifics about how a group of tests were run.
    """
    def __init__(self, timeout_seconds=60*60, maxthread=0, d_override='', run_as_perf=False):
        self.timeout_seconds = timeout_seconds
        self.d_override = d_override
        self.run_as_perf = run_as_perf
        self.maxthread = int(maxthread)
        self.tabquery_paths = None

    def set_tabquery_paths(self, linux_path, mac_path, windows_path):
        if not linux_path and not mac_path and not windows_path:
            return
        self.tabquery_paths = TabQueryPath(linux_path, mac_path, windows_path)

    def set_tabquery_path_from_array(self, path_list):
        if not path_list:
            return
        self.tabquery_paths = TabQueryPath.from_array(path_list)

    def has_customized_tabquery_path(self):
        return self.tabquery_paths is not None

class TestConfig(object):
    """
        Defines all the tests that can be run for a single data source. An organized collection of TestSet objects.
    """
    def __init__(self, dsname, logical_config_name, run_time_config=None):
        self.dsname = dsname
        self.logical_config_name = logical_config_name
        self.calcs_tds = self.get_tds_name('cast_calcs.')
        self.staples_tds = self.get_tds_name('Staples.')
        self.logical_test_set = []
        self.expression_test_set = []
        self.smoke_test_set = []
        self.logical_config = {}
        self.run_time_config = run_time_config

    def get_config_name(self, prefix):
        return prefix + self.dsname

    def get_logical_test_path(self, prefix):
        return prefix + self.logical_config_name + '.xml'

    def get_tds_name(self, prefix):
        if prefix[-4:] == '.tds':
            return prefix
        return prefix + self.dsname + '.tds'

    def get_pasword_file_name(self):
        return self.dsname + ".password"

    def add_logical_test(self, base_config_name, tds_name, exclusions, test_path, test_dir, password_file,
                         expected_message, smoke_test, test_is_enabled, test_is_skipped):
        new_test = LogicalTestSet(self.dsname, test_dir, self.get_config_name(base_config_name), self.get_tds_name(tds_name),
                                  exclusions, test_path, self.dsname, password_file, expected_message, smoke_test,
                                  test_is_enabled, test_is_skipped)
        self.add_logical_testset(new_test)

    def add_logical_testset(self, new_test):
        self.logical_test_set.append(new_test)

    def add_expression_test(self, base_config_name, tds_name, exclusions, test_path, test_dir, password_file,
                            expected_message, smoke_test, test_is_enabled, test_is_skipped):
        new_test = ExpressionTestSet(self.dsname, test_dir, self.get_config_name(base_config_name), self.get_tds_name(tds_name),
                                     exclusions, test_path, self.dsname, password_file, expected_message, smoke_test,
                                     test_is_enabled, test_is_skipped)
        self.add_expression_testset(new_test)

    def add_expression_testset(self, new_test):
        self.expression_test_set.append(new_test)

    def get_logical_tests(self, config_filter=None):
        return self.logical_test_set if not config_filter  or config_filter == '*' else [ ts for ts in self.logical_test_set if config_filter in ts.config_name ]  # noqa: E501

    def get_expression_tests(self, config_filter=None):
        return self.expression_test_set if not config_filter or config_filter == '*' else [ ts for ts in self.expression_test_set if config_filter in ts.config_name ]  # noqa: E501

    def add_logical_config(self, cfg):
        self.logical_config = cfg.copy()

    def __str__(self):
        msg = ''
        for test in self.get_logical_tests() + self.get_expression_tests():
            msg += str(test) + "\n"
        return msg
