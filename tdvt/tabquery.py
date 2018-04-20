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

def build_tabquery_command_line(work):
    try:
        sys.path.insert(0, get_extensions_dir())
        from extend_tabquery import TabqueryCommandLineExtension
        sys.path.pop(0)
        tb = TabqueryCommandLineExtension()
        logging.debug("Imported extension extend_tabquery")
    except:
        tb = TabqueryCommandLine()

    cmdline = tb.build_tabquery_command_line(work)
    return cmdline

class TabqueryCommandLine(object):
    def extend_command_line(self, cmdline, work):
        pass

    def build_tabquery_command_line(self, work):
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

            #Save all the log files from the core Tableau process.
            cmdline.extend(["-DLogDir=" + expected_output_dir])
            cmdline.extend(["-DLogName=" + "log_" + work.test_name.replace('.', '_') + ".txt"])
            cmdline.extend(["-DOverride=ProtocolServerNewLog"])

        if work.test_config.d_override:
            for override in work.test_config.d_override.split(' '):
                cmdline.extend([override])

        #Disable constant expression folding. This will bypass the VizEngine for certain simple calculations. This way we run a full database query
        #that tests what you would expect.
        cmdline.extend(["-DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall"])

        self.extend_command_line(cmdline, work)
        work.test_config.command_line = cmdline
        return cmdline

def tabquerycli_exists():
    global tab_cli_exe
    if os.path.isfile(tab_cli_exe):
        logging.debug("Found tabquerycli.exe at [{0}]".format(tab_cli_exe))
        return True

    logging.debug("Could not find tabquerycli.exe at [{0}]".format(tab_cli_exe))
    return False


