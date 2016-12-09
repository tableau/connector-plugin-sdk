"""
    Helper script to generate config files for each datasource listed below.
"""

from string import Template
import os
import argparse 

from .test_config import TestConfig
from .datasource_list import *

def generate_config_files(output_dir, ds_registry, force=False):
    base_output_dir = output_dir
    #Generate all the config files.
    try:
        os.mkdir(base_output_dir)
    except:
        pass
    if not ds_registry:
        print ("Did not find any registry of tests to generate config files for.")
        return

    for ds in ds_registry.dsnames:
        cfg = ds_registry.dsnames[ds]
        if not cfg.config_files_exist(base_output_dir) or force:
            cfg.write_config_files(base_output_dir)

