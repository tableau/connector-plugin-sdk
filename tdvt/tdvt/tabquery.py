import configparser
import os
import sys

from .resources import *
from .tabquery_path import TabQueryPath

tab_cli_exe = ''

def configure_tabquery_path():
    """Setup the tabquery path from ini settings."""
    global tab_cli_exe

    if os.environ.get('TABQUERY_CLI_PATH'):
        tab_cli_exe = os.environ.get('TABQUERY_CLI_PATH')
        logging.info(
            "Tabquery path from TABQUERY_CLI_PATH environment variable is: {}"
            .format(tab_cli_exe)
        )
    else:
        logging.info("TABQUERY_CLI_PATH environment variable not set. Trying ini files.")
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

def get_max_process_level_of_parallelization(desired_threads):
    if sys.platform.startswith("darwin") and 'tabquerytool' in tab_cli_exe:
        return 1
    return desired_threads

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

def build_connectors_test_tabquery_command_line(conn_test_name, conn_test_file_name, conn_test_password_file):
    global tab_cli_exe
    cmdline = [tab_cli_exe]
    cmdline.extend(["--conn-test", conn_test_name])
    cmdline.extend(["--conn-test-file", conn_test_file_name])
    if conn_test_password_file:
        cmdline.extend(["--conn-test-password-file", conn_test_password_file])
    return cmdline

class TabqueryCommandLine(object):
    def extend_command_line(self, cmdline, work):
        pass

    def build_tabquery_command_line(self, work):
        """Build the command line string for calling tabquerycli."""
        global tab_cli_exe
        cli_arg = "--query-file-list" if work.test_config.logical else "--expression-file-list"

        cmdline = [tab_cli_exe]
        if work.test_config.tested_run_time_config is not None and work.test_config.tested_run_time_config.has_customized_tabquery_path():
            cmdline = [work.test_config.tested_run_time_config.tabquery_paths.get_path(sys.platform)]

        cmdline_base = [cli_arg, work.test_list_path]
        cmdline.extend(cmdline_base)
        tds_arg = ["-d", work.test_config.tds]
        cmdline.extend(tds_arg)
        cmdline.extend(["--combined"])

        password_file = work.test_set.get_password_file_name()
        if os.path.isfile(password_file):
            password_arg = ["--password-file", password_file]
            cmdline.extend(password_arg)

        if work.test_config.output_dir:
            cmdline.extend(["--output-dir", work.test_config.output_dir])

        #Save all the log files from the core Tableau process.
        cmdline.extend(["-DLogDir=" + work.test_config.log_dir])
        cmdline.extend(["-DOverride=ProtocolServerNewLog"])

        if work.test_config.d_override:
            for override in work.test_config.d_override.split(' '):
                cmdline.extend([override])

        logical_rewrite_iter = next((i for i in cmdline if i.find('-DLogicalQueryRewriteDisable') != -1), None)
        if logical_rewrite_iter == None:
            #Disable constant expression folding. This will bypass the VizEngine for certain simple calculations. This way we run a full database query
            #that tests what you would expect.
            cmdline.extend(["-DLogicalQueryRewriteDisable=Funcall:RewriteConstantFuncall"])

        # LogicalQuery cache can cache results across multiple expressions, and prevent
        # issuance of queries to the underlying database, so disable it.
        cmdline.extend(["-DInMemoryLogicalCacheDisable"])

        self.extend_command_line(cmdline, work)
        work.test_config.command_line = cmdline
        return cmdline

def tabquerycli_exists(tabquery_cli_path: TabQueryPath = None):
    global tab_cli_exe
    if tabquery_cli_path:
        resolved_path = tabquery_cli_path.get_path(sys.platform)
        if os.path.isfile(resolved_path):
            logging.debug("Found tabquery at [{0}]".format(resolved_path))
            return True

    if os.path.isfile(tab_cli_exe):
        logging.debug("Found tabquery at [{0}]".format(tab_cli_exe))
        return True

    logging.debug("Could not find tabquery at [{0}]".format(tab_cli_exe))
    return False


