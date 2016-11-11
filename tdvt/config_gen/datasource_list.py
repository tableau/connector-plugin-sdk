# -----------------------------------------------------------------------------
# 
# This file is the copyrighted property of Tableau Software and is protected 
# by registered patents and other applicable U.S. and international laws and 
# regulations.
# 
# Unlicensed use of the contents of this file is prohibited. Please refer to 
# the NOTICES.txt file for further details.
# 
# -----------------------------------------------------------------------------

"""
    Register datasources for use with TDVT runner.

"""

import configparser
import glob
import os.path

from ..resources import *
from .test_config import TestConfig,TestSet,build_config_name,build_tds_name

def LoadTest(config):
    """ Parse a datasource test suite config into a TestConfig object.
    [Datasource]
    Name = bigquery
    LogicalQueryFormat = bool_
    CommandLineOverride =

    [StandardTests]
    LogicalExclusions_Calcs = 
    LogicalExclusions_Staples = Filter.Trademark
    ExpressionExclusions_Standard = string.char,dateparse

    [LODTests]
    LogicalExclusions_Staples = 
    ExpressionExclusions_Calcs = 

    [StaplesDataTest]

    [NewExpressionTest1]
    Name = expression_test_dates.
    TDS = cast_calcs.bigquery_sql_dates.tds
    Exclusions = string.ascii
    TestPath = exprtests/standard/ 
    
    """
    CALCS_TDS = 'cast_calcs.'
    STAPLES_TDS = 'Staples.'

    dsconfig = config['Datasource']
    test_config = TestConfig(dsconfig['Name'], dsconfig['LogicalQueryFormat'], dsconfig.get('CommandLineOverride', ''))

    #Add the standard test suites.
    try:
        standard = config['StandardTests']
        
        test_config.add_logical_test('logical.calcs.', CALCS_TDS, standard.get('LogicalExclusions_Calcs', ''), test_config.get_logical_test_path('logicaltests/setup/calcs/setup.*.'))
        test_config.add_logical_test('logical.staples.', STAPLES_TDS, standard.get('LogicalExclusions_Staples', ''), test_config.get_logical_test_path('logicaltests/setup/staples/setup.*.'))
        test_config.add_expression_test('expression_test.', CALCS_TDS, standard.get('ExpressionExclusions_Standard', ''), 'exprtests/standard/')
    except KeyError:
        pass

    #Add the optional LOD tests.
    try:
        lod = config['LODTests']
        test_config.add_logical_test('logical.lod.', STAPLES_TDS, lod.get('LogicalExclusions_Staples', ''), test_config.get_logical_test_path('logicaltests/setup/lod/setup.*.'))
        test_config.add_expression_test('expression.lod.', CALCS_TDS, lod.get('ExpressionExclusions_Calcs', ''), 'exprtests/lodcalcs/setup.*.txt')
    except KeyError:
        pass

    #Add the optional Staples data check test.
    try:
        staples_data = config['StaplesDataTest']
        test_config.add_expression_test('expression.staples.', STAPLES_TDS, '', 'exprtests/staples/setup.*.txt')
    except KeyError:
        pass

    #Add any extra expression tests.
    for section in config.sections():
        if 'NewExpressionTest' in section:
            try:
                sect = config[section]
                test_config.add_expression_test(sect.get('Name',''), sect.get('TDS',''), sect.get('Exclusions',''), sect.get('TestPath',''))
            except KeyError:
                pass

    #Add any extra logical tests.
    for section in config.sections():
        if 'NewLogicalTest' in section:
            try:
                sect = config[section]
                test_config.add_logical_test(sect.get('Name',''), sect.get('TDS',''), sect.get('Exclusions',''), sect.get('TestPath',''))
            except KeyError:
                pass

    return test_config
        

class TestRegistry(object):
    """Add a new datasource here and then add it to the appropriate registries below."""
    def __init__(self, ini_file):
        self.dsnames = {}
        self.suite_map = {}

        #Read all the datasource ini files and load the test configuration.
        ini_files = get_all_ini_files('config')
        for f in ini_files:
            config = configparser.ConfigParser()
            config.read(f)
            self.add_test(LoadTest(config))

        self.load_registry(ini_file)

    def load_registry(self, ini_file):
        try:
            #Create the test suites (groups of datasources to test)
            config = configparser.ConfigParser()
            config.read(get_ini_path('config/registry', 'tdvt'))
            ds = config['DatasourceRegistry']

            suite_all = self.interpret_ds_list(ds.get('all', ''))
            if suite_all:
                self.suite_map['all'] = suite_all
            suite_standard = self.interpret_ds_list(ds.get('standard', ''))
            if suite_standard:
                self.suite_map['standard'] = suite_standard
            suite_slow = self.interpret_ds_list(ds.get('slow', ''))
            if suite_slow:
                self.suite_map['slow'] = suite_slow

        except KeyError:
            #Create a simple default.
            self.suite_map['all'] = self.dsnames

    def interpret_ds_list(self, ds_list):
        if ds_list == '*':
            return [x for x in self.dsnames]
        return [x.strip() for x in ds_list.split(',')]

    def add_test(self, test_config):
        self.dsnames[test_config.dsname] = test_config

    def get_datasource_info(self, dsname):
        if dsname in self.dsnames:
            return self.dsnames[dsname]
        return None

    def get_datasources(self, suite):
        ds_to_run = []
        if not suite:
            return
        for ds in suite.split(','):
            ds = ds.strip()
            if ds in self.suite_map:
                ds_to_run.extend(self.suite_map[ds])
            elif ds:
                ds_to_run.append(ds)
        
        return ds_to_run

class WindowsRegistry(TestRegistry):
    """Windows specific test suites."""
    def __init__(self):
        super(WindowsRegistry, self).__init__('windows.ini')


class MacRegistry(TestRegistry):
    """Mac specific test suites."""
    def __init__(self):
        super(MacRegistry, self).__init__('mac.ini')

