import os

from pathlib import Path
from zipfile import ZipFile

from .connector_file import ConnectorFile
from .manifest import Manifest


def create_jar(source_dir, files, jar_filename, dest_dir="..\jar"):
    """
    Package JAR file from given files.

    :param source_dir: source dir of files to be packaged
    :type source_dir: str

    :param files: files need to be packaged
    :type files: list of ConnectorFile

    :param jar_filename: filename of the created JAR
    :type jar_filename: str

    :param dest_dir: destination dir to create jar file
    :type dest_dir: str

    :return: None
    """

    abs_source_path = os.path.abspath(source_dir)
    print("Start packaging", jar_filename, "from", abs_source_path)

    # if dest dir doesn't exist, then create it
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with ZipFile(os.path.join(dest_dir, Path(jar_filename)), "w") as jar:
        jar.writestr("META-INF/", "")
        jar.writestr("META-INF/MANIFEST.MF", Manifest().get_data())
        for file in files:
            jar.write(os.path.join(abs_source_path, file.file_name), file.file_name)

    print(jar_filename, "was created in", os.path.abspath(dest_dir))


if __name__ == "__main__":
    # TODO: Replace all hard coded below input when ready.
    path_from_args = Path("..\..\samples\plugins\postgres_odbc")
    files_to_package = [
        ConnectorFile("manifest.xml", "manifest"),
        ConnectorFile("connection-dialog.tcd", "connection-dialog"),
        ConnectorFile("connectionBuilder.js", "script"),
        ConnectorFile("dialect.tdd", "dialect"),
        ConnectorFile("connectionResolver.tdr", "connection-resolver")]

    jar_dest_path = Path("..\jar")
    jar_name = "postgres_odbc.jar"
    create_jar(path_from_args, files_to_package, jar_name, jar_dest_path)
