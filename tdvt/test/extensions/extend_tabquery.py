from tdvt.tabquery import TabqueryCommandLine

class TabqueryCommandLineExtension(TabqueryCommandLine):
    def extend_command_line(self, cmdline, work):
        """Extend the command line string for calling tabquerycli."""
        try:
            work.test_extension
            cmdline.extend(["--test_arg", work.test_config.output_dir])
        except AttributeError:
            pass


