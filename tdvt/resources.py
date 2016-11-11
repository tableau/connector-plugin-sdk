import pkg_resources

def get_ini_path(base_ini_dir, base_ini_name):
    ini_files = pkg_resources.resource_listdir(__name__, base_ini_dir)
    config_file = base_ini_name + '.ini'
    config_file_override = base_ini_name + '_override.ini'
    if config_file_override in ini_files:
        config_file = config_file_override
    
    return pkg_resources.resource_filename(__name__, base_ini_dir + '/' + config_file)

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
