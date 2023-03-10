"""
TestCreator creates test case setup files from a csv file of expected types and values.
ExpectedCreator creates expecteds for an existing test case.
"""
import csv
import logging
import os
import random
import sys

from collections import Counter
from pathlib import Path
from typing import Counter, List, TextIO, Tuple, Union, Dict

from ..constants import DATA_TYPES, TEST_ARGUMENT_DATA_TYPES, CUSTOM_TABLE_TEST_SET, \
    CUSTOM_TABLE_EXPRESSION_TEST_EXCLUSIONS
from ..resources import get_root_dir

EMPTY_CELL = '%null%'


class TestCreator:

    def __init__(self, csv_file, datasource_name, output_dir=os.getcwd()):
        self.csv_file: Path = Path(csv_file)
        self.datasource_name: str = datasource_name
        self.output_dir: Path = Path(output_dir)

    def _csv_to_lists(self) -> Tuple[List[str], List[str]]:
        with open(self.csv_file, 'r') as f:
            headers = f.readline().split(',')
            cleaned_headers = [item.replace('"', '').replace('\n', '') for item in headers]
            col_types = f.readline().split(',')
            cleaned_col_types = [item.replace('"', '').replace('\n', '') for item in col_types]
            # TODO: when we care about null/empty, we add that here

            if len(cleaned_headers) != len(cleaned_col_types):
                logging.error("CSV file has different number of column names and data types than expected.")
                sys.exit(1)

        return cleaned_headers, cleaned_col_types

    def _return_data_type_count(self, tuple_of_csv_data: Tuple[List[str], List[str]]) -> Counter:
        """
        This method returns the number of data types in the csv file.
        :param tuple_of_csv_data: Tuple of lists of headers and data types
        :return: int of number of data types
        """
        col_data_types = tuple_of_csv_data[1]
        return Counter(col_data_types)

    def get_count_of_data_types_in_csv(self) -> Counter:
        csv_tuple = self._csv_to_lists()
        return self._return_data_type_count(csv_tuple)

    def parse_csv_to_list(self) -> Tuple[List[str], List[str]]:
        """
        This method needs to:
          1. Check the csv file exists
          2. Check the csv has correct headers
          3. Dump columns into appropriate buckets (col name, type, all remaining data)
        :None:
        """
        if not self._check_output_and_input_exist():
            print("{} does not exist.".format(self.csv_file))
            sys.exit(1)

        # get data from csv into list of lists
        headers, csv_data = self._csv_to_lists()

        return headers, csv_data


    def write_expecteds_to_file(
            self,
            list_to_write: List[str],
            is_expected_file: bool = False
    ) -> None:
        if is_expected_file:
            output_affix = 'expected.setup.'
        else:
            output_affix = 'setup.'
        for item in list_to_write:
            output_file_name = output_affix + self.datasource_name + '.' + item + '_column.txt'
            output_path = self.output_dir / output_file_name
            with open(output_path, 'w') as out:
                print('writing to {}'.format(output_path))
                logging.info("writing to {}".format(output_path))
                self._test_file_writer(out, item, is_expected_file)
            logging.info("Successfully wrote to {}".format(output_path))

    def _test_file_writer(
            self,
            out: TextIO,
            list_to_write: Union[List[List[str]], List[str], str],
            is_expected_file: bool
    ) -> None:
        if not is_expected_file:
            out.write(list_to_write + '\n')
        else:
            out.write("<results>\n")
            for item in list_to_write:
                out.write("  <test name='{}'>\n".format(item[0]))
                out.write("    <table>\n")
                out.write("      <schema>\n")
                out.write("        <column></column>\n")
                out.write("      </schema>\n")
                for result in item[1:]:
                    out.write("      <tuple>\n")
                    out.write("        <value>{}</value>\n".format(result))
                    out.write("      </tuple>\n")
                out.write("    </table>\n")
                out.write("  </test>\n")
            out.write("</results>")

    def _check_output_and_input_exist(self) -> bool:
        result = True
        if self.csv_file.is_file() and self.output_dir.is_dir():
            logging.info("Source CSV file found.")
            logging.info("Output directory found.")
        else:
            if not self.csv_file.is_file():
                logging.error("CSV file does not exist at indicated path: {}.".format(self.csv_file))
            if not self.output_dir.is_dir():
                logging.error("Output directory {} does not exist.".format(self.output_dir))
            result = False

        return result

    def _parse_col_constants(self) -> Dict[str, List[str]]:
        """
        Parses TEST_ARGUMENT_DATA_TYPES from constants file to get the column names.
        """

        col_type_map = {
            k: [] for k in TEST_ARGUMENT_DATA_TYPES.keys()
        }
        return col_type_map

    def _map_user_cols_to_test_cols(self) -> Dict[str, Dict[str, str]]:
        with open(self.csv_file, 'r') as f:
            reader = csv.reader(f)
            data = zip(*[row for row in reader])
            user_cols_dict = {
                row[0]: {
                    'type': row[1],
                    'data_shape': row[2],
                    'alts': row[3]
                } for row in data
            }
        return user_cols_dict

    def map_user_cols_to_test_args(self) -> Dict[str, List[str]]:
        user_cols_dict = self._map_user_cols_to_test_cols()
        test_args_dict = self._parse_col_constants()
        for key in user_cols_dict.keys():
            for tkey in TEST_ARGUMENT_DATA_TYPES.keys():
                if user_cols_dict[key] == TEST_ARGUMENT_DATA_TYPES[tkey]:
                    test_args_dict[tkey].append(key)
        return test_args_dict

    def rewrite_tests_to_use_user_cols(self, test_sets_to_run: List[str]) -> None:
        test_args_dict = self.map_user_cols_to_test_args()
        """
        We will do the following here:
        1. Read in the test file
           a. it could be a blank line or a commented out line; handle them.
           a. create output file to read using two `with` statements
           b. need to filter out the test sets that won't work (see the spreadsheet)
             - this is from CUSTOM_TABLE_EXPRESSION_TEST_EXCLUSIONS
        2. Find the test arguments
           a. use regex for this. need to differentiate between col names and str args.
        3. Replace the test arguments with the user's column names
           a. if the user col does not have equivalent arg(s), comment out the test 
              and add explanation ('no matching test arg')
           b. need to make sure we don't repeat the same col in test args. add a check
              if there aren't unique args, comment out the test and add explanation
        4. Write the new test file to the output directory 
        """
        test_suite_names = tuple('setup.' + key for key in test_sets_to_run)
        if len(test_suite_names) == 0:
            print("No test sets specified. Exiting.")
            return

        test_dir = get_root_dir() + '/exprtests/standard/'
        test_setup_files = [
            item for item in os.listdir(test_dir)
            if item.startswith(test_suite_names)
            and not item.startswith(CUSTOM_TABLE_EXPRESSION_TEST_EXCLUSIONS)
        ]
        print("Creating custom test files for the following test suites: {}".format(test_sets_to_run))
        for test_file in test_setup_files:
            with open(test_dir + test_file, 'r') as source_file:
                skipped_lines = 0
                all_lines = 0
                lines_out = []
                for line in source_file:
                    all_lines += 1
                    processed_line, skipped = self._process_line(line, test_args_dict)
                    skipped_lines += skipped
                    lines_out.append(processed_line)
            output_file_name = test_file
            if all_lines == skipped_lines:
                output_file_name = 'SKIP.' + test_file
            with open(self.output_dir / output_file_name, 'w') as out_file:
                for line in lines_out:
                    out_file.write(line)
            print("\tCreated {}".format(self.output_dir / output_file_name))


    def _process_line(self, line: str, test_args_dict: List[Dict[str, List]]) -> Tuple[str, int]:
        ignored_line = 0
        # turn commented out tests into blank lines
        if line.startswith('//') or line == '\n':
            ignored_line += 1
            return '\n', ignored_line
        # take care of col names that are in the test args
        else:
            line = line.strip('\n')
            test_col_names = TEST_ARGUMENT_DATA_TYPES.keys()
            extant_cols = [
                col_name for col_name in test_col_names
                if col_name in line
            ]
            user_col_test_col_map = {}
            for column in extant_cols:
                if len(test_args_dict[column]) == 0:
                    new_line = '// ' + line + '  {} has no matching column in the user table.\n'.format(column)
                    ignored_line += 1
                    return new_line, ignored_line
                else:
                    no_match = True
                    column_at_hand = test_args_dict[column].copy()
                    while column_at_hand and no_match:
                        possible_user_col = random.choice(column_at_hand)
                        if possible_user_col in user_col_test_col_map.values():
                            column_at_hand.remove(possible_user_col)
                        else:
                            no_match = False
                    if no_match:
                        ignored_line += 1
                        return '// ' + line + '  {} has no matching column in the user table.\n'.format(column), ignored_line

                    user_col_test_col_map[column] = possible_user_col

            for k in user_col_test_col_map.keys():
                line = line.replace(k, user_col_test_col_map[k])
            return line + '\n', ignored_line

        ignored_line += 1
        return ('// ' + line + ' there was an error processing this line\n', ignored_line)
