""" Test result and configuration related classes. """

import sys
from typing import Optional

from .test_config import TestConfig, RunTimeTestConfig


class TdvtInvocation(object):
    """Track how items were tested. This captures how tdvt was invoked."""

    def __init__(self, from_args=None, from_json=None, test_config: TestConfig = None):
        self.tested_sql = False
        self.tested_tuples = True
        self.tested_error = False
        self.log_dir = ''
        self.output_dir = ''
        self.custom_output_dir = ''
        self.timeout_seconds = 60 * 60
        self.logical = False
        self.config_file = ''
        self.suite_name = ''
        self.d_override = ''
        self.verbose = False
        self.command_line = ''
        self.noheader = False
        self.thread_count = 6
        self.leave_temp_dir = False
        self.run_as_perf = False
        self.thread_id = -1
        self.tds = ''
        self.tested_run_time_config = None
        self.tabquery_path = ''
        self.iteration: int = 0
        self.generate_expected = False
        self.schema_name: Optional[str] = None
        self.loose_comparison = False

        if from_args:
            self.init_from_args(from_args)
        if from_json:
            self.init_from_json(from_json)
        if test_config:
            self.set_run_time_test_config(test_config.run_time_config)
            self.suite_name = test_config.dsname

    def set_run_time_test_config(self, rtt: RunTimeTestConfig):
        self.timeout_seconds = rtt.timeout_seconds
        self.d_override = rtt.d_override
        self.run_as_perf = rtt.run_as_perf or self.run_as_perf
        self.schema_name = rtt.schema_name
        self.tested_run_time_config = rtt
        if rtt.tabquery_paths:
            self.tabquery_path = rtt.tabquery_paths.to_array()

    def init_from_args(self, args):
        if args.compare_sql:
            self.tested_sql = args.compare_sql
        if args.nocompare_tuples:
            self.tested_tuples = False
        if args.compare_error:
            self.tested_error = True
        if args.noclean:
            self.leave_temp_dir = True
        if args.verbose:
            self.verbose = args.verbose
        if args.custom_output_dir:
            self.custom_output_dir = args.custom_output_dir
        if args.perf_run:
            self.run_as_perf = True
        if args.perf_iteration:
            self.iteration = args.perf_iteration
        if args.generate_expected:
            self.generate_expected = True
        if args.loose_comparison:
            self.loose_comparison = True


    def init_from_json(self, json):
        self.tested_sql = json.get('tested_sql', self.tested_sql)
        self.tested_tuples = json.get('tested_tuples', self.tested_tuples)
        self.tested_error = json.get('tested_error', self.tested_error)
        self.output_dir = json.get('output_dir', self.output_dir)
        self.logical = json.get('logical', self.logical)
        self.config_file = json.get('config_file', self.config_file)
        self.suite_name = json.get('suite_name', self.suite_name)
        self.d_override = json.get('d_override', self.d_override)
        self.verbose = json.get('verbose', self.verbose)
        self.tds = json.get('tds', self.tds)
        self.noheader = json.get('noheader', self.noheader)
        if 'tabquery_path' in json:
            rtt = RunTimeTestConfig()
            rtt.set_tabquery_path_from_array(self.tabquery_path)
            self.tested_run_time_config = rtt
        self.thread_count = json.get('thread_count', self.thread_count)
        self.loose_comparison = json.get('loose_comparison', self.loose_comparison)

    def __str__(self):
        return ("suite [{}]: tested sql [{}]: tested tuples [{}]: tested error [{}]: output dir [{}]: " +
                "logical [{}]: config file [{}]: override [{}]: tds [{}]: thread [{}], loose comparison [{}]").format(
                self.suite_name, self.tested_sql, self.tested_tuples, self.tested_error, self.output_dir,
                self.logical, self.config_file, self.d_override, self.tds, self.thread_count, self.loose_comparison)

    def __json__(self):
        return {
            'tested_sql': self.tested_sql,
            'tested_tuples': self.tested_tuples,
            'tested_error': self.tested_error,
            'output_dir': self.output_dir,
            'logical': self.logical,
            'config_file': self.config_file,
            'suite_name': self.suite_name,
            'd_override': self.d_override,
            'verbose': self.verbose,
            'tds': self.tds,
            'noheader': self.noheader,
            'tabquery_path': self.tabquery_path,
            'thread_count': self.thread_count,
            'loose_comparison': self.loose_comparison}

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False
