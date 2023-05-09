"""
TestCreator creates test case setup files from a json file of expected types and values.
ExpectedCreator creates expecteds for an existing test case.
"""
import json
import logging
import os
import random
import sys

from pathlib import Path
from typing import List, Tuple, Dict

from ..constants import TEST_ARGUMENT_DATA_TYPES, CUSTOM_TABLE_EXPRESSION_TEST_EXCLUSIONS
from ..resources import get_root_dir


class TestCreator:

    def __init__(self, json_file, datasource_name, output_dir=os.getcwd()):
        self.json_file: Path = Path(json_file)
        self.datasource_name: str = datasource_name
        self.output_dir: Path = Path(output_dir)

    def _json_to_header_list(self) -> List[str]:
        json_file = self.json_file
        with open(json_file, 'r') as f:
            json_dict = json.load(f)
        headers = list(json_dict.keys())
        return headers

    def parse_json_to_list_of_columns(self) -> List[str]:
        if not self._check_output_dir_and_input_json_exist():
            print("{} does not exist.".format(self.json_file))
            sys.exit(1)

        headers = self._json_to_header_list()

        return headers

    def write_test_files(self, list_to_write: List[str]) -> None:
        output_affix = 'setup.'
        for item in list_to_write:
            output_file_name = output_affix + self.datasource_name + '.' + item + '_column.txt'
            output_path = self.output_dir / output_file_name
            with open(output_path, 'w') as out:
                print('writing to {}'.format(output_path))
                logging.info("writing to {}".format(output_path))
                out.write(item + '\n')
            logging.info("Successfully wrote to {}".format(output_path))

    def _check_output_dir_and_input_json_exist(self) -> bool:
        result = True
        if self.json_file.is_file() and self.output_dir.is_dir():
            logging.info("Source JSON file found.")
            logging.info("Output directory found.")
        else:
            if not self.json_file.is_file():
                logging.error("JSON file does not exist at indicated path: {}.".format(self.json_file))
            if not self.output_dir.is_dir():
                logging.error("Output directory {} does not exist.".format(self.output_dir))
            result = False

        return result

    @staticmethod
    def _parse_col_constants() -> Dict[str, List[str]]:
        """
        Parses TEST_ARGUMENT_DATA_TYPES from constants file to get the column names.
        """

        col_type_map = {
            k: [] for k in TEST_ARGUMENT_DATA_TYPES.keys()
        }
        return col_type_map

    def _map_user_cols_to_test_cols(self) -> Dict[str, Dict[str, str]]:
        with open(self.json_file, 'r') as f:
            user_cols_dict = json.load(f)
        return user_cols_dict

    def map_user_cols_to_test_args(self) -> Dict[str, List[str]]:
        user_cols_dict = self._map_user_cols_to_test_cols()
        test_args_dict = self._parse_col_constants()
        for user_col in user_cols_dict.keys():
            for test_col in TEST_ARGUMENT_DATA_TYPES.keys():
                if user_cols_dict[user_col] == TEST_ARGUMENT_DATA_TYPES[test_col]:
                    test_args_dict[test_col].append(user_col)
        return test_args_dict

    def rewrite_tests_to_use_user_cols(self, test_sets_to_run: List[str]) -> None:
        test_args_dict = self.map_user_cols_to_test_args()

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

    @staticmethod
    def _process_line(line: str, test_args_dict: List[Dict[str, List]]) -> Tuple[str, int]:
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
                    new_line = '// {}  {} has no matching column in the user table.\n'.format(line, column)
                    ignored_line += 1
                    return new_line, ignored_line
                else:
                    no_match = True
                    column_at_hand = test_args_dict[column].copy()
                    while column_at_hand and no_match:
                        possible_user_col = column_at_hand[0]
                        if possible_user_col in user_col_test_col_map.values():
                            column_at_hand.remove(possible_user_col)
                        else:
                            no_match = False
                    if no_match:
                        ignored_line += 1
                        return '// {}  {} has no unique matching column in the user table.\n'.format(
                            line, column), ignored_line

                    user_col_test_col_map[column] = possible_user_col

            for k in user_col_test_col_map.keys():
                line = line.replace(k, user_col_test_col_map[k])
            return line + '\n', ignored_line

    def create_custom_expression_tests_for_renamed_staples_and_calcs_tables(self):
        pass
