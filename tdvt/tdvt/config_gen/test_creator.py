"""
TestCreator creates test cases from a csv file of expected types and values
ExpectedCreator creates expecteds for an existing test case.
"""


import csv, logging, sys

from pathlib import Path
from typing import Dict, List, Optional

from ..constants import DATA_TYPES


EMPTY_CELL = '%null%'

class TestCreator:
    csv_file: str
    output_dir: Optional[str]=None
    datasource_name: str

    def __init__(self, csv_file, output_dir, datasource_name):
        self.csv_file: Path = csv_file
        self.output_dir: Path = output_dir
        self.datasource_name: str = datasource_name

    def _csv_column_checker(self, column):
        pass

    def _csv_to_lists(self):
        with open(self.csv_file, newline='') as file:
            reader = csv.reader(file)

            headers = next(reader)

            num_of_headers = len(headers)

            columns = []

            for i in range(num_of_headers):
                columns.append([])

            for i, row in enumerate(reader):
                for i, item in enumerate(row):
                    columns[i].append()

            dict_out = {
                header: None for header in headers
            }

            for i, h in enumerate(headers):
                dict_out[h] = columns[i]

    def _test_expected_formatter(self, col: List):
        """
        Needs to take the col type and then write each result element into the correct looking result type.
        Needs to name the expected file that it's creating.
        """
        col_type = col[0]
        col_data = col[1:]




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
