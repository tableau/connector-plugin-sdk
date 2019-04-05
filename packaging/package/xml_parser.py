import logging
from pathlib import Path
import xmlschema
from defusedxml.ElementTree import parse,ParseError

from .connector_file import ConnectorFile
from .xsd_validator import validate_single_file, get_xsd_file, PATH_TO_XSD_FILES

logger = logging.getLogger(__name__)

class XMLParser:
    """
        Handles parsing the xml connector files

        Arguments:
            path_to_folder {Path} -- path to the folder that contains the files to parse

        Methods:
            generate_file_list: generates a list of files to package by parsing the xml files
    """

    def __init__(self, path_to_folder):
        self.path_to_folder = path_to_folder
        self.class_name = None # Get this from the class name in the manifest file
        self.file_list = [] # list of files to package
        self.loc_strings = [] #list of loc strings so we can make sure they are covered in the resource files.


    def generate_file_list(self):
        """
        Arguments:
            None

        Returns:
            list[ConnectorFile] -- list of files to package
            -- Returns none if any of the files are invalid, or the files do not agree on the name
        """
        
        logging.debug("Generating list of files to package...")
        
        if not self.path_to_folder.is_dir():
            logger.warning("Error: " + str(self.path_to_folder) + " does not exist or is not a directory.")   
            return None
        
        # Make sure manifest exists
        path_to_manifest = self.path_to_folder / Path("manifest.xml")
        if not path_to_manifest.is_file():
            logger.warning("Error: " + str(self.path_to_folder) + " does contain a file called manifest.xml.")   
            return None
        
        self.file_list.append(ConnectorFile("manifest.xml", "manifest"))   

        # Call parse_file on manifest, when it finds links to other files it will recursiveley call it again
        files_valid = self.parse_file(self.file_list[0])

        if not files_valid:
            return None

        # if we have loc_files, bring them in too
        #TODO: implement finding translatable strings. Not making that a priority right now.
        if len(self.loc_strings) > 0:
            logger.debug("We have localization files.")
        else:
            logger.debug("No loc files.")

        logger.debug("Generated file list:")
        for f in self.file_list:
            logger.debug("-- " + f.file_name)

        if not self.class_name:
            logger.debug("Class name not found in files.")
            return None

        return self.file_list

    def parse_file(self, file_to_parse):
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

        xsd_path = PATH_TO_XSD_FILES / get_xsd_file(file_to_parse)

        logger.debug("Parsing " + str(path_to_file))

        # Get XML file ready for parsing
        schema = xmlschema.XMLSchema(str(xsd_path))
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
                if child.tag != 'script':
                    children_valid = self.parse_file(new_file)
                    if not children_valid:
                        return False

            if 'class' in child.attrib:
                
                # Name not yet found
                if not self.class_name:
                    logging.debug("Found class name: " + child.attrib['class'])
                    self.class_name = child.attrib['class']

                # Make sure the name is the same
                elif child.attrib['class'] != self.class_name:
                    logging.debug("Error: class attribute in file " + file_to_parse.file_name + " does not equal class attribute in manifest.")
                    logging.debug(self.class_name +  " in manifest, " + child.attrib['class'] + " in " + file_to_parse.file_name)
                    return False

        # If we've reached here, all the children are valid
        return True
        