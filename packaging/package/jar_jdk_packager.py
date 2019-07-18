import os
import logging
import subprocess
import shutil

from pathlib import Path
from .connector_file import ConnectorFile
from .helper import check_jdk_environ_variable

JAR_EXECUTABLE_NAME = "jar.exe"
PATH_ENVIRON = "PATH"
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

    :return: Boolean
    """

    if not check_jdk_environ_variable(JAR_EXECUTABLE_NAME):
        logger.error("Error: jdk_create_jar: no jdk set up in PATH environment variable, "
                     "please download JAVA JDK and add it to PATH")
        return False

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
    return True






