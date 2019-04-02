import os

from connector_file import ConnectorFile
from zipfile import ZipFile
from manifest import Manifest
from pathlib import Path

def create_jar(jar_file, root, files):
    """
    Package JAR file from given files.
    :param jar_file: filename of the created JAR
    :type jar_file: str
    :param root: root dir of files to be packaged
    :type root: str
    :param files: files need to be packaged
    :type files: list of ConnectorFile
    :return: None
    """

    print("Start packaging", jar_file, "from", os.path.abspath(root))

    with ZipFile(jar_file, "w") as jar:
        jar.writestr("META-INF/", "")
        jar.writestr("META-INF/MANIFEST.MF", Manifest().get_data())
        for file in files:
            jar.write(os.path.join(root, file.file_name), file.file_name)

    print(jar_file, "was created in", os.path.abspath(root))


if __name__ == "__main__":
    path_from_args = Path("..\..\samples\plugins\postgres_odbc")
    files_to_package = [
        ConnectorFile("manifest.xml", "manifest"),
        ConnectorFile("connection-dialog.tcd", "connection-dialog"),
        ConnectorFile("connectionBuilder.js", "script"),
        ConnectorFile("dialect.tdd", "dialect"),
        ConnectorFile("connectionResolver.tdr", "connection-resolver")]

    jar_name = "postgres_odbc.jar"
    create_jar(jar_name, path_from_args, files_to_package)


