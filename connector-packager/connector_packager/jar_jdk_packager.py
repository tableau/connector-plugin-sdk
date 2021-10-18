import os
import logging
import subprocess
import shutil
import xml.etree.ElementTree as ET

from packaging import version
from pathlib import Path
from typing import List

from .connector_file import ConnectorFile
from .helper import check_jdk_environ_variable
from .version import __default_min_version_tableau__

JAR_EXECUTABLE_NAME = "jar"
if os.name == 'nt':
    JAR_EXECUTABLE_NAME += ".exe"
logger = logging.getLogger('packager_logger')
MANIFEST_FILE_TYPE = "manifest"
MANIFEST_FILE_NAME = MANIFEST_FILE_TYPE + ".xml"
MANIFEST_FILE_COPY_NAME = MANIFEST_FILE_TYPE + "_copy.xml"
MANIFEST_ROOT_ELEM = "connector-plugin"
MIN_TABLEAU_VERSION_ATTR = "min-version-tableau"
TABLEAU_SUPPORT_LINK = "https://www.tableau.com/support"


def get_min_support_version(file_list: List[ConnectorFile], cur_min_version_tableau: str, manifest_plugin_elem: ET.Element, input_dir: Path) -> str:
    """
    Get the minimum support version based on features used in the connector

    :param file_list: files need to be packaged
    :type file_list: list of ConnectorFile

    :return: String
    """

    # set minimum tableau version to default, then check for features requiring later version
    min_version_tableau = __default_min_version_tableau__

    reasons = []

    # Check support link
    support_link = manifest_plugin_elem.find("vendor-information").find("support-link").get("url")
    if support_link == TABLEAU_SUPPORT_LINK:
        if 2021.1 > float(min_version_tableau):
            min_version_tableau = "2021.1"
        reasons.append("Tableau support link not usable in versions before 2021.1")

    # Check file types
    for connector_file in file_list:

        # if we have a connection-fields file, then we are using modular dialogs and need 2020.3+
        if connector_file.file_type == "connection-fields":
            if 2020.3 > float(min_version_tableau):
                min_version_tableau = "2020.3"
            reasons.append("Connector uses Connection Dialogs V2, which was added in the 2020.3 release")
        elif connector_file.file_type == "oauth-config":
            if 2021.1 > float(min_version_tableau):
                min_version_tableau = "2021.1"
            reasons.append("Connector uses OAuth, which was added in the 2021.1 release")
        elif connector_file.file_type == "connection-resolver":
            # Check to see if we're using inferred connection resolver, which needs 2021.1+
            tdr_root = ET.parse(input_dir / connector_file.file_name).getroot()
            attribute_list = tdr_root.find('.//connection-normalizer/required-attributes/attribute-list')

            if not attribute_list:
                if 2021.1 > float(min_version_tableau):
                    min_version_tableau = "2021.1"
                reasons.append("Connector uses inferred connection resolver, which was added in the 2021.1 release")

    if version.parse(cur_min_version_tableau) > version.parse(min_version_tableau):
        reasons.append("min-tableau-version set to " + cur_min_version_tableau + ", since that is higher than calculated version of " + min_version_tableau)
        min_version_tableau = cur_min_version_tableau

    return min_version_tableau, reasons


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

    manifest = ET.parse(input_dir / manifest_file.file_name)
    plugin_elem = manifest.getroot()
    if plugin_elem.tag != MANIFEST_ROOT_ELEM:
        logger.info("Manifest's root element has been modified after xml validation")
        return False

    # stamp the min-tableau-version onto original manifest
    cur_min_version_tableau = plugin_elem.get(MIN_TABLEAU_VERSION_ATTR, "0")
    min_version_tableau, reasons = get_min_support_version(file_list, cur_min_version_tableau, plugin_elem, input_dir)
    plugin_elem.set(MIN_TABLEAU_VERSION_ATTR, min_version_tableau)
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

    logger.info("Detected minimum Tableau version required: " + min_version_tableau)
    for reason in reasons:
        logger.info("-" + reason)

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
