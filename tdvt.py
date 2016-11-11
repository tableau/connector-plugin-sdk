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
    Tableau Datasource Verification Tool
    Run logical queiries and expression tests against datasources.

"""

import os
import sys
#BEGIN Tableau environment specific.
# Rerun with right version
#FLOC = os.path.abspath(os.path.dirname(__file__))
#sys.path.append(os.path.join(FLOC, '..', '..', 'tools', 'python'))
#import venv_launcher
#venv_launcher.rerun_this_script_using('3.4.0', '3.4.0')
#END Tableau environment specific.

from tdvt import tdvt

tdvt.main()
