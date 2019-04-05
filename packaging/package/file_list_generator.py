import logging
from pathlib import Path
import xmlschema
from defusedxml.ElementTree import parse,ParseError

from .connector_file import ConnectorFile
from .xsd_validator import validate_single_file, get_xsd_file, PATH_TO_XSD_FILES

logger = logging.getLogger(__name__)

def generate_file_list(path_to_folder):
    
    logging.debug("Generating list of files to package...")
    
    if not path_to_folder.is_dir():
        logger.warning("Error: " + str(path_to_folder) + " does not exist or is not a directory.")   
        return None 
    
    # Make sure manifest exists
    path_to_manifest = path_to_folder / Path("manifest.xml")
    if not path_to_manifest.is_file():
        logger.warning("Error: " + str(path_to_folder) + " does contain a file called manifest.xml.")   
        return None 
    
    file_list = [ConnectorFile("manifest.xml", "manifest")]
    loc_strings = [] #list of loc strings so we can make sure they are covered in the resource files.

    # Call parse_file on manifest, when it finds links to other files it will recursiveley call it again
    files_valid = parse_file(file_list[0], path_to_folder, file_list, loc_strings)

    if not files_valid:
        return None

    # if we have loc_files, bring them in too
    #TODO: implement finding translatable strings. Not making that a priority right now.
    if len(loc_strings) > 0:
        logger.debug("We have localization files.")
    else:
        logger.debug("No loc files.")

    # files_list = [
    #     ConnectorFile("manifest.xml", "manifest"),
    #     ConnectorFile("connection-dialog.tcd", "connection-dialog"),
    #     ConnectorFile("connectionBuilder.js", "script"),
    #     ConnectorFile("dialect.tdd", "dialect"),
    #     ConnectorFile("connectionResolver.tdr", "connection-resolver")]

    logger.debug("Generated file list:")
    for f in file_list:
        logger.debug("-- " + f.file_name)

    return file_list

def parse_file(file_to_parse, path_to_folder, file_list, loc_strings):
    """"
    Arguments:
        file_to_parse {ConnectorFile} -- file to parse
        path_to_folder {Path} -- path to folder that contains the files
        files_list {list[ConnectorFile]} -- Current list of files to append any new files found
        loc_strings {list[strings]} -- List of transaltable strings we have found


    Returns:
        bool -- True if parsing succeeds
        -- Appends any new files found in this one to file_list and recursively calls parse_file on it
        -- If any translatable strings are found, append it to loc_strings
    """
    path_to_file = path_to_folder / str(file_to_parse.file_name)
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
        
        # Big TODO: Make sure we don't have infinite loop

        if 'file' in child.attrib:
            
            logging.debug("Tag: " + str(child.tag))
            logging.debug(child.attrib)

            # Make new connector file and add it to the list
            logging.debug("Adding file to list (name = " + child.attrib['file'] + ", type = " + child.tag + ")")
            new_file = ConnectorFile(child.attrib['file'], child.tag)
            file_list.append(new_file)
            
            # If not a script, parse the file for more files to include
            if child.tag != 'script':
                children_valid = parse_file(new_file, path_to_folder, file_list, loc_strings)
                if not children_valid:
                    return False

    return True
    