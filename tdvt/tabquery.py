import configparser
import sys
from .resources import *

tab_cli_exe = ''

def configure_tabquery_path():
    """Setup the tabquery path from ini settings."""
    global tab_cli_exe
    config = configparser.ConfigParser()
    
    tdvt_cfg = get_ini_path_local_first('config/tdvt', 'tdvt')
    logging.debug("Reading tdvt ini file [{}]".format(tdvt_cfg))
    config.read(tdvt_cfg)

    if sys.platform.startswith("darwin"):
        tab_cli_exe = config['DEFAULT']['TAB_CLI_EXE_MAC']
    elif sys.platform.startswith("linux"):
        tab_cli_exe = config['DEFAULT']['TAB_CLI_EXE_LINUX']
    else:
        tab_cli_exe = config['DEFAULT']['TAB_CLI_EXE_X64']
    logging.debug("Reading tdvt ini file tabquerycli path is [{}]".format(tab_cli_exe))

def build_tabquery_command_line_local(work):
    """To facilitate testing. Just get the executable name and not the full path to the executable which depends on where the test is run."""
    cmd = build_tabquery_command_line(work)
    new_cmd = []
    new_cmd.append(os.path.split(cmd[0])[1])
    new_cmd += cmd[1:]
    return new_cmd

def build_tabquery_command_line(work):
    """Build the command line string for calling tabquerycli."""
    global tab_cli_exe
    cli_arg = "-q" if work.test_config.logical else "-e"

    cmdline = [tab_cli_exe]
    cmdline_base = [cli_arg, work.test_file]
    cmdline.extend(cmdline_base)
    tds_arg = ["-d", work.test_config.tds]
    cmdline.extend(tds_arg)
    cmdline.extend(["--combined"])

    expected_output_dir = work.test_config.output_dir

    if work.test_config.logical:
        existing_output_filepath, actual_output_filepath, base_test_name, base_filepath, expected_dir = get_logical_test_file_paths(work.test_file, work.test_config.output_dir)
        expected_output_dir = expected_output_dir if expected_output_dir else expected_dir

    if expected_output_dir:
        if not os.path.isdir(expected_output_dir):
            logging.debug("Making dir: {}".format(expected_output_dir))
            try:
                os.makedirs(expected_output_dir)
            except FileExistsError:
                pass
        cmdline.extend(["--output-dir", expected_output_dir])

    if work.test_config.d_override:
        for override in work.test_config.d_override.split(' '):
            cmdline.extend(["-D" + override])

    #Disable constant expression folding. This will bypass the VizEngine for certain simple calculations. This way we run a full database query
    #that tests what you would expect.
    cmdline.extend(["-DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall"])
    
    work.test_config.command_line = cmdline
    return cmdline

def tabquerycli_exists():
    global tab_cli_exe
    if os.path.isfile(tab_cli_exe):
        logging.debug("Found tabquerycli.exe at [{0}]".format(tab_cli_exe))
        return True

    logging.debug("Could not find tabquerycli.exe at [{0}]".format(tab_cli_exe))
    return False


