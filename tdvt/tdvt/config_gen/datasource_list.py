"""
    Register datasources for use with TDVT runner.

"""

import configparser
import glob
import os.path
import logging

from .gentests import list_configs, list_config
from ..resources import *
from .test_config import TestConfig, RunTimeTestConfig

RUN_IN_INCORRECT_DIRECTORY_MSG = "\nNo data sources found in this directory. To run tests, the base directory must contain a valid test configuration."


def print_ds(ds, ds_reg):
    print("\n\t" + ds)
    test_config = ds_reg.get_datasource_info(ds)
    if not test_config:
        return
    print("\tLogical tests:")
    for x in test_config.get_logical_tests():
        print("\t" * 2 + str(x))
        root_directory = get_root_dir()
        tests = x.generate_test_file_list()
        for test in tests:
            print("\t" * 3 + test.test_path)

    print("\tExpression tests:")
    for x in test_config.get_expression_tests():
        print("\t" * 2 + str(x))
        root_directory = get_root_dir()
        tests = x.generate_test_file_list()
        for test in tests:
            print("\t" * 3 + test.test_path)


def print_configurations(ds_reg, dsname, verbose):
    if not dsname or len(ds_reg.get_datasources(dsname)) == 0:
        try:
            ds_all = ds_reg.get_datasources(['all'])
        except TypeError as e:
            print(RUN_IN_INCORRECT_DIRECTORY_MSG)
            return
        if not ds_all:
            print(RUN_IN_INCORRECT_DIRECTORY_MSG)
            return
        print("\nAvailable datasources:")
        for ds in sorted(ds_all):
            print(ds)
        print("\nAvailable suites:")
        for suite in ds_reg.suite_map:
            print(suite)
            print("\t" + ', '.join(ds_reg.suite_map[suite]))
            print('\n')
        return

    ds_to_run = ds_reg.get_datasources(dsname)
    if len(ds_to_run) == 1:
        print_ds(ds_to_run[0], ds_reg)
    else:
        print("\nDatasource suite " + str(dsname) + " is " + ",".join(ds_to_run))
        if verbose:
            for ds in ds_to_run:
                print_ds(ds, ds_reg)



def get_password_file(config):
    return config.get('PasswordFile', '')


def get_expected_message(config):
    return config.get('ExpectedMessage', '')


def get_is_smoke_test(config):
    return config.get('SmokeTest', 'False') == 'True'


def get_is_test_enabled(config, key_name=None):
    if key_name:
        return config.get(key_name, 'True') == 'True'
    else:
        return config.get('Enabled', 'True') == 'True'


def print_logical_configurations(ds_registry, config_name=None):
    if config_name:
        for config in list_config(ds_registry, config_name):
            print(config)
    else:
        print("Available logical query configurations: \n")
        for config in list_configs(ds_registry):
            print(config)


def load_test(config, test_dir=get_root_dir()):
    """ Parse a datasource test suite config into a TestConfig object.
    [Datasource]
    Name = bigquery
    LogicalQueryFormat = bool_
    CommandLineOverride =
    TabQueryPath = [optional path to override tabquery locally.]

    [StandardTests]
    LogicalExclusions_Calcs =
    LogicalExclusions_Staples = Filter.Trademark
    ExpressionExclusions_Standard = string.char,dateparse

    [LODTests]
    LogicalExclusions_Staples =
    ExpressionExclusions_Calcs =

    [StaplesDataTest]

    [UnionTest]

    [MedianTests]

    [PercentileTests]

    [NewExpressionTest1]
    Name = expression_test_dates.
    TDS = cast_calcs.bigquery_sql_dates.tds
    Exclusions = string.ascii
    TestPath = exprtests/standard/

    [NewExpressionTest2]
    SmokeTest = True  # tests are treated as smoke tests if SmokeTest = True
    Enabled = False # If set to False, the test is marked `D`, not run, and counted as a fail.

    [LogicalConfig]
    Name = mydb_config
    key = value

    [ConnectionTests]
    CastCalcsTestEnabled = True  # by default these two values are True; set `False` if disabling a test.
    StaplesTestEnabled = False

    """
    CALCS_TDS = 'cast_calcs.'
    STAPLES_TDS = 'Staples.'

    standard_tests = 'StandardTests'
    lod_tests = 'LODTests'
    staples_data_test = 'StaplesDataTest'
    new_expression_test = 'NewExpressionTest'
    new_logical_test = 'NewLogicalTest'
    union_test = 'UnionTest'
    datasource_section = 'Datasource'
    regex_test = 'RegexTest'
    median_test = 'MedianTests'
    percentile_test = 'PercentileTests'
    logical_config = 'LogicalConfig'
    connection_test = 'ConnectionTests'

    KEY_EXCLUSIONS = 'Exclusions'

    # Check the ini sections to make sure there is nothing that is unrecognized. This should be empty by the time we are done.
    all_ini_sections = config.sections()

    # This is required.
    dsconfig = config[datasource_section]
    all_ini_sections.remove(datasource_section)
    config_name = dsconfig['Name']
    run_time_config = RunTimeTestConfig(
        dsconfig.getint('TimeoutSeconds', 60 * 60),
        dsconfig.get('MaxThread', '0'),
        dsconfig.get('CommandLineOverride', ''),
        dsconfig.getboolean('RunAsPerf', False)
    )
    run_time_config.set_tabquery_paths(
        dsconfig.get('TabQueryPathLinux', ''),
        dsconfig.get('TabQueryPathMac', ''),
        dsconfig.get('TabQueryPathx64', '')
    )
    test_config = TestConfig(config_name, dsconfig['LogicalQueryFormat'], run_time_config)


    # Add the standard test suites.
    if standard_tests in config.sections():
        try:
            standard = config[standard_tests]
            all_ini_sections.remove(standard_tests)

            test_config.add_logical_test('logical.calcs.', CALCS_TDS, standard.get('LogicalExclusions_Calcs', ''),
                                         test_config.get_logical_test_path('logicaltests/setup/calcs/setup.*.'),
                                         test_dir, get_password_file(standard), get_expected_message(standard),
                                         get_is_smoke_test(standard), get_is_test_enabled(standard), False)
            test_config.add_logical_test('logical.staples.', STAPLES_TDS, standard.get('LogicalExclusions_Staples', ''),
                                         test_config.get_logical_test_path('logicaltests/setup/staples/setup.*.'),
                                         test_dir, get_password_file(standard), get_expected_message(standard),
                                         get_is_smoke_test(standard), get_is_test_enabled(standard), False)
            test_config.add_expression_test('expression.standard.', CALCS_TDS,
                                            standard.get('ExpressionExclusions_Standard', ''),
                                            'exprtests/standard/setup.*.txt',
                                            test_dir, get_password_file(standard), get_expected_message(standard),
                                            get_is_smoke_test(standard), get_is_test_enabled(standard), False)
        except KeyError as e:
            logging.debug(e)
            pass

    # Add the optional LOD tests.
    if lod_tests in config.sections():
        try:
            lod = config[lod_tests]
            all_ini_sections.remove(lod_tests)
            test_config.add_logical_test('logical.lod.', STAPLES_TDS, lod.get('LogicalExclusions_Staples', ''),
                                         test_config.get_logical_test_path('logicaltests/setup/lod/setup.*.'), test_dir,
                                         get_password_file(lod), get_expected_message(lod), get_is_smoke_test(lod),
                                         get_is_test_enabled(lod), False)
            test_config.add_expression_test('expression.lod.', CALCS_TDS, lod.get('ExpressionExclusions_Calcs', ''),
                                            'exprtests/lodcalcs/setup.*.txt', test_dir, get_password_file(lod),
                                            get_expected_message(lod), get_is_smoke_test(lod), get_is_test_enabled(lod),
                                            False)
        except KeyError as e:
            logging.debug(e)
            pass

    # Add the optional Staples data check test.
    if staples_data_test in config.sections():
        try:
            staples_data = config[staples_data_test]
            all_ini_sections.remove(staples_data_test)
            test_config.add_expression_test('expression.staples.', STAPLES_TDS, '', 'exprtests/staples/setup.*.txt',
                                            test_dir, get_password_file(staples_data),
                                            get_expected_message(staples_data), get_is_smoke_test(staples_data),
                                            get_is_test_enabled(staples_data), False)
        except KeyError as e:
            logging.debug(e)
            pass

    # Add the optional Union test.
    if union_test in config.sections():
        try:
            union = config[union_test]
            all_ini_sections.remove(union_test)
            test_config.add_logical_test('logical.union.', CALCS_TDS, '',
                                         test_config.get_logical_test_path('logicaltests/setup/union/setup.*.'),
                                         test_dir, get_password_file(union), get_expected_message(union),
                                         get_is_smoke_test(union), get_is_test_enabled(union), False)
        except KeyError as e:
            logging.debug(e)
            pass

    # Add the optional Regex test.
    if regex_test in config.sections():
        try:
            regex = config[regex_test]
            all_ini_sections.remove(regex_test)
            test_config.add_expression_test('expression.regex.', CALCS_TDS, regex.get(KEY_EXCLUSIONS, ''),
                                            'exprtests/regexcalcs', test_dir, get_password_file(regex),
                                            get_expected_message(regex), get_is_smoke_test(regex),
                                            get_is_test_enabled(regex), False)
        except KeyError as e:
            logging.debug(e)
            pass

    # Add the optional Median test.
    if median_test in config.sections():
        try:
            median = config[median_test]
            all_ini_sections.remove(median_test)
            test_config.add_expression_test('expression.median.', CALCS_TDS, median.get(KEY_EXCLUSIONS, ''),
                                            'exprtests/median', test_dir, get_password_file(median),
                                            get_expected_message(median), get_is_smoke_test(median),
                                            get_is_test_enabled(median), False)
        except KeyError as e:
            logging.debug(e)
            pass

    # Add the optional Percentile test.
    if percentile_test in config.sections():
        try:
            percentile = config[percentile_test]
            all_ini_sections.remove(percentile_test)
            test_config.add_expression_test('expression.percentile.', CALCS_TDS, percentile.get(KEY_EXCLUSIONS, ''),
                                            'exprtests/percentile', test_dir, get_password_file(percentile),
                                            get_expected_message(percentile), get_is_smoke_test(percentile),
                                            get_is_test_enabled(percentile), False)
        except KeyError as e:
            logging.debug(e)
            pass

    # Optional logical config settings.
    if logical_config in config.sections():
        try:
            cfg = config[logical_config]
            all_ini_sections.remove(logical_config)
            cfg_data = {}
            name = cfg.get('Name', '')
            cfg_data[name] = {}
            for k in cfg:
                if k == 'Name':
                    continue
                else:
                    cfg_data[name][k] = cfg[k]
            test_config.add_logical_config(cfg_data)
        except KeyError as e:
            logging.debug(e)
            pass

    # Add any extra expression tests.
    for section in config.sections():
        sect = config[section]
        # Allow wildcard substitution .
        tds_name = sect.get('TDS', '').replace('*', config_name)
        if new_expression_test in section or sect.get('Type', '') == 'expression':
            try:
                all_ini_sections.remove(section)
                test_config.add_expression_test(sect.get('Name', ''), tds_name, sect.get(KEY_EXCLUSIONS, ''),
                                                sect.get('TestPath', ''), test_dir, get_password_file(sect),
                                                get_expected_message(sect), get_is_smoke_test(sect),
                                                get_is_test_enabled(sect), False)
            except KeyError as e:
                logging.debug(e)
                pass

        # Add any extra logical tests.
        elif new_logical_test in section or sect.get('Type', '') == 'logical':
            try:
                all_ini_sections.remove(section)
                test_config.add_logical_test(sect.get('Name', ''), tds_name, sect.get(KEY_EXCLUSIONS, ''),
                                             sect.get('TestPath', ''), test_dir, get_password_file(sect),
                                             get_expected_message(sect), get_is_smoke_test(sect),
                                             get_is_test_enabled(sect), False)
            except KeyError as e:
                logging.debug(e)
                pass
        # Add smoke tests
        elif connection_test in section:
            try:
                all_ini_sections.remove(section)
                test_config.add_logical_test('StaplesConnectionTest', STAPLES_TDS, sect.get(KEY_EXCLUSIONS, ''),
                                             test_config.get_logical_test_path('logicaltests/setup/connection_test/setup.staples.*.'),  # noqa: E501
                                             test_dir, get_password_file(sect), get_expected_message(sect), True,
                                             get_is_test_enabled(sect, 'StaplesTestEnabled'), False)
                test_config.add_expression_test('CastCalcsConnectionTest', CALCS_TDS, sect.get(KEY_EXCLUSIONS, ''),
                                                'exprtests/pretest/connection_tests/calcs/', test_dir,
                                                get_password_file(sect), get_expected_message(sect), True,
                                                get_is_test_enabled(sect, 'CastCalcsTestEnabled'), False)
            except KeyError as e:
                logging.debug(e)
                pass

    if all_ini_sections:
        logging.debug("Found unparsed sections in the ini file.")
        for section in all_ini_sections:
            logging.debug("Unparsed section: {0}".format(section))

    logging.debug(test_config)
    return test_config


