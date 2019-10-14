import logging
from typing import List, Optional

from pathlib import Path

from defusedxml.ElementTree import parse

from .connector_file import ConnectorFile
from .xsd_validator import validate_single_file

logger = logging.getLogger(__name__)

HTTPS_STRING = "https://"
TRANSLATABLE_STRING_PREFIX = "@string/"
TABLEAU_SUPPORTED_LANGUAGES = ["de_DE", "en_GB", "en_US", "es_ES", "fr_FR", "ga_IE", "ja_JP", "ko_KR", "pt_BR", "zh_CN",
                               "zh_TW"]


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

            # Check for files for each of the languages we suport
            for language in TABLEAU_SUPPORTED_LANGUAGES:
                resource_file_name = "resources-" + language + ".xml"
                path_to_resource = self.path_to_folder / Path(resource_file_name)
                if path_to_resource.is_file():
                    # Validate that the resource file is valid.
                    new_file = ConnectorFile(resource_file_name, "resource")
                    xml_violations_buffer = []

                    if not validate_single_file(new_file, path_to_resource, xml_violations_buffer):
                        for error in xml_violations_buffer:
                            logging.debug(error)
                        return None

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

        # if the file is not valid, return false
        if not validate_single_file(file_to_parse, path_to_file, xml_violation_buffer):
            for v in xml_violation_buffer:
                logger.debug(v)
            return False

        logger.debug("Parsing " + str(path_to_file))

        # Get XML file ready for parsing
        xml_tree = parse(str(path_to_file))
        root = xml_tree.getroot()

        # Check children. If they have a "file" or a "script" attribute then make a new ConnectorFile and parse
        for child in root.iter():

            # If xml element has file attribute, add it to the file list. If it's not a script, parse that file too.

            if 'file' in child.attrib:

                # Make new connector file object
                logging.debug("Adding file to list (name = " + child.attrib['file'] + ", type = " + child.tag + ")")
                new_file = ConnectorFile(child.attrib['file'], child.tag)

                # figure out if new file is in the list
                already_in_list = new_file in self.file_list

                # add new file to list
                self.file_list.append(new_file)

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
