---
title: Share Your Connector
---

You've created and tested your connector.
Now you'd like to get the connector, or at least the data that your connector can access, to your users.

**IMPORTANT:** This is beta software and should be used in a test environment.
Do not deploy the connector to a production environment.

You can share the data your connector accesses by connecting to the data, creating an extract, and publishing the extract to Tableau Server or Tableau Online.

Or, if you prefer to have your users test the connector, you can place the connector files in the directories and then run the commands as follows:

**Tableau Desktop:** This is the same as developing the connector.
Place the files into a subdirectory you create, and then use the -DConnectPluginsPath command line argument.  For example, place your plugin files in `C:\tableau_connectors\myconnector` and then start Tableau:

```
tableau.exe -DConnectPluginsPath =C:\tableau_connectors
```

**Tableau Server:** Follow the same instructions as Tableau Desktop for each server node.
Then set this option: "native_api.connect_plugins_path: C:/tableau_connectors".
For information about using TSM to do this, see [tsm configuration set Options](https://onlinehelp.tableau.com/current/server-linux/en-us/cli_configuration-set_tsm.htm) in the Tableau Server help.

For example:

```
tsm configuration set -k native_api.connect_plugins_path -v C:/tableau_connectors
```
