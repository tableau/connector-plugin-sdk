import logging
from pathlib import Path
from pprint import pprint

from .connector_file import ConnectorFile
from .xsd_validator import validate_single_file, PATH_TO_XSD_FILES, XSD_DICT

logger = logging.getLogger(__name__)

def generate_file_list(path_to_folder):
    
    if not path_to_folder.is_dir():
        logger.warning("Error: " + str(path_to_folder) + " does not exist or is not a directory.")   
        return None 
    
    # Make sure manifest exists
    path_to_manifest = path_to_folder / Path("manifest.xml")
    if not path_to_manifest.is_file():
        logger.warning("Error: " + str(path_to_folder) + " does contain a file called manifest.xml.")   
        return None 
    
    file_list = [ConnectorFile("manifest.xml", "manifest")]
    loc_files = False

    # Call parse_file on manifest, when it finds links to other files it will recursiveley call it again
    parse_file(file_list[0], path_to_folder, file_list, loc_files)

    # if we have loc_files, bring them in too
    if loc_files:
        logger.debug("We have localization files. Tenemos archivos de localización. 我们有本地化文件.")

    # files_list = [
    #     ConnectorFile("manifest.xml", "manifest"),
    #     ConnectorFile("connection-dialog.tcd", "connection-dialog"),
    #     ConnectorFile("connectionBuilder.js", "script"),
    #     ConnectorFile("dialect.tdd", "dialect"),
    #     ConnectorFile("connectionResolver.tdr", "connection-resolver")]



    return file_list

def parse_file(file_to_parse, path_to_folder, file_list, loc_files):
    """"
    Arguments:
        file_to_parse {ConnectorFile} -- file to parse
        path_to_folder {Path} -- path to folder that contains the files
        files_list {list[ConnectorFile]} -- Current list of files to append any new files found
        loc_files {bool} -- True if there are any translatable strings


    Returns:
        bool -- True if parsing succeeds
        -- Appends any new files found in this one to file_list and recursively calls parse_file on it
        -- If any translatable strings are found, set loc_files to True
    """
    logger.debug("Parsing " + str(file_to_parse.file_name))
    file_list.append(ConnectorFile("connection-dialog.tcd", "connection-dialog"))
    loc_files = True

    return
    