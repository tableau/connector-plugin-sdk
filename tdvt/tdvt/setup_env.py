import csv
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

from .config_gen.datasource_list import print_logical_configurations
from .config_gen.test_creator import TestCreator
from .resources import *
from .constants import CUSTOM_TABLE_TEST_SET



def create_test_environment():
    """Create directories and necessary ini files."""
    create_setup_structure()
    create_tdvt_ini_file()


def create_setup_structure():
    try:
        os.mkdir('tds')
    except:
        pass
    try:
        os.makedirs('config/tdvt')
    except:
        pass


def create_tdvt_ini_file():
    try:
        ini_path = 'config/tdvt/tdvt_override.ini'
        if os.path.isfile(ini_path):
            return
        ini = open(ini_path, 'w')
        ini.write('#Add paths to tabquery executable.\n')
        ini.write('[DEFAULT]\n')
        ini.write('TAB_CLI_EXE_X64 = Full Or Relative/Path/to/tabquerytool.exe\n')
        ini.write('TAB_CLI_EXE_MAC = Full Or Relataive/Path/to/tabquerytool.exe\n')
        print("Created ini file: " + ini_path)
        print("Please set the tabquery executable file path.")
    except:
        pass


def add_datasource(name, ds_registry):
    """
        Create the datasource ini file and try to rename the connections in the tds file.
        This is a necessary step for the logical query tests.
    """
    print("Make sure you have already saved the appropriate TDS files in the tds directory.")
    print("Adding a new datasource [" + name + "] ...")

    connection_password_name = name + "_connection"
    if input(
            "Would you like to setup a password file? (y/n) "
            "This is suitable for a single connection per tds (standard). "
    ).lower() == 'y':
        password = input("Enter the datasource password: ")
        create_password_file(name, connection_password_name, password)
    picked = False
    logical = None
    custom_schema_name = None
    custom_table = None
    output_dir = None
    tds_name = None
    renamed_cols = False

    # Find out if the datasource uses custom table and create test files accordingly
    if input("Would you like to run TDVT against a schema other than TestV1? (y/n) ").lower() == 'y':
        custom_schema_name = input("Enter the schema name: ")

    if input("Do you have the Staples & Calcs tables loaded using different column names "
             "(e.g. num0_col instead of num0)? (y/n) ").lower() == 'y':
        renamed_cols = True
        col_mapping_json_path = Path(input("Enter the path to the column mapping json file: "))
        if not col_mapping_json_path.exists():
            logging.error("Could not find the file at {}".format(col_mapping_json_path))
            print("Could not find the file at the path provided. Please try again.")
            sys.exit(1)
        output_dir = create_custom_test_dir(name)
        tc = TestCreator(col_mapping_json_path, name, output_dir)
        tc.create_custom_expression_tests_for_renamed_staples_and_calcs_tables()
        print("Created custom expression tests for renamed staples and calcs tables.")

    if not renamed_cols and input("Would you like to run TDVT against a custom table? (y/n) ").lower() == 'y':
        custom_table = True
        tds_name = input("What is the name of your tds file? ")
        custom_table_json_path = input("Enter the path to the custom table csv file: ")

        output_dir = create_custom_test_dir()

        tc = TestCreator(custom_table_json_path, name, output_dir)
        headers = tc.parse_json_to_list_of_columns()
        tc.write_test_files(headers)  # this creates the test setup file.

        tests = []  # This is our list of tests to run.
        for i in CUSTOM_TABLE_TEST_SET:  # Include the nice_name & url for each prompt.
            item = CUSTOM_TABLE_TEST_SET[i]
            try:
                nice_name = item.get("nice_name")
                url_for_docs = item.get("url_for_docs")
            except TypeError:
                print("Error reading file format.")
                nice_name = "*no nice_name provided*"
                url_for_docs = "*no url_for_docs provided*"

            msg = "Do you want to run the {} suite? Learn more about it at {}. y/n: ".format(
                nice_name, url_for_docs
            )
            prompt = input(msg).lower()

            while prompt != 'y' and prompt != "n":
                print("Please enter 'y' or 'n': ")
                prompt = input(msg)
            if prompt == "y":
                tests.append(i)
        if tests:
            tc.rewrite_tests_to_use_user_cols(tests)

    while not picked:
        logical = input(
            "Enter the logical config to use or type 'list' to see the options or 's' to skip selecting one now: "
        )
        if logical == 'list':
            print_logical_configurations(ds_registry)
        else:
            logical = logical.replace("\"", "")
            logical = logical.replace("\'", "")
            logical = logical.strip()
            picked = True
        if logical == 's':
            logical = None

    create_ds_ini_file(name, logical, custom_schema_name, tds_name, renamed_cols)
    if not custom_table:
        update_tds_files(name, connection_password_name)

    if custom_table:
        print("Setup complete.")
        print("Please run your test against your custom table by running the following command:")
        print("\tpython -m tdvt.tdvt run {} --generate_expected".format(name))
        print("This will generate the expected results for the test in:")
        print("\t{}".format(output_dir))
        print("After you verify the contents of the expecteds, tests can be run with:")
        print("\tpython -m tdvt.tdvt run {}".format(name))


