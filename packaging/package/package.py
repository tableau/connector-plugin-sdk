import sys
from pathlib import Path

from .xsd_validator import validate_xsd
from .connector_file import ConnectorFile


def create_package_output(path):
    print("create jar package from: " + str(path))


def main():
    path_from_args = Path(
        "D:/dev/tableau/connector-plugin-sdk/samples/plugins/postgres_odbc")
    files_to_package = [
        ConnectorFile("manifest.xml", "manifest"),
        ConnectorFile("connection-dialog.tcd", "connection-dialog"),
        ConnectorFile("connectionBuilder.js", "script"),
        ConnectorFile("dialect.tdd", "dialect"),
        ConnectorFile("connectionResolver.tdr", "connection-resolver")]

    validate_xsd(files_to_package, path_from_args)
    create_package_output(path_from_args)


if __name__ == '__main__':
    main()
