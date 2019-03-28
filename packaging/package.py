import sys

if sys.version_info[0] < 3:
    raise EnvironmentError("package requires Python 3 or greater.")


def validate_package_contents(path):
    print("generate file list from: " + path)
    print("ensure files comply with XSDs in: connector-plugin-sdk/validation")


def create_package_output(path):
    print("create jar package from: " + path)


def main():
    path_from_args = "D:/dev/tableau/connector-plugin-sdk/samples/plugins/postgres_odbc"
    validate_package_contents(path_from_args)
    create_package_output(path_from_args)


main()