def create_custom_test_dir(datasource_name=None) -> str:
    if datasource_name:
        output_dir = get_root_dir() + '/exprtests/custom_tests/{}'.format(datasource_name)
    else:
        output_dir = get_root_dir() + '/exprtests/custom_tests'
    print("Creating {} if it does not exist.".format(output_dir))
    if os.path.isdir(output_dir):
        print("{} already exists.".format(output_dir))
        print("Please make sure the directory is empty before continuing.")
        ignored_input = input("Press any key to continue. ")
    try:
        os.mkdir(output_dir)
    except Exception as e:
        print("Could not create custom_tests directory. Error was " + str(e))
        print("Please create the directory manually and run the script again.")
    print("Test directory created.")
    return output_dir


def create_ds_ini_file(
        name,
        logical_config,
        custom_schema_name: Optional[str] = None,
        tds_name: Optional[str] = None,
        renamed_cols: bool = False
):
    try:
        ini_path = 'config/' + name + '.ini'
        if os.path.isfile(ini_path):
            overwrite = input("Overwrite existing ini file?(y/n)")
            if overwrite.lower() != 'y':
                return
        ini = open(ini_path, 'w')

        ini.write('[Datasource]\n')
        ini.write('Name = ' + name + '\n')
        if not logical_config:
            ini.write('LogicalQueryFormat = TODO\n')
        else:
            ini.write('LogicalQueryFormat = ' + logical_config + '\n')
        if custom_schema_name:
            ini.write('SchemaName = ' + custom_schema_name + '\n')
        ini.write('\n')
        if not tds_name:
            ini.write('[StandardTests]\n')
            if renamed_cols:
                ini.write('TestPath = exprtests/custom_tests/{}/standard/\n'.format(name))
            ini.write('\n')
            ini.write('[LODTests]\n')
            if renamed_cols:
                ini.write('TestPath = exprtests/custom_tests/{}/lodcalcs/\n'.format(name))
            ini.write('\n')
            ini.write('[UnionTest]\n')
            ini.write('\n')
            ini.write('[ConnectionTests]\n')
            ini.write('StaplesTestEnabled = True\n')
            ini.write('CastCalcsTestEnabled = True\n')
            if renamed_cols:
                ini.write('TestPath = exprtests/custom_tests/{}/pretest/connection_tests/\n'.format(name))
        if tds_name:
            ini.write('[CustomSchemaTests]\n')
            ini.write('TDS = ' + tds_name + '\n')
        ini.write('\n')

        print("Created ini file: " + ini_path)
        if not logical_config:
            print("Please set the LogicalQueryFormat value to the expected format.")

    except:
        pass


def create_password_file(name, connection_name, password):
    try:
        file_path = 'tds/' + name + '.password'
        if os.path.isfile(file_path):
            overwrite = input("Overwrite existing file?(y/n): " + file_path)
            if overwrite.lower() != 'y':
                return
        ini = open(file_path, 'w')

        ini.write(connection_name + ';' + password + '\n')

        print("Created file: " + file_path)
    except IOError as e:
        print(e)
        pass


def update_tds_files(name, connection_password_name):
    mangle_tds(get_tds_full_path(get_root_dir(), 'cast_calcs.' + name + '.tds'),
               connection_password_name)  # TODO: Update this to take whatever
    mangle_tds(get_tds_full_path(get_root_dir(), 'Staples.' + name + '.tds'), connection_password_name)


def mangle_tds(file_path, connection_password_name):
    print('Modifying ' + file_path)
    try:
        with open(file_path, 'r') as f:
            new_tds = updated_tds_as_str(f, connection_password_name)
        f = open(file_path, 'w')
        f.write(new_tds)
        f.close()
    except IOError as e:
        print(e)
        return


def get_tds_new_line(rmatch: Optional[re.Match[str]], mid_str: str, connection_password_name=None):
    new_line = ''
    new_line = rmatch.group(1) + mid_str + connection_password_name + '\' ' + rmatch.group(2)

    return new_line


def updated_tds_as_str(f, connection_name) -> str:
    r1 = re.compile('(^\s*<named-connection.*?name=\')(.*?)(\'>)')  # no space because of redshift_singlenode
    r2 = re.compile('(^\s*<.*relation connection=\')(.*?)(\' .*>)')
    r3 = re.compile('(^\s*<connection)(\s)(.*>)')
    new_tds = ''

    for line in f:
        new_line = line.rstrip()
        m1 = r1.match(line)
        if m1:
            new_line = m1.string.replace(m1.group(2), 'leaf')

        m2 = r2.match(line)
        if m2:
            new_line = m2.string.replace(m2.group(2), 'leaf')

        m3 = r3.match(line)
        if m3 and not 'tdvtconnection=\'' in line.lower():
            new_line = f"{m3.group(1)} tdvtconnection='{connection_name}' {m3.group(3)}"

        new_tds += new_line + '\n'
    return new_tds

def get_failed_cmd_line(cls, index):
    res_info = cls.combined_output[index]
    ds = res_info.get('Suite')
    tds_name = res_info.get('TDSName')
    ab_path = res_info.get('TestPath')
    test_type = res_info.get('Test Type')
    if test_type == 'expression':
        test_type = 'exp'
    else:
        test_type = 'logp'
    if get_root_dir() in ab_path:
        test_path = ab_path.split(get_root_dir())[1].replace('\\','/').lstrip('/')
    else:
        test_path = ab_path
    str_info = {'ds': ds,
                'tds_name': tds_name,
                'test_path': test_path,
                'test_type': test_type
                }
    cmd_line = 'python -m run-pattern {ds} --{test_type} {test_path} --tdp {tds_name}.tds'.format(**str_info)

    return cmd_line
