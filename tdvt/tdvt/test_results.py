""" Test result and configuration related classes. """

import math
import json
import re

from .config_gen.tdvtconfig import TdvtInvocation
from .config_gen.test_config import TestSet

TEST_DISABLED = "Test disabled in .ini file."
TEST_SKIPPED = "Test not run because smoke tests failed."
TEST_NOT_RUN = "Not run"

class TestMetadata(object):
    """Simple struct containing lists of categories and functions tested for a single test"""
    def __init__(self, priority):
        self.categories = set()
        self.functions = set()
        self.priority = priority

    def add_category(self, category):
        if category:
            self.categories.add(category)

    def add_function(self, function):
        if function:
            self.functions.add(function)

    def concat_categories(self):
        return ','.join(self.categories)

    def concat_functions(self):
        return ','.join(self.functions)

    def get_priority(self):
        return self.priority

class TestCaseResult(object):
    """The actual or expected results of a test run.

        ie The math.round test contains ROUND(int), ROUND(num) etc test cases.

    """
    def __init__(self, name, id, sql, query_time, error_msg, error_type, table, test_config, test_metadata):
        self.name = name
        self.id = id
        self.sql = sql
        self.table = table
        self.execution_time = query_time
        self.error_message = error_msg
        self.error_type: TestErrorState = error_type
        self.diff_count = 0
        self.diff_string = ''
        self.passed_sql = False
        self.passed_tuples = False
        self.passed_error = False
        self.tested_config = test_config
        self.test_metadata = test_metadata

    def set_diff(self, diff_string, diff_count):
        self.diff_string = diff_string
        self.diff_count = diff_count

    def get_sql_text(self):
        return self.sql

    def get_tuples(self):
        tuple_list = []
        tuples = self.table.findall('tuple') if self.table else None
        if not tuples:
            return tuple_list
        for t in tuples:
            for v in t.findall('value'):
                tuple_list.append(v.text)

        return tuple_list

    def get_error_message(self):
        if self.error_message:
            return self.error_message

        if not self.all_passed() and isinstance(self.error_type, TestErrorResults):
            return 'Actual does not match expected.'

        return ''

    def test_error_expected(self):
        if isinstance(self.error_type, (TestErrorExpected, TestErrorDisabledTest, TestErrorSkippedTest)):
            return True
        else:
            return False

    def test_error_other(self):
        if isinstance(self.error_type, TestErrorOther):
            return True
        else:
            return False

    def all_passed(self):
        """Return true if all aspects of the test passed."""
        if self.test_error_expected() and self.error_type:
            return True

        passed = True
        if self.tested_config.tested_sql and not self.passed_sql:
            passed = False
        if self.tested_config.tested_tuples and not self.passed_tuples:
            passed = False
        if self.tested_config.tested_error and not self.passed_error:
            passed = False

        return passed

    def is_skipped(self):
        return isinstance(self.error_type, TestErrorSkippedTest)

    def is_disabled(self):
        return isinstance(self.error_type, TestErrorDisabledTest)

    def table_to_json(self):
        json_str = 'tuple'
        tuple_list = []
        tuples = self.table.findall('tuple') if self.table else None
        if tuples:
            for t in tuples:
                for v in t.findall('value'):
                    tuple_list.append(v.text)

        return {'tuples': tuple_list}

    def __json__(self):
        return {'tested_sql': self.tested_config.tested_sql, 'tested_tuples': self.tested_config.tested_tuples,
            'tested_error': self.tested_config.tested_error, 'id': self.id, 'name': self.name,
            'sql': self.get_sql_text(), 'table': self.table_to_json()}


class TestErrorState(object):
    """The cause of a test failure."""

    def __init__(self):
        pass

    def get_error(self):
        pass


class TestErrorAbort(TestErrorState):
    def get_error(self):
        return "Test was aborted."


class TestErrorStartup(TestErrorState):
    def get_error(self):
        return "Test did not start."


class TestErrorNotRun(TestErrorState):
    def get_error(self):
        return "Test did not run."


class TestErrorTimeout(TestErrorState):
    def get_error(self):
        return "Test timed out."


class TestErrorOther(TestErrorState):
    def get_error(self):
        return "Error."


class TestErrorExpected(TestErrorState):
    def get_error(self):
        return "Error is expected."


class TestErrorMissingActual(TestErrorState):
    def get_error(self):
        return "No actual file."


class TestErrorDisabledTest(TestErrorState):
    def get_error(self):
        return "Test disabled in .ini file."


class TestErrorResults(TestErrorState):
    def get_error(self):
        return "Actual does not match expected."


