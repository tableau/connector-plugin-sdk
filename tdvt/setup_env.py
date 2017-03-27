import re
from .resources import *

def create_test_environment():
    """Create directories and necessary ini files."""
    create_setup_structure()
    create_tdvt_ini_file()

def create_setup_structure():
    try:
        os.mkdir('tds')
    except:
        pass
    try:
        os.makedirs('config/tdvt')
    except:
        pass

def create_tdvt_ini_file():
    try:
        ini_path = 'config/tdvt/tdvt_override.ini'
        if os.path.isfile(ini_path):
            return
        ini = open(ini_path, 'w')
        ini.write('#Add paths to tabquerycli.exe.\n')
        ini.write('[DEFAULT]\n')
        ini.write('TAB_CLI_EXE_X64 = Full Or Relative/Path/to/tabquerycli.exe\n')
        ini.write('TAB_CLI_EXE_MAC = Full Or Relataive/Path/to/tabquerycli.exe\n')
        print ("Created ini file: " + ini_path)
        print ("Please set the tabquerycli.exe file path.")
    except:
        pass

def add_datasource(name):
    """Create the datasource ini file and try to rename the connections in the tds file. This is a necessary step for the logical query tests."""
    create_ds_ini_file(name)
    update_tds_files(name)

def create_ds_ini_file(name):
    try:
        ini_path = 'config/' + name + '.ini'
        if os.path.isfile(ini_path):
            return
        ini = open(ini_path, 'w')

        ini.write('[Datasource]\n')
        ini.write('Name = ' + name + '\n')
        ini.write('LogicalQueryFormat = TODO\n')
        ini.write('\n')
        ini.write('[StandardTests]\n')
        ini.write('\n')
        ini.write('[LODTests]\n')
        ini.write('\n')
        ini.write('[UnionTest]\n')
        ini.write('\n')

        print ("Created ini file: " + ini_path)
        print ("Please set the LogicalQueryFormat value to the expected format.")

    except:
        pass
   
def update_tds_files(name):
     mangle_tds(get_tds_full_path(get_root_dir(), 'cast_calcs.' + name + '.tds'))
     mangle_tds(get_tds_full_path(get_root_dir(), 'Staples.' + name + '.tds'))

def mangle_tds(file_path):
    print ('Modifying ' + file_path)
    try:
        r1 = re.compile('(^.*<named-connection .*? name=\').*?(\'>)') 
        r2 = re.compile('(^.*<relation connection=\').*?(\' .*>)') 

        f =  open(file_path, 'r')
        new_tds = ''
        for line in f:
            new_line = line.rstrip()
            m1 = r1.match(line)
            if m1:
                new_line = m1.group(1) + 'leaf' + m1.group(2)
            m2 = r2.match(line)
            if m2:
                new_line = m2.group(1) + 'leaf' + m2.group(2)

            new_tds += new_line + '\n'

        f.close()
        f =  open(file_path, 'w')
        f.write(new_tds)
        f.close()
    except IOError as e:
        print (e)
        return
