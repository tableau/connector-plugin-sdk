# -----------------------------------------------------------------------------
# 
# This file is the copyrighted property of Tableau Software and is protected 
# by registered patents and other applicable U.S. and international laws and 
# regulations.
# 
# Unlicensed use of the contents of this file is prohibited. Please refer to 
# the NOTICES.txt file for further details.
# 
# -----------------------------------------------------------------------------

"""
    Helper script to generate config files for each datasource listed below.
"""

from string import Template
import os
import argparse 

from .test_config import TestConfig
from .datasource_list import *

def generate_config_files(output_dir, force=False):
    base_output_dir = output_dir
    tests = TestRegistry('')

    #Generate all the config files.
    for ds in tests.dsnames:
        cfg = tests.dsnames[ds]
        if not cfg.config_files_exist(base_output_dir) or force:
            need_config_gen = True
            cfg.ensure_config_dir_exists(base_output_dir)
            cfg.write_config_files(base_output_dir)

