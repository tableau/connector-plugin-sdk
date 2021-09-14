import logging
from typing import List, Optional
import os
import sys

from pathlib import Path

from defusedxml.ElementTree import parse

from .connector_file import ConnectorFile
from .xsd_validator import validate_single_file

logger = logging.getLogger('packager_logger')


MAX_FILE_SIZE = 1024 * 256  # This is based on the max file size we will load on the Tableau side
HTTPS_STRING = "https://"
TRANSLATABLE_STRING_PREFIX = "@string/"
TABLEAU_FALLBACK_LANGUAGE = "en_US"  # If localizing a connector, US English must be translated since we'll fall back to the English strings if we can't find one for the correct language
TABLEAU_SUPPORTED_LANGUAGES = ["de_DE", "en_GB", "es_ES", "fr_CA", "fr_FR", "ga_IE", "it_IT", "ja_JP", "ko_KR",
                               "pt_BR", "zh_CN", "zh_TW"]


class XMLParser:
    """
        Handles parsing the xml connector files

        Arguments:
            path_to_folder {Path} -- path to the folder that contains the files to parse

        Methods:
            generate_file_list: generates a list of files to package by parsing the xml files
    """

    def __init__(self, path_to_folder: Path):
        self.path_to_folder = path_to_folder
        self.class_name = None  # Get this from the class name in the manifest file
        self.file_list = []  # list of files to package
        self.loc_strings = []  # list of loc strings so we can make sure they are covered in the resource files.

    def generate_file_list(self) -> Optional[List[ConnectorFile]]:
        """
        Arguments:
            None

        Returns:
            list[ConnectorFile] -- list of files to package
            -- Returns none if any of the files are invalid, or the files do not agree on the name
        """

        logging.debug("Generating list of files for validation and/or packaging...")

        if not self.path_to_folder.is_dir():
            logger.error("Error: " + str(self.path_to_folder) + " does not exist or is not a directory.")
            return None

        # Make sure manifest exists
        path_to_manifest = self.path_to_folder / "manifest.xml"
        if not path_to_manifest.is_file():
            logger.error("Error: " + str(self.path_to_folder) + " does not contain a file called manifest.xml.")
            return None

        self.file_list.append(ConnectorFile("manifest.xml", "manifest"))

        # Call parse_file on manifest, when it finds links to other files it will recursiveley call it again
        files_valid = self.parse_file(self.file_list[0])

        if not files_valid:
            return None

        if not self.class_name:
            logger.debug("Class name not found in files.")
            return None

        # If we found localized strings, bring in the resource files as well
        if len(self.loc_strings) > 0:
            logger.debug("Found translatable strings, looking for resource files...")
            logger.debug('Strings found:')
            for s in self.loc_strings:
                logger.debug("-- " + s)

            # Check that the fallback language (English) exists
            fallback_resource_file_name = "resources-" + TABLEAU_FALLBACK_LANGUAGE + ".xml"
            path_to_fallback_resource = self.path_to_folder / Path(fallback_resource_file_name)
            if path_to_fallback_resource.is_file():
                self.file_list.append(ConnectorFile(fallback_resource_file_name, "resource"))
                logging.debug("Adding file to list (name = " + fallback_resource_file_name + ", type = resource)")
            else:
                logger.error("Error: Found localized strings but " + fallback_resource_file_name + " does not exist. US English translations are required to fall back on if other languages are not translated.")
                return None

            # Check for files for each of the languages we suport
            for language in TABLEAU_SUPPORTED_LANGUAGES:
                resource_file_name = "resources-" + language + ".xml"
                path_to_resource = self.path_to_folder / Path(resource_file_name)
                if path_to_resource.is_file():
                    self.file_list.append(ConnectorFile(resource_file_name, "resource"))
                    logging.debug("Adding file to list (name = " + resource_file_name + ", type = resource)")

        else:
            logger.debug("No loc files.")

        # Print generated files to log for debugging
        logger.debug("Generated file list:")
        for f in self.file_list:
            logger.debug("-- " + f.file_name)

        return self.file_list

    def parse_file(self, file_to_parse: ConnectorFile) -> bool:
        """"
        Arguments:
            file_to_parse {ConnectorFile} -- file to parse

        Returns:
            bool -- True if parsing succeeds
            -- Appends any new files found in this one to self.file_list and recursively calls parse_file on it
            -- If any translatable strings are found, append it to self.loc_strings
        """
        path_to_file = self.path_to_folder / str(file_to_parse.file_name)
        xml_violation_buffer = []

        logger.debug("Parsing " + str(path_to_file))

        # If the file is too big, we shouldn't try and parse it, just log the violation and move on
        if path_to_file.stat().st_size > MAX_FILE_SIZE:
            logging.error(file_to_parse.file_name + " exceeds maximum size of " + str(int(MAX_FILE_SIZE / 1024)) + " KB")
            return False

        # Get XML file ready for parsing
        # Catch any errors and display them to user
        try:
            xml_tree = parse(str(path_to_file))
            root = xml_tree.getroot()
        except Exception:
            saved_error_type = sys.exc_info()[0]
            saved_error = sys.exc_info()[1]
            logger.error("Error parsing " + file_to_parse.file_name + "\nError Type: " + str(saved_error_type) +
                         "\n" + str(saved_error))
            return False

        # Check children. If they have a "file" or a "script" attribute then make a new ConnectorFile and parse
        for child in root.iter():

            # Check the tag
            # Oauth config file uses dbclass tag instead of class attribute. We need to make sure that matches the class name as well.
            if child.tag == "dbclass":
                if child.text != self.class_name:
                    logging.error("Error: dbclass in file " + file_to_parse.file_name +
                                  " does not equal class attribute in manifest.")
                    logging.debug(self.class_name + " in manifest, " + child.text + " in " +
                                  file_to_parse.file_name)
                    return False

            # Check the attributes
            # If xml element has file attribute, add it to the file list. If it's not a script, parse that file too.
            if 'file' in child.attrib:

                # Check to make sure the file actually exists
                new_file_path = str(self.path_to_folder / child.attrib['file'])

                if not os.path.isfile(new_file_path):
                    logger.debug("Error: " + new_file_path + " does not exist but is referenced in " +
                                 str(file_to_parse.file_name))
                    return False

                # Make new connector file object
                logging.debug("Adding file to list (name = " + child.attrib['file'] + ", type = " + child.tag + ")")
                new_file = ConnectorFile(child.attrib['file'], child.tag)

                # figure out if new file is in the list
                already_in_list = new_file in self.file_list

                # add new file to list
                self.file_list.append(new_file)

                # If connection-metadata, make sure that connection-fields file exists
                if child.tag == 'connection-metadata':
                    connection_fields_exists = False

                    for xml_file in self.file_list:
                        if xml_file.file_type == 'connection-fields':
                            connection_fields_exists = True
                            break

                    if not connection_fields_exists:
                        logger.debug("Error: connection-metadata file requires a connection-fields file")
                        return False

                # If not a script and not in list, parse the file for more files to include
                if child.tag != 'script' and not already_in_list:
                    children_valid = self.parse_file(new_file)
                    if not children_valid:
                        return False

            if 'url' in child.attrib:

                url_link = child.attrib['url']
                # If URL does not start with https:// then do not package and return false
                if not url_link.startswith(HTTPS_STRING):
                    logging.error("Error: Only HTTPS URL's are allowed. URL " + url_link +
                        " is a non-https link in file " + file_to_parse.file_name)
                    return False

            # If an element has the 'class' attribute, and the class name is not set, set the class name. If it is set,
            #  make sure it is the same name
            if 'class' in child.attrib:

                # Name not yet found
                if not self.class_name:
                    logging.debug("Found class name: " + child.attrib['class'])
                    self.class_name = child.attrib['class']

                # Make sure the name is the same
                elif child.attrib['class'] != self.class_name:
                    logging.error("Error: class attribute in file " + file_to_parse.file_name +
                                  " does not equal class attribute in manifest.")
                    logging.debug(self.class_name + " in manifest, " + child.attrib['class'] + " in " +
                                  file_to_parse.file_name)
                    return False

            # If an attribute has @string, then add that string to the loc_strings list.
            for key, value in child.attrib.items():
                if value.startswith(TRANSLATABLE_STRING_PREFIX):
                    self.loc_strings.append(value)

        # If we've reached here, all the children are valid
        return True
