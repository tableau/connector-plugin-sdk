""" Test result and configuration related classes. """

import json
import re

from .config_gen.tdvtconfig import TdvtTestConfig


class TestCaseResult(object):
    """The actual or expected results of a test run.

        ie The math.round test contains ROUND(int), ROUND(num) etc test cases.

    """
    def __init__(self, name, id, sql, query_time, error_msg, error_type, table, test_config):
        self.name = name
        self.id = id
        self.sql = sql
        self.table = table
        self.execution_time = query_time
        self.error_message = error_msg
        self.error_type = error_type
        self.diff_count = 0
        self.diff_string = ''
        self.passed_sql = False
        self.passed_tuples = False
        self.tested_config = test_config

    def set_diff(self, diff_string, diff_count):
        self.diff_string = diff_string
        self.diff_count = diff_count

    def get_sql_text(self):
        return self.sql

    def get_tuples(self):
        tuple_list = []
        tuples = self.table.findall('tuple')
        for t in tuples:
            for v in t.findall('value'):
                tuple_list.append(v.text)

        return tuple_list

    def get_error_message(self):
        if self.error_message:
            return self.error_message

        if not self.all_passed():
            return 'Actual does not match expected.'

        return ''

    def test_error_expected(self):
        if isinstance(self.error_type, TestErrorExpected):
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
        passed = True
        if self.tested_config.tested_sql and not self.passed_sql:
            passed = False
        if self.tested_config.tested_tuples and not self.passed_tuples:
            passed = False
        if not self.test_error_expected() and self.error_type:
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


class TestResult(object):
    """Information about a test run. A test can contain one or more test cases."""
    def __init__(self, base_name = '', test_config = TdvtTestConfig(), test_file = '', relative_test_file = '', test_set = None):
        self.name = base_name
        self.test_config = test_config
        self.matched_expected_version = 0
        self.error_status = None
        self.saved_error_message = None
        self.diff_count = 0
        self.best_matching_expected_results = None
        self.test_file = test_file
        self.path_to_expected = ''
        self.path_to_actual = ''
        self.overall_error_message = ''
        self.test_case_map = []
        self.cmd_output = ''
        self.run_time_ms = 0
        self.relative_test_file = relative_test_file
        self.test_set = test_set

    def __json__(self):
        return {'all_passed' : self.all_passed(), 'name' : self.name,
                'matched_expected' : self.matched_expected_version, 'expected_diffs' : self.diff_count,
                'test_cases' : self.test_case_map, 'expected_results' : self.best_matching_expected_results}

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
        self.test_case_map = []
        self.path_to_actual = actual_path
        #Go through all the test nodes under 'results'.
        for i in range(0, len(list(test_xml))):
            test_child = test_xml[i]

            node= test_child.find('error')
            error_msg = node.text if node is not None else ''

            node = test_child.find('error-type')
            error_type = node.text.strip() if node is not None else ''

            node = test_child.find('query-time')
            query_time = node.text if node is not None else '0'

            node = test_child.find('sql')
            sq = node.text if node is not None else ''

            test_result = TestCaseResult(test_child.get('name'), str(i), sq, query_time, error_msg, error_type, test_child.find('table'), self.test_config)
            self.test_case_map.append(test_result)

    def get_failure_message_or_all_exceptions(self):
        msg = ''
        for case in self.test_case_map:
            if case.get_error_message():
                msg += case.get_error_message() + '\n'

        if msg:
            return msg

        return self.get_failure_message()

    def get_failure_message(self):
        if self.saved_error_message:
            return self.saved_error_message

        #TODO need this?
        if self.overall_error_message:
            return self.overall_error_message

        if self.error_status:
            return self.error_status.get_error()

        return "No results found."

    def get_exceptions(self):
        if self.error_status:
            return []
        return [ tc.error_type for tc in self.test_case_map if not tc.all_passed() and tc.error_type ]

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
        return self.run_time_ms

    def get_failure_count(self):
        failures = 0
        for test_case in self.test_case_map:
            if test_case.all_passed() == False:
                failures += 1

        return failures

    def get_test_case_count(self):
        return len(self.test_case_map) if self.test_case_map else 0

    def get_test_case(self, index):
        case = None
        try:
            case = self.test_case_map[index]
        except IndexError:
            pass

        return case

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
                joined_cases = ",".join(sorted([x.name for x in obj.test_case_map if not x.all_passed()]))
                if joined_cases:
                    test_cases = test_name + ":" + joined_cases

            if not test_cases:
                test_cases = test_name

        json_output = {'suite' : suite_name,
                'class' : 'TDVT',
                'test_name' : suite_name + '.' + test_name,
                'duration' : obj.get_total_execution_time(),
                'case' : test_cases,
                'test_file' : obj.relative_test_file,
                'test_type' : test_type,
                'test_config' : obj.test_config.__json__(),
                'tds' : obj.test_config.tds,
                'password_file' : obj.test_set.password_file,
                'expected' : obj.path_to_expected,
               }
        if obj.all_passed():
            return json_output

        failtype = ','.join(obj.get_exceptions())
        json_output['failtype'] = failtype if failtype else 'test_failure'
        json_output['message'] = obj.get_failure_message_or_all_exceptions()
        json_output['actual'] = obj.path_to_actual
        return json_output
