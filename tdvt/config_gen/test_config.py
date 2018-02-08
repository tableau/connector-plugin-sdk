"""
    TestConfig defines how to run tests with TDVT runner.

"""

import os
import tempfile
from ..resources import *

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

class TestSet(object):
    """
        Represents everything needed to run a set of tests. This includes a path to the test files, which tds etc.
    """
    def __init__(self, config_name, tds_name, exclusions, allow_pattern, is_logical):
        self.config_name = config_name
        self.tds_name = tds_name
        self.exclusions = exclusions
        self.allow_pattern = allow_pattern
        self.is_logical = is_logical

    def get_exclusions(self):
        return [] if not self.exclusions else self.exclusions.split(',')

    def __str__(self):
        return "[name={0}] [tds={1}] [exclusions={2}] [test pattern={3}]".format(self.config_name, self.tds_name, self.exclusions, self.allow_pattern)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class LogicalTestSet(TestSet):
    def __init__(self, config_name, tds_name, exclusions, allow_pattern):
        super(LogicalTestSet, self).__init__(config_name, tds_name, exclusions, allow_pattern, True)
        
class ExpressionTestSet(TestSet):
    def __init__(self, config_name, tds_name, exclusions, allow_pattern):
        super(ExpressionTestSet, self).__init__(config_name, tds_name, exclusions, allow_pattern, False)

class SingleLogicalTestSet(LogicalTestSet):
    def __init__(self, test_pattern, tds_pattern, exclude_pattern, ds_info):
        super(SingleLogicalTestConfig, self).__init__('temp' + ds_info.dsname, tds_pattern, exclude_pattern, test_pattern)
        self.allow_pattern = self.allow_pattern.replace('?', ds_info.logical_config_name)
        self.tds_name = tds_pattern.replace('*', ds_info.dsname)

class SingleExpressionTestSet(ExpressionTestSet):
    def __init__(self, test_pattern, tds_pattern, exclude_pattern, ds_info):
        super(SingleExpressionTestConfig, self).__init__('temp' + ds_info.dsname, tds_pattern, exclude_pattern, test_pattern)
        self.tds_name = tds_pattern.replace('*', ds_info.dsname)

def build_config_name(prefix, dsname):
    return prefix + dsname + '.cfg'

def build_tds_name(prefix, dsname):
    return prefix + dsname + '.tds'

class TestConfig(object):
    """
        Defines all the tests that can be run for a single data source. An organized collection of TestSet objects.
    """
    def __init__(self, dsname, logical_config_name, maxthread, maxsubthread, d_override=''):
        self.dsname = dsname
        self.logical_config_name = logical_config_name
        self.calcs_tds = self.get_tds_name('cast_calcs.')
        self.staples_tds = self.get_tds_name('Staples.')
        self.logical_test_set = []
        self.expression_test_set = []
        self.d_override = d_override
        self.maxthread = 0
        self.logical_config = {}
        if int(maxthread) > 0:
            self.maxthread = int(maxthread)
        self.maxsubthread = 0
        if int(maxsubthread) > 0:
            self.maxsubthread = int(maxsubthread)

    def get_config_name(self, prefix):
        return prefix + self.dsname

    def get_logical_test_path(self, prefix):
        return prefix + self.logical_config_name + '.xml'

    def get_tds_name(self, prefix):
        if prefix[-4:] == '.tds':
            return prefix
        return prefix + self.dsname + '.tds'

    def add_logical_test(self, base_config_name, tds_name, exclusions, test_path):
        new_test = LogicalTestSet(self.get_config_name(base_config_name), self.get_tds_name(tds_name), exclusions, test_path)
        self.add_logical_testset(new_test)

    def add_logical_testset(self, new_test):
        self.logical_test_set.append(new_test)

    def add_expression_test(self, base_config_name, tds_name, exclusions, test_path):
        new_test = ExpressionTestSet(self.get_config_name(base_config_name), self.get_tds_name(tds_name), exclusions, test_path)
        self.add_expression_testset(new_test)

    def add_expression_testset(self, new_test):
        self.expression_test_set.append(new_test)

    def get_logical_tests(self, config_filter=None):
        return self.logical_test_set if not config_filter else [ ts for ts in self.logical_test_set if config_filter in ts.config_name ]
    
    def get_expression_tests(self, config_filter=None):
        return self.expression_test_set if not config_filter else [ ts for ts in self.expression_test_set if config_filter in ts.config_name ]

    def add_logical_config(self, cfg):
        self.logical_config = cfg.copy()

    def __str__(self):
        msg = ''
        for test in self.get_logical_tests() + self.get_expression_tests():
            msg += str(test) + "\n"
        return msg

