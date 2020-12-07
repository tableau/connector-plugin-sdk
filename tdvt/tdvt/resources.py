from functools import reduce
import hashlib
import logging
import os
import pkg_resources
import tempfile

def make_temp_dir(components):
    component_string = reduce(lambda x,y : str(x) + y, components)
    return tempfile.mkdtemp(prefix=hashlib.sha224(component_string.encode()).hexdigest())

def get_ini_file_names(base_ini_name):
    return (base_ini_name + '.ini', base_ini_name + '_override.ini')

def get_ini_path_local_first(base_ini_dir, base_ini_name):
    config_file, config_file_override = get_ini_file_names(base_ini_name)
    local_dir_to_check = os.path.join(os.getcwd(), base_ini_dir)
    if os.path.isdir(local_dir_to_check):
        files = os.listdir(local_dir_to_check)
        cfg = config_file_override if config_file_override in files else config_file

        full_cfg_path = os.path.join(os.getcwd(), base_ini_dir, cfg)
        if os.path.isfile(full_cfg_path):
            return full_cfg_path
    return get_ini_path(base_ini_dir, base_ini_name)

def get_ini_path(base_ini_dir, base_ini_name):
    ini_files = pkg_resources.resource_listdir(__name__, base_ini_dir)
    config_file, config_file_override = get_ini_file_names(base_ini_name)
    if config_file_override in ini_files:
        config_file = config_file_override

    return pkg_resources.resource_filename(__name__, base_ini_dir + '/' + config_file)

def get_local_test_dir():
    return os.path.join(os.getcwd(), "tests")

def get_extensions_dir():
    return os.path.join(os.getcwd(), "extensions")

def get_metadata_dir():
    return os.path.join(get_root_dir(), "metadata")

def get_local_logical_test_dir():
    return os.path.join(get_local_test_dir(), "logical")

def get_all_ini_files_local_first(base_ini_dir):
    file_names = []
    local_dir_to_check = os.path.join(os.getcwd(), base_ini_dir)
    if os.path.isdir(local_dir_to_check):
        files = os.listdir(local_dir_to_check)
        for f in files:
            if f[-4:] == '.ini':
                file_path = os.path.join(os.getcwd(), base_ini_dir, f)
                file_names.append(file_path)

    return file_names if file_names else get_all_ini_files(base_ini_dir)

def get_all_ini_files(base_ini_dir):
    file_names = []
    ini_files = pkg_resources.resource_listdir(__name__, base_ini_dir)
    for f in ini_files:
        file_path = pkg_resources.resource_filename(__name__, base_ini_dir + '/' + f)
        if file_path[-4:] == '.ini':
            file_names.append(file_path)
    return file_names

def get_path(base_dir, file_name=None, module_name='tdvt'):
    path_to_get = base_dir if not file_name else base_dir + '/' + file_name
    return pkg_resources.resource_filename(module_name, path_to_get)

def get_root_dir():
    return get_path('')

def split_to_list(path):
    everything = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:
            everything.insert(0, parts[0])
            break
        elif parts[1] == path:
            everything.insert(0, parts[1])
            break
        else:
            path = parts[0]
            everything.insert(0, parts[1])
    return everything

