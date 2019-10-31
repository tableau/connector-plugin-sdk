import os
import logging
import subprocess
import shutil
import xml.etree.ElementTree as ET

from pathlib import Path
from typing import List

from .connector_file import ConnectorFile
from .helper import check_jdk_environ_variable
from .version import __min_version_tableau__

JAR_EXECUTABLE_NAME = "jar"
if os.name == 'nt':
    JAR_EXECUTABLE_NAME += ".exe"
logger = logging.getLogger('packager_logger')
MANIFEST_FILE_TYPE = "manifest"
MANIFEST_FILE_NAME = MANIFEST_FILE_TYPE + ".xml"
MANIFEST_FILE_COPY_NAME = MANIFEST_FILE_TYPE + "_copy.xml"
MANIFEST_ROOT_ELEM = "connector-plugin"
MIN_TABLEAU_VERSION_ATTR = "min-version-tableau"


def stamp_min_support_version(input_dir: Path, file_list: List[ConnectorFile], jar_filename: str) -> bool:
    """
    Stamp of minimum support version to the connector manifest in packaged jar file

    :param input_dir: source dir of files to be packaged
    :type input_dir: Path

    :param file_list: files need to be packaged
    :type file_list: list of ConnectorFile

    :param jar_filename: filename of the created JAR
    :type jar_filename: str

    :return: Boolean
    """

    # find manifest in connector file list
    manifest_file = None
    for file in file_list:
        if file.file_type == MANIFEST_FILE_TYPE and file.file_name == MANIFEST_FILE_NAME:
            manifest_file = file
            break
    if not manifest_file:
        logger.info("Can not find manifest.xml in input directory while packaging")
        return False

    # make a copy of manifest file
    shutil.copyfile(input_dir / manifest_file.file_name, input_dir / MANIFEST_FILE_COPY_NAME)

    # stamp the original manifest file
    manifest = ET.parse(input_dir / manifest_file.file_name)
    plugin_elem = manifest.getroot()
    if plugin_elem.tag != MANIFEST_ROOT_ELEM:
        logger.info("Manifest's root element has been modified after xml validation")
        return False
    plugin_elem.set(MIN_TABLEAU_VERSION_ATTR, __min_version_tableau__)
    manifest.write(input_dir / manifest_file.file_name, encoding="utf-8", xml_declaration=True)

    # update the connector manifest inside taco
    args = ["jar", "uf", jar_filename, manifest_file.file_name]
    p = subprocess.Popen(args, cwd=os.path.abspath(input_dir))
    return_code = p.wait()

    # Recover manifest file from its copy
    os.remove(input_dir / MANIFEST_FILE_NAME)
    os.rename(input_dir / MANIFEST_FILE_COPY_NAME, input_dir / MANIFEST_FILE_NAME)

    # Check Subprocess result
    if return_code != 0:
        logger.info("Unable to stamp minimum support version while packaging")
        return False
    return True


def jdk_create_jar(source_dir: Path, files: List[ConnectorFile], jar_filename: str, dest_dir: Path) -> bool:
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
        return False

    abs_source_path = source_dir.resolve()
    logging.debug("Start packaging " + jar_filename + " from " + str(abs_source_path) + " using JDK")

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        logging.debug("Creating destination directory " + str(dest_dir))

    args = ["jar", "cf", jar_filename]
    for file in files:
        args.append(file.file_name)
    p = subprocess.Popen(args, cwd=abs_source_path)
    p.wait()

    if not stamp_min_support_version(source_dir, files, jar_filename):
        return False

    shutil.move(abs_source_path / jar_filename, dest_dir / jar_filename)

    logging.info(jar_filename + " was created in " + str(os.path.abspath(dest_dir)))
    return True
