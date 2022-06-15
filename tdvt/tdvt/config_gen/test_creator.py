"""
TestCreator creates test cases from a csv file of expected types and values
ExpectedCreator creates expecteds for an existing test case.
"""

import csv, logging, sys
import os

from pathlib import Path
from typing import Dict, List, Optional

from ..constants import DATA_TYPES

EMPTY_CELL = '%null%'


class TestCreator:

    def __init__(self, csv_file, datasource_name, output_dir=os.getcwd()):
        self.csv_file: Path = Path(csv_file)
        self.datasource_name: str = datasource_name
        self.output_dir: str = output_dir

    def _csv_column_checker(self, column):
        pass

    def _csv_to_lists(self) -> List:
        with open(self.csv_file, newline='') as file:
            reader = csv.reader(file)

            headers = next(reader)
            col_data_types = next(reader)

            columns = []

            for header in headers:
                columns.append([header])

            for i, dt in enumerate(col_data_types):
                columns[i].append(dt)

            for row in reader:
                for j, item in enumerate(row):
                    columns[j].append(item if item else '%null%')

        return columns

    def _write_setup_file(self):
        pass

    def write_expecteds_to_file(self, all_test_results: List):
        output_file_name = 'expected.setup.' + self.datasource_name + '_columns.txt'
        output_path = Path(self.output_dir) / Path(output_file_name)
        with open(output_path, 'x') as out:
            print("writing to {}".format(output_path))
            out.write("<results>\n")
            for item in all_test_results:
                affix = self.return_expected_affix(item)
                out.write("  <test name='{}'>\n".format(item[0]))  # TODO: we should make this a named tuple, not list
                out.write("    <table>\n")
                out.write("      <schema>\n")
                out.write("      </schema>\n")
                for result in item[2]:
                    formatted_result = affix + result + affix if affix else result
                    out.write("        <tuple>\n")
                    out.write("          {}\n".format(formatted_result))
                    out.write("        </tuple>\n")
                out.write("    </table>\n")
                out.write("  </test>\n".format(item[0]))
            out.write("</results>")

    def return_expected_affix(self, col: List) -> Optional[str]:
        """
        Uses a dict from constants to return any affix needed to format a result correctly.
        """
        col_type = col[1]
        return DATA_TYPES.get(col_type, None)

    def _format_output_list_items(self, col: List, affix: str=None) -> List:
        """
        Takes list of results and appends affixes to each result, handling null and empty string values
        """
        formatted_list = []
        for item in col:
            if item == '':
                formatted_list.append('&quot;&quot;')
            elif item == '%null%':
                formatted_list.append(item)
            else:
                if affix:
                    out = affix + item + affix
                else:
                    out = item
                formatted_list.append(out)

        return formatted_list

    def _return_sorted_set_of_results(self, results: List) -> List:
        # this method needs to deal with date/datetime things that are surrounded by #...#
        # but also have %null% or '&quot;&quot;' in the col.
        results_set = set(results)

        first_elements = []

        if '%null%' in results_set:
            first_elements.append('%null%')
            results_set.remove('%null%')
        if '&quot;&quot;' in results_set:
            first_elements.append('&quot;&quot;')
            results_set.remove('&quot;&quot;')

        sorted_results = first_elements + sorted(list(results_set))

        return sorted_results



    def check_csv_exists(self) -> bool:
        if self.csv_file.is_file():
            return True
        else:
            logging.error("CSV file does not exist at indicated path.")
            return False

    def parse_csv(self):
        """
        This method needs to:
          1. Check the csv file exists
          2. Check the csv has correct headers
          3. Dump columns into appropriate buckets (col name, type, all remaining data)
        :None:
        """
        if self.check_csv_exists():
            logging.info("Source CSV file found.")
        else:
            logging.warning("Exiting because CSV did not exist.")
            print("%f does not exist.".format(self.csv_file))
            sys.exit(1)

        input_csv_columns: Dict[str, List[str]] = {}
        # k:v = col_name: [type: str, [values]]

        with open(self.csv_file, 'r') as csv_file:

            for column in csv_file:
                self._csv_column_checker(column)

        # Open the CSV, check for headers, dump data for each col


class ExpectedCreator:
    pass
