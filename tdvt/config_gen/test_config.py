"""
    TestConfig defines how to run tests with TDVT runner.

"""

import os
import tempfile
from ..resources import *

class TestSet(object):
    """
        Represents everything needed to run a set of tests. This includes a path to the test files, which tds etc.
    """
    def __init__(self, config_file_name, tds_name, exclusions, allow_pattern):
        self.config_file_name = config_file_name
        self.tds_name = tds_name
        self.exclusions = exclusions
        self.allow_pattern = allow_pattern

    def __str__(self):
        return "[name={0}] [tds={1}] [exclusions={2}] [test pattern={3}]".format(self.config_file_name, self.tds_name, self.exclusions, self.allow_pattern)
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

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
        return prefix + self.dsname + '.cfg'

    def get_logical_test_path(self, prefix):
        return prefix + self.logical_config_name + '.xml'

    def get_tds_name(self, prefix):
        if prefix[-4:] == '.tds':
            return prefix
        return prefix + self.dsname + '.tds'

    def add_logical_test(self, base_config_name, tds_name, exclusions, test_path):
        new_test = TestSet(self.get_config_name(base_config_name), self.get_tds_name(tds_name), exclusions, test_path)
        self.add_logical_testset(new_test)

    def add_logical_testset(self, new_test):
        self.logical_test_set.append(new_test)

    def add_expression_test(self, base_config_name, tds_name, exclusions, test_path):
        new_test = TestSet(self.get_config_name(base_config_name), self.get_tds_name(tds_name), exclusions, test_path)
        self.add_expression_testset(new_test)

    def add_expression_testset(self, new_test):
        self.expression_test_set.append(new_test)

    def get_logical_tests(self, config_filter=None):
        return self.logical_test_set if not config_filter else [ ts for ts in self.logical_test_set if config_filter in ts.config_file_name ]
    
    def get_expression_tests(self, config_filter=None):
        return self.expression_test_set if not config_filter else [ ts for ts in self.expression_test_set if config_filter in ts.config_file_name ]

    def config_files_exist(self, root_dir):
        all_cfg = [x.config_file_name for x in (self.logical_test_set + self.expression_test_set)]
        for f in all_cfg:
            if not os.path.exists(os.path.join(root_dir, f)):
                return False
        return True

    def add_logical_config(self, cfg):
        self.logical_config = cfg.copy()

    def write_config_files(self, root_dir):
        for test in self.logical_test_set + self.expression_test_set:
            self.write_config_file(test.config_file_name, root_dir, test.allow_pattern, test.exclusions)

    def write_config_file(self, name, dir, allow, exclude):
        filename = os.path.join(dir, name)
        f = open(get_path('config/gen/', name), 'w')
        f.write('allow:\n')
        f.write(allow + '\n')
        if len(exclude) > 0:
            f.write('\nexclude:\n')
            for exclude_pattern in exclude.split(','):
                f.write(exclude_pattern + '\n')
        f.close()

    def __str__(self):
        msg = ''
        for test in self.get_logical_tests() + self.get_expression_tests():
            msg += str(test) + "\n"
        return msg

class SingleTestConfig(object):
    """Maintain information about running a single test. This is different that running a test suite which has a premade config file."""
    def __init__(self, test_pattern, tds_pattern, exclude_pattern, ds_name):
        self.valid = False
        self.ds_name = ds_name
        self.test_pattern = test_pattern
        self.tds_pattern = tds_pattern
        self.tds_name = self.tds_pattern.replace('*', ds_name)
        self.exclude_pattern = exclude_pattern

    def write_cfg(self):
        if self.test_pattern and self.tds_pattern:
            try:
                fd, tmppath = tempfile.mkstemp(suffix='.cfg')
                tmpcfg = open(tmppath, 'w')
                tmpcfg.write("allow:\n")
                tmpcfg.write(self.test_pattern)
                tmpcfg.write("\n")
                if self.exclude_pattern:
                    tmpcfg.write("exclude:\n")
                    tmpcfg.write(self.exclude_pattern)
                    tmpcfg.write("\n")
                tmpcfg.close()
                os.close(fd)
            except IOError:
                return

            self.temp_cfg_path = tmppath
            self.valid = True

    def __del__(self):
        if not self.valid:
            return
        try:
            os.remove(self.temp_cfg_path)
        except OSError:
            pass

class SingleLogicalTestConfig(SingleTestConfig):
    def __init__(self, test_pattern, tds_pattern, exclude_pattern, ds_info):
        super(SingleLogicalTestConfig, self).__init__(test_pattern, tds_pattern, exclude_pattern, ds_info.dsname)
        self.test_pattern = self.test_pattern.replace('?', ds_info.logical_config_name)
        super(SingleLogicalTestConfig, self).write_cfg()

class SingleExpressionTestConfig(SingleTestConfig):
    def __init__(self, test_pattern, tds_pattern, exclude_pattern, ds_info):
        super(SingleExpressionTestConfig, self).__init__(test_pattern, tds_pattern, exclude_pattern, ds_info.dsname)
        super(SingleExpressionTestConfig, self).write_cfg()
    pass

