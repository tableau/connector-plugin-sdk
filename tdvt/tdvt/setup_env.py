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


def parse_test_args_to_data_types(
    custom_table_cols_and_types: List[Dict[str, str]],
    tableau_data_type_map: Dict[str, str]
) -> Dict[str, str]:
    """Parse the column names and data types from the csv file."""
    col_names = []
    data_types = []
    for col in custom_table_cols_and_types:
        col_names.append(col['name'])
        data_types.append(col['type'])
    return dict(zip(col_names, data_types))


def parse_custom_schema_csv_file(csv_path):
    """Parse the custom schema csv file and return a list of the headers and a list of the rows."""
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)
        rows = []
        for row in csv_reader:
            rows.append(row)
    return headers, rows


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
    output_dir = None
    tds_name = None

    # Find out if the datasource uses custom table and create test files accordingly
    if input("Would you like to run TDVT against a schema other than TestV1? (y/n) ").lower() == 'y':
        custom_schema_name = input("Enter the schema name: ")

    if input("Would you like to run TDVT against a custom table? (y/n) ").lower() == 'y':
        custom_table = True
        tds_name = input("What is the name of your tds file? ")
        csv_path = input("Enter the path to the custom table csv file: ")

        print("Creating tdvt/exprtests/custom_tests if it does not exist.")
        if os.path.isdir(get_root_dir() + '/exprtests/custom_tests'):
            print("tdvt/exprtests/custom_tests already exists.")
            print("Please make sure the directory is empty before continuing.")
            ignored_input = input("Press any key to continue. ")
        else:
            try:
                os.mkdir(get_root_dir() + '/exprtests/custom_tests')
            except Exception as e:
                print("Could not create custom_tests directory. Error was " + str(e))
                print("Please create the directory manually and run the script again.")
        output_dir = Path(Path(os.getcwd()) / 'tdvt/exprtests/custom_tests')

        print("Test directory created. Generating setup files to enumerate table rows.")

        tc = TestCreator(csv_path, name, output_dir)
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

    create_ds_ini_file(name, logical, custom_schema_name, tds_name)
    if not custom_table:
        update_tds_files(name, connection_password_name)

    if output_dir:
        print("Setup complete.")
        print("Please run your test against your custom table by running the following command:")
        print("\tpython -m tdvt.tdvt run {} --generate_expected".format(name))
        print("This will generate the expected results for the test in:")
        print("\t{}".format(output_dir))
        print("After you verify the contents of the expecteds, tests can be run with:")
        print("\tpython -m tdvt.tdvt run {}".format(name))


def create_ds_ini_file(
        name,
        logical_config,
        custom_schema_name: Optional[str] = None,
        tds_name: Optional[str] = None
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
            ini.write('\n')
            ini.write('[LODTests]\n')
            ini.write('\n')
            ini.write('[UnionTest]\n')
            ini.write('\n')
            ini.write('[ConnectionTests]\n')
            ini.write('StaplesTestEnabled = True\n')
            ini.write('CastCalcsTestEnabled = True\n')
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
    # TODO: change this to get rid of calcs/staples hardcoding; handle custom table then fall back
    mangle_tds(get_tds_full_path(get_root_dir(), 'cast_calcs.' + name + '.tds'),
               connection_password_name)  # TODO: Update this to take whatever
    mangle_tds(get_tds_full_path(get_root_dir(), 'Staples.' + name + '.tds'), connection_password_name)


def mangle_tds(file_path, connection_password_name):
    print('Modifying ' + file_path)
    try:
        r1 = re.compile('(^\s*<named-connection .*? name=\').*?(\'>)')
        r2 = re.compile('(^\s*<.*relation connection=\').*?(\' .*>)')
        r3 = re.compile('(^\s*<connection .*?)(\s*/>)')

        f = open(file_path, 'r')
        new_tds = ''
        for line in f:
            new_line = line.rstrip()
            m1 = r1.match(line)
            if m1:
                new_line = m1.group(1) + 'leaf' + m1.group(2)

            m2 = r2.match(line)
            if m2:
                new_line = m2.group(1) + 'leaf' + m2.group(2)

            m3 = r3.match(line)
            if m3 and not 'tdvtconnection=\'' in line.lower():
                new_line = m3.group(1) + ' tdvtconnection=\'' + connection_password_name + '\' ' + m3.group(2)

            new_tds += new_line + '\n'

        f.close()
        f = open(file_path, 'w')
        f.write(new_tds)
        f.close()
    except IOError as e:
        print(e)
        return
