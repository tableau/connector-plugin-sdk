import pkg_resources
import os

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
