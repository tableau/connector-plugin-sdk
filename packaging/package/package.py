import sys
from pathlib import Path

from xsd_validator import validate_xsd
from connector_file import ConnectorFile
from jar_packager import create_jar

if sys.version_info[0] < 3:
    raise EnvironmentError("package requires Python 3 or greater.")


def validate_package_contents(path):
    print("generate file list from: " + path)
    print("ensure files comply with XSDs in: connector-plugin-sdk/validation")


def create_package_output(path):
    print("create jar package from: " + path)


def main():
    # TODO: Replace all hard coded below input when ready.
    path_from_args = Path("..\..\samples\plugins\postgres_odbc")
    files_to_package = [
        ConnectorFile("manifest.xml", "manifest"),
        ConnectorFile("connection-dialog.tcd", "connection-dialog"),
        ConnectorFile("connectionBuilder.js", "script"),
        ConnectorFile("dialect.tdd", "dialect"),
        ConnectorFile("connectionResolver.tdr", "connection-resolver")]

    validate_xsd(files_to_package, path_from_args)

    jar_dest_path = Path("../jar")
    jar_name = "postgres_odbc.jar"
    create_jar(path_from_args, files_to_package, jar_name, jar_dest_path)


if __name__ == '__main__':
    main()