class TestErrorSkippedTest(TestErrorState):
    def get_error(self):
        return "Test not run because smoke tests failed."


class TestResult(object):
    """Information about a test run. A test can contain one or more test cases."""

    def __init__(self, base_name='', test_config=TdvtInvocation(), test_file='', relative_test_file='', test_set: TestSet = None, error_status=None, test_metadata: TestMetadata = None):
        self.name = base_name
        self.test_config = test_config
        self.matched_expected_version = 0
        self.error_status = error_status
        self.saved_error_message = None
        self.diff_count = 0
        self.best_matching_expected_results = None
        self.test_file = test_file
        self.path_to_expected = ''
        self.path_to_actual = ''
        self.overall_error_message = ''
        self.test_case_map = []
        self.cmd_output = ''
        self.relative_test_file = relative_test_file
        self.test_set: TestSet = test_set
        self.test_metadata = test_metadata

        self.parse_default_test_cases()

    def return_testcaseresult_for_not_run_tests(self, test_case_count=None):
        # TestCaseResult error messages should be specific to that exact test case. Overall test problems should be
        # set at a higher level (TestResult).
        if self.test_set.test_is_enabled is False:
            if self.test_set.is_logical:
                return TestCaseResult('', 0, "", 0, '', TestErrorDisabledTest(), None, self.test_config, self.test_metadata)
            else:
                return TestCaseResult('', str(test_case_count), "", test_case_count, '',
                                      TestErrorDisabledTest(), None, self.test_config)
        elif self.test_set.test_is_skipped is True:
            if self.test_set.is_logical:
                return TestCaseResult('', 0, "", 0, '', TestErrorSkippedTest(), None, self.test_config, self.test_metadata)
            else:
                return TestCaseResult('', str(test_case_count), "", test_case_count, '',
                                      TestErrorSkippedTest(), None, self.test_config, self.test_metadata)
        else:

            if self.test_set.is_logical:
                return TestCaseResult('', 0, "", 0, '', self.error_status, None, self.test_config, self.test_metadata)
            else:
                return TestCaseResult('', str(test_case_count), "", test_case_count, '',
                                      self.error_status, None, self.test_config, self.test_metadata)

    def parse_default_test_cases(self):
        if self.test_set and self.test_set.test_is_enabled is False:
            self.overall_error_message = TEST_DISABLED
        elif self.test_set and self.test_set.test_is_skipped is True:
            self.overall_error_message = TEST_SKIPPED
        else:
            self.overall_error_message = TEST_NOT_RUN

        # If it is an expression test with no results, it probably means the test failed and the individual test cases
        # weren't run. Count them here. Parse the setup file to get the count.
        if not self.test_case_map and self.test_set:
            if self.test_set.is_logical:
                test_result = self.return_testcaseresult_for_not_run_tests()
                self.test_case_map.append(test_result)
            else:
                reg_blank = re.compile('^\s*$')
                reg_comment = re.compile('^\s*//.*')
                try:
                    with open(self.test_file, 'r') as test_file:
                        test_case_count = 0
                        for line in test_file.readlines():
                            if not re.match(reg_blank, line) and not re.match(reg_comment, line):
                                test_result = self.return_testcaseresult_for_not_run_tests(
                                    test_case_count)
                                self.test_case_map.append(test_result)
                                test_case_count += 1
                except IOError:
                    pass

    def __json__(self):
        return {'all_passed': self.all_passed(), 'name': self.name,
                'matched_expected': self.matched_expected_version, 'expected_diffs': self.diff_count,
                'test_cases': self.test_case_map, 'expected_results': self.best_matching_expected_results,
                'priority': self.test_metadata.get_priority(), 'functions': self.test_metadata.concat_functions(),
                'categories': self.test_metadata.concat_categories()}

    def add_test_results(self, test_xml, actual_path):
        """
            <results>
            <test name='blah'>
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
            </test>
            </results>

        """
        self.path_to_actual = actual_path
        # Go through all the test nodes under 'results'.
        if not test_xml:
            return

        temp_test_cases = []
        for i in range(0, len(list(test_xml))):
            test_child = test_xml[i]

            node = test_child.find('error')
            error_msg = node.text if node is not None else ''

            node = test_child.find('error-type')
            error_type = node.text.strip() if node is not None else ''

            node = test_child.find('query-time')
            query_time = 0
            try:
                query_time = float(node.text if node is not None else '0')
            except ValueError:
                pass

            node = test_child.find('sql')
            sq = node.text if node is not None else ''

            test_child_name = test_child.get('name')
            if not test_child_name:
                continue
            test_result = TestCaseResult(test_child_name, str(
                i), sq, query_time, error_msg, error_type, test_child.find('table'), self.test_config, self.test_metadata)
            temp_test_cases.append(test_result)

        if temp_test_cases:
            # Clear any dummy place holders.
            self.test_case_map = temp_test_cases

    def get_failure_message_or_all_exceptions(self):
        msg = ''
        for case in self.test_case_map:
            if case.get_error_message():
                msg += case.get_error_message() + '\n'

        if msg and not msg.isspace():
            return msg

        return self.get_failure_message()

    def get_error_type(self):
        if self.error_status:
            return self.error_status.get_error()
        return "None"

    def get_failure_message(self):
        if self.saved_error_message:
            return self.saved_error_message

        if self.error_status:
            return self.error_status.get_error()

        # TODO need this?
        if self.overall_error_message:
            return self.overall_error_message

        return "No results found."

    def get_exceptions(self):
        if self.error_status:
            return []
        return [tc.error_type for tc in self.test_case_map if not tc.all_passed() and tc.error_type]

    def set_diff_counts(self, diff_counts):
        if len(diff_counts) != len(self.test_case_map):
            return
        for i in range(0, len(self.test_case_map)):
            self.test_case_map[i].diff_count = diff_counts[i]

    def set_best_matching_expected_output(self, expected_output, expected_path, expected_number, diff_counts):
        diff_count = sum(diff_counts)
        if self.best_matching_expected_results is None or self.diff_count > diff_count:
            self.best_matching_expected_results = expected_output
            self.matched_expected_version = expected_number
            self.set_diff_counts(diff_counts)
            self.diff_count = diff_count
            self.path_to_expected = expected_path

    def get_name(self):
        """Chop off the end of the test file (extension) when getting the name."""
        regex = re.compile('setup\.(.*)\.[a-zA-Z]{3}')
        match = re.match(regex, self.name)
        if not match:
            return self.name
        return match.group(1)

    def test_error_expected(self):
        if isinstance(self.error_status, TestErrorExpected):
            return True
        else:
            return False

    def test_error_other(self):
        if isinstance(self.error_status, TestErrorOther):
            return True
        else:
            return False

    def all_passed(self):
        """Return true if all aspects of the test passed."""
        if self.test_error_expected():
            return True
        elif self.test_error_other() or not self.test_case_map:
            return False
        for test_case in self.test_case_map:
            if test_case.all_passed() == False:
                return False
        return True

    def get_total_execution_time(self):
        """Time to run all test cases."""
        total_query_time = 0
        for tc in self.test_case_map:
            total_query_time += tc.execution_time
        return total_query_time

    def get_failure_count(self):
        failures = 0
        for test_case in self.test_case_map:
            if test_case.all_passed() == False:
                failures += 1

        return failures

    def get_disabled_count(self):
        disabled = 0
        for test_case in self.test_case_map:
            if test_case.error_type and isinstance(test_case.error_type, TestErrorDisabledTest):
                disabled += 1

        return disabled

    def get_skipped_count(self):
        skipped = 0
        for test_case in self.test_case_map:
            if test_case.error_type and isinstance(test_case.error_type, TestErrorSkippedTest):
                skipped += 1

        return skipped

    def get_test_case_count(self):
        return len(self.test_case_map) if self.test_case_map else 0

    def get_test_case(self, index):
        case = None
        try:
            case = self.test_case_map[index]
        except IndexError:
            pass

        return case

    def diff_test_results(self, expected_output: 'TestResult'):
        """Compare the actual results to the expected test output based on the given rules."""

        test_case_count = self.get_test_case_count()
        diff_counts = [0] * test_case_count
        diff_string = ''
        # Go through all test cases.
        for test_case in range(0, test_case_count):
            expected_testcase_self = expected_output.get_test_case(test_case)
            actual_testcase_self = self.get_test_case(test_case)
            if not actual_testcase_self:
                continue
            if expected_testcase_self is None:
                actual_testcase_self.passed_sql = False
                actual_testcase_self.passed_tuples = False
                actual_testcase_self.passed_error = False
                continue

            config = self.test_config
            # Compare the SQL.
            if config.tested_sql:
                diff, diff_string = self.diff_sql_node(
                    actual_testcase_self.sql, expected_testcase_self.sql, diff_string)
                actual_testcase_self.passed_sql = diff == 0
                diff_counts[test_case] = diff

            # Compare the tuples.
            if config.tested_tuples:
                diff, diff_string = self.diff_table_node(actual_testcase_self.table, expected_testcase_self.table,
                                                         diff_string, expected_testcase_self.name)
                actual_testcase_self.passed_tuples = diff == 0
                diff_counts[test_case] = diff

            # Compare the error.
            if config.tested_error:
                diff, diff_string = self.diff_error_node(
                    actual_testcase_self.error_message, expected_testcase_self.error_message, diff_string)
                actual_testcase_self.passed_error = diff == 0
                diff_counts[test_case] = diff

        self.diff_string = diff_string
        return diff_counts, diff_string

    def diff_table_node(self, actual_table, expected_table, diff_string, test_name):
        if actual_table == None or expected_table == None:
            return (-1, diff_string)

        actual_tuples = actual_table.findall('tuple')
        expected_tuples = expected_table.findall('tuple')

        if actual_tuples == None and expected_tuples == None:
            return (0, diff_string)

        diff_string += "\nTuples - " + test_name + "\n"
        if actual_tuples == None or expected_tuples == None:
            diff_string += "\tTuples do not exist for one side.\n"
            return (math.fabs(len(actual_tuples) - len(expected_tuples)), diff_string)

        # Compare all the values for the tuples.
        if len(actual_tuples) != len(expected_tuples):
            diff_string += "\tDifferent number of tuples.\n"

        if not len(actual_tuples):
            diff_string += "\tNo 'actual' file tuples.\n"

        diff_count = 0

        expected_tuple_list = []
        for j in expected_tuples:
            for k in j.findall('value'):
                expected_tuple_list.append(k.text)

        actual_tuple_list = []
        for j in actual_tuples:
            for k in j.findall('value'):
                actual_tuple_list.append(k.text)

        diff_count = sum(a != b for a, b in zip(
            actual_tuple_list, expected_tuple_list))
        diff_count += abs(len(actual_tuple_list) - len(expected_tuple_list))

        for a, b in zip(actual_tuple_list, expected_tuple_list):
            if a != b:
                diff_string += "\t <<<< >>>> \n"
                diff_string += "\tactual: " + a + "\n"
                diff_string += "\texpected: " + b + "\n"

        return (diff_count, diff_string)

    def diff_sql_node(self, actual_sql, expected_sql, diff_string):
        if actual_sql == None and expected_sql == None:
            return (0, diff_string)

        diff_string += "SQL\n"
        if actual_sql == None or expected_sql == None or (actual_sql != expected_sql):
            diff_string += "<<<<\n" + actual_sql + "\n"
            diff_string += ">>>>\n" + expected_sql + "\n"
            return (1, diff_string)

        return (0, diff_string)

    def diff_error_node(self, actual_error, expected_error, diff_string):
        if actual_error == None and expected_error == None:
            return (0, diff_string)

        diff_string += "Error\n"
        if actual_error == None or expected_error == None or (expected_error not in actual_error):
            diff_string += "<<<<\n" + actual_error + "\n"
            diff_string += ">>>>\n" + expected_error + "\n"
            return (1, diff_string)

        return (0, diff_string)


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
        test_name = '' if not obj.get_name() else obj.get_name()
        test_type = '-q' if obj.test_config.logical else '-e'
        if obj.test_config.logical:
            test_cases = test_name
        else:
            test_cases = test_name
            if obj.test_case_map:
                joined_cases = ",".join(
                    sorted([x.name for x in obj.test_case_map if not x.all_passed()]))
                if joined_cases:
                    test_cases = test_name + ":" + joined_cases

            if not test_cases:
                test_cases = test_name

        json_output = {'suite': suite_name,
                       'class': 'TDVT',
                       'test_name': suite_name + '.' + test_name,
                       'duration': obj.get_total_execution_time(),
                       'expected_message': obj.test_set.get_expected_message(),
                       'case': test_cases,
                       'test_file': obj.relative_test_file,
                       'test_type': test_type,
                       'test_config': obj.test_config.__json__(),
                       'tds': obj.test_config.tds,
                       'password_file': obj.test_set.password_file,
                       'expected': obj.path_to_expected,
                       'priority': obj.test_metadata.get_priority() if obj.test_metadata else 'unknown',
                       'functions': obj.test_metadata.concat_functions() if obj.test_metadata else 'unknown',
                       'categories': obj.test_metadata.concat_categories() if obj.test_metadata else 'unknown'
                       }
        if obj.all_passed():
            return json_output

        failtype = ','.join(obj.get_exceptions())
        json_output['failtype'] = failtype if failtype else 'test_failure'
        json_output['message'] = obj.get_failure_message_or_all_exceptions()
        json_output['actual'] = obj.path_to_actual
        return json_output
