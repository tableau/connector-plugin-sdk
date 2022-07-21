"""
TestCreator creates test case setup files from a csv file of expected types and values.
ExpectedCreator creates expecteds for an existing test case.
"""

import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, TextIO, Tuple, Union

from ..constants import DATA_TYPES

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

            if len(cleaned_headers) != len(cleaned_col_types):
                logging.error("CSV file has different number of column names and data types than expected.")
                sys.exit(1)

        return cleaned_headers, cleaned_col_types

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
                self._expecteds_writer(out, item, is_expected_file)
            logging.info("Successfully wrote to {}".format(output_path))

    def _expecteds_writer(
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

    def _return_expected_affix(self, col_type: str) -> Optional[str]:
        """
        Uses a dict of constants to return any affix needed to format a result correctly.
        """
        return DATA_TYPES.get(col_type, None)

    def _format_output_list_items(
        self,
        cols: List
    ) -> List:
        """
        Takes list of results and appends affixes to each result, handling null and empty string values.
        Results list contains:
          [name of column, type of column, n results...]
        """
        formatted_list_of_cols = []

        for col in cols:

            col_name = col[0]
            col_type = col[1]
            col_data = col[2:]

            col_out = [col_name, col_type]

            affix = self._return_expected_affix(col_type)

            for item in col_data:
                if item == '':
                    col_out.append('&quot;&quot;')
                elif item == '%null%':
                    col_out.append(item)
                else:
                    if col_type == 'bool':
                        self._format_bools(item)
                    elif col_type == 'float':
                        out = str(float(item))
                    elif col_type in ['time', 'date', 'datetime']:
                        self._format_datetime(item)
                    elif affix:
                        out = affix + item + affix
                    else:
                        out = item
                    col_out.append(out)
                

            formatted_list_of_cols.append(col_out)

        return formatted_list_of_cols

    def _format_datetime(self, item: str) -> None:
        pass

    def _format_bools(self, item: str) -> None:
        item.lower().replace('false', '0').replace('true', '1')

    def _return_sorted_set_of_results(
            self,
            results: List
        ) -> List:
            # this method needs to deal with date/datetime things that are surrounded by #...#
            # but also have %null% or '&quot;&quot;' in the col.
            data_type = results[1]

            first_elements = [results[0]]

            results_set = set(results[2:])

            if '%null%' in results_set:
                first_elements.append('%null%')
                results_set.remove('%null%')
            if '&quot;&quot;' in results_set:
                first_elements.append('&quot;&quot;')
                results_set.remove('&quot;&quot;')
            if data_type == 'int':
                sorted_results = first_elements + sorted(list(results_set), key=int)
            if data_type == 'float':
                sorted_results = first_elements + sorted(list(results_set), key=float)
            else:
                sorted_results = first_elements + sorted(list(results_set))

            return sorted_results

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

    def _write_setup_file(self):
        """
        TODO: this is for the datasource's .ini file
        :return:
        """
        pass