class TestRegistry(object):
    """Add a new datasource here and then add it to the appropriate registries below."""

    def __init__(self, ini_file):
        self.dsnames = {}
        self.suite_map = {}

        # Read all the datasource ini files and load the test configuration.
        ini_files = get_all_ini_files_local_first('config')
        for f in ini_files:
            logging.debug("Reading ini file [{}]".format(f))
            config = configparser.ConfigParser()
            # Preserve the case of elements.
            config.optionxform = str
            try:
                config.read(f)
            except configparser.ParsingError as e:
                logging.debug(e)
                continue

            self.add_test(load_test(config))

        self.load_ini_file(ini_file)

    def load_ini_file(self, ini_file):
        # Create the test suites (groups of datasources to test)
        registry_ini_file = get_ini_path_local_first('config/registry', ini_file)
        logging.debug("Reading registry ini file [{}]".format(registry_ini_file))
        self.load_registry(registry_ini_file)

    def load_registry(self, registry_ini_file):
        try:
            config = configparser.ConfigParser()
            config.read(registry_ini_file)
            ds = config['DatasourceRegistry']

            for suite_name in ds:
                self.suite_map[suite_name] = [x.strip() for x in self.interpret_ds_list(ds[suite_name], False).split(',')]

        except KeyError:
            # Create a simple default.
            if self.dsnames:
                self.suite_map['all'] = self.dsnames

    def interpret_ds_list(self, ds_list, built_list=None):
        if ds_list == '*':
            return ','.join([x for x in self.dsnames])
        return ds_list

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
        for ds in suite:
            if ds in self.suite_map:
                ds_to_run.extend(self.get_datasources(self.suite_map[ds]))
            elif ds:
                ds_to_run.append(ds)

        # Unique list that preserves order.
        seen_ds = set()
        return [x.strip() for x in ds_to_run if not (x.strip() in seen_ds or seen_ds.add(x.strip()))]


class WindowsRegistry(TestRegistry):
    """Windows specific test suites."""

    def __init__(self):
        super(WindowsRegistry, self).__init__('windows')


class MacRegistry(TestRegistry):
    """Mac specific test suites."""

    def __init__(self):
        super(MacRegistry, self).__init__('mac')


class LinuxRegistry(TestRegistry):
    """Linux specific test suites."""

    def __init__(self):
        super(LinuxRegistry, self).__init__('linux')
