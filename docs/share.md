---
title: Share Your Connector
---

You've created and tested your connector.
Now you'd like to get the connector, or at least the data that your connector can access, to your users.

**IMPORTANT:** This is beta software and should be used in a test environment.
Do not deploy the connector to a production environment.

You can share the data your connector accesses by connecting to the data, creating an extract, and publishing the extract to Tableau Server or Tableau Online.

Or, if you prefer to have your users test the connector, you can place the connector files in the directories and then run the commands as follows:

**Tableau Desktop:** 

1. Create a directory for Tableau connectors. For example: `C:\tableau_connectors`
1. Put the the folder containing your connector's manifest.xml file in this directory. Each connector should have its own folder. For example: `C:\tableau_connectors\my_connector`
1. Run Tableau using the `-DConnectPluginsPath` command line argument, pointing to your connector directory. For example: 

    ```
    tableau.exe -DConnectPluginsPath=C:\tableau_connectors
    ```

**Tableau Server:** 

1. For each server node, follow Tableau Desktop's steps 1 and 2 above.
1. Set the `native_api.connect_plugins_path` option. For example:

    ```
    tsm configuration set -k native_api.connect_plugins_path -v C:/tableau_connectors 
    ```
  
1. Restart Tableau Server to see the new connector.

If you get a configuration error when you set the option in step 2, try adding the `--force-keys` option to the end of the command.

For information about using TSM to set the option, see [tsm configuration set Options](https://onlinehelp.tableau.com/current/server-linux/en-us/cli_configuration-set_tsm.htm) in the Tableau Server help.
    