def get_logical_test_file_paths(test_file, output_dir):
    """ Given the full path to logical test file, return all the paths to the expected output and gold result files.
        This depends on the logical tests main directory having 2 levels of subdirectories
        eg  tdvt/logicaltests/setup/calcs
        and tdvt/logicaltests/expected/calcs
    """
    #eg d:/dev/data-dev/tableau-tests/tdvt/logicaltests/setup/calcs
    expected_base_dir = os.path.split(test_file)[0]
    expected_base_dir, logical_subdir = os.path.split(expected_base_dir)
    #Split again to remove the 'setup' dir.
    expected_base_dir = os.path.split(expected_base_dir)[0]
    #eg d:/dev/data-dev/tableau-tests/tdvt/logicaltests/expected/calcs
    expected_base_dir = os.path.join(expected_base_dir, 'expected', logical_subdir)
    expected_output_dir = expected_base_dir

    #eg setup.bugs.b1713.dbo.xml
    expected_base_filename = os.path.split(test_file)[1]
    #Get the abstract test name without the datasource specific customization.
    #eg setup.bugs.b1713.xml
    new_base_filename = ".".join(expected_base_filename.split(".")[:-2]) + ".xml"
    #eg setup.bugs.b1713.dbo-combined.xml
    expected_output_filename = expected_base_filename.replace('.xml', '-combined.xml')

    temp_output_dir = output_dir if output_dir else expected_base_dir
    #eg full path to above file.
    existing_output_filepath = os.path.join(temp_output_dir, expected_output_filename)
    #if not os.path.isfile( existing_output_filepath ):
    #The filename and full path to the expected output from tabquery.
    new_output_filename = "actual." + new_base_filename
    new_output_filepath = os.path.join(temp_output_dir, new_output_filename)
    #Full path the expected file.
    new_base_filepath = os.path.join(expected_base_dir, new_base_filename)

    return existing_output_filepath, new_output_filepath, new_base_filename, new_base_filepath, expected_output_dir

def get_test_file_paths(root_directory, test_name, output_dir):
    """Given a test name like 'exprtests/setup.calcs_data.txt', return full paths to the setup file its self, any actual file, and a list of any existing expected files (can be numbered)."""

    #d:\...\tdvt\exprtests
    test_path_base = os.path.join(root_directory, os.path.split(test_name)[0])
    test_name = os.path.split(test_name)[1]

    setupfile_path = os.path.join(test_path_base, test_name)
    actual_dir = output_dir if output_dir else test_path_base
    actualfile_path = os.path.join(actual_dir, test_name.replace('setup', 'actual.setup'))
    diff_file, diff_ext = os.path.splitext(actualfile_path)
    diff_file_path = diff_file + "_diff" + diff_ext

    expected_file_version = 0
    expected_filename = 'expected.' + test_name
    expected_file_path = test_path_base

    expected_file_path = os.path.join(expected_file_path, expected_filename)
    next_expected_file_path = ''
    expected_file_list = []
    while os.path.isfile(expected_file_path):
        expected_file_list.append(expected_file_path)

        expected_file_version += 1
        #Everything but the ending.
        expected_file_parts = expected_filename.split(".")[:-1]
        #Put the number in.
        expected_file_parts.append( str(expected_file_version) )
        #Add the ending again.
        expected_file_parts.append( expected_filename.split(".")[-1] )
        expected_file = ".".join(expected_file_parts)

        expected_file_path = os.path.join(test_path_base, expected_file)
        next_expected_file_path = expected_file_path

    if not expected_file_list:
        #Always add the base expected file even if it doesn't exist. The callers will use this to copy the actual.
        expected_file_list.append(expected_file_path)

    for filepath in expected_file_list:
        logging.debug("Found expected filepath " + filepath)
    return (actualfile_path, diff_file_path, setupfile_path, expected_file_list, next_expected_file_path)

def find_file_path(root_directory, base_file, default_dir):
    """Return the full path to base_file using either the root_directory and base_file, or a default directory and base_file from there."""
    path_verbatim = os.path.join(root_directory, base_file)
    if os.path.isfile(path_verbatim):
        return path_verbatim

    path_inferred = os.path.join(root_directory, default_dir)
    path_inferred = os.path.join(path_inferred, base_file)
    return path_inferred

def get_resource_full_path(root_directory, base_name, default_dir):
    #First look for a local file (in the place you ran this module, not in the module installation dir).
    local_file = find_file_path(os.getcwd(), base_name, default_dir)
    if os.path.isfile(local_file):
        return local_file
    return find_file_path(root_directory, base_name, default_dir)

def get_base_test(test_file):
    return os.path.split(test_file)[1]

def get_tds_full_path(root_directory, tds):
    """Return the full path to the tds file to use for this test run."""
    return get_resource_full_path(root_directory, tds, "tds")

