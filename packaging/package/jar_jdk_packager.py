import os
import logging
import subprocess
import shutil

from pathlib import Path
from .connector_file import ConnectorFile

logger = logging.getLogger(__name__)


def jdk_create_jar(source_dir, files, jar_filename, dest_dir):
    """
    Package JAR file from given files using JAVA JDK

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
    logging.debug("Start packaging " + jar_filename + " from " + str(abs_source_path) + " using JDK")

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        logging.debug("Creating destination directory " + str(dest_dir))

    args = ["jar", "cf", jar_filename]
    for file in files:
        args.append(file.file_name)
    p = subprocess.Popen(args, cwd=abs_source_path)
    p.wait()

    shutil.move(abs_source_path/Path(jar_filename), dest_dir/jar_filename)

    logging.info(jar_filename + " was created in " + str(os.path.abspath(dest_dir)))








