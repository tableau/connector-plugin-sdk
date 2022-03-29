---
title: Filing a Bug with the SDK
---

If you encounter a bug with the Tableau Connector SDK, please file it as a GitHub issue. We will look at it and respond as soon as we are able.

# Artifacts
When filing a bug on GitHub, attaching the following to the issue:
- A readme file that contains the following (can be in the issue itself):
    - Your name and company
    - A short description of the bug
    - Repro steps with screenshots
    - The product(s) it appears in
    - The exact version of the Tableau products you are using (for example, Desktop 2020.3.1, Server 2020.2.2), as relevant to the bug
    - The exact version of TDVT you are running, if the bug is related to TDVT or discovered during a TDVT run
    - The operating system you are using
- Connector Files. Can be either a folder with the loose connector files or a packaged .taco connector. Should be the latest version of the connector.
- Clean logs showing the error
    - Desktop: This will be in the "My Tableau Repository\Logs" folder for desktop. Remove all items from the folder and then reproduce the bug, then copy the remaining files.
    - Server: The "tsm maintenance ziplogs" command can be used, see [this](https://help.tableau.com/current/server/en-us/logs_loc.htm) page

If the bug is related to TDVT, please also add the following from your TDVT working directory:
- tabquery_logs.zip
- tdvt_actuals_combined.zip
- tdvt_log_combined.txt
- tdvt_output_combined.json
- test_results_combined.csv
- (Optional) The test_results_combined.csv file loaded into our [TDVT Results Workbook](https://github.com/tableau/connector-plugin-sdk/blob/master/tdvt/TDVT%20Results.twbx)
