import sys

from xsd_validator import validate_xsd

if sys.version_info[0] < 3:
    raise EnvironmentError("package requires Python 3 or greater.")


def validate_package_contents(path):
    print("generate file list from: " + path)
    print("ensure files comply with XSDs in: connector-plugin-sdk/validation")


def create_package_output(path):
    print("create jar package from: " + path)


def main():
    path_from_args = "D:/dev/tableau/connector-plugin-sdk/samples/plugins/postgres_odbc"
    files_to_package = [
        "manifest.xml",
        "connectionBuilder.js",
        "connection-dialog.tcd",
        "connectionResolver.tdr",
        "dialect.tdd"]

    validate_xsd(files_to_package, folder_path=path_from_args)
    create_package_output(path_from_args)


if __name__ == '__main__':
    main()
