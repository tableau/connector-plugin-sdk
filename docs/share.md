---
title: Run Your "Under Development" Connector
---

**IMPORTANT:** This is beta software and should be used in a test environment.
Do not deploy the connector to a production environment.

# Set up Tableau Desktop

__For Windows:__
1. Create a directory for Tableau connectors. For example:   
`C:\tableau_connectors`
1. Put the folder containing your connector's manifest.xml file in this directory. Each connector should have its own folder. For example:    
`C:\tableau_connectors\my_connector`
1. Run Tableau using the <span style="font-family: courier new">-DConnectPluginsPath</span> command-line argument, pointing to your connector directory. For example:   
`tableau.exe -DConnectPluginsPath=C:\tableau_connectors`

__For macOS:__

__Note:__ In the steps below, replace [username] with your name (for example /Users/agarcia/tableau_connectors) and [version] with the version of Tableau that you’re running (for example, 2019.3.app).

1. Create a directory for Tableau connectors. For example:   
`/Users/[username]/tableau_connectors`
1. Put the folder containing your connector's manifest.xml file in this directory. Each connector should have its own folder. For example:   
`/Users/[username]/tableau_connector/my connector`
1. Run Tableau using the <span style="font-family: courier new">-DConnectPluginsPath</span> command-line argument and pointing to your connector directory. For example:    
    ```
    /Applications/Tableau\ Desktop\[version].app/Contents/MacOS/Tableau -DConnectPluginsPath=/Users/[username]/tableau_connectors

    ```

# Set up Tableau Server

1. For each server node:
    - Create a directory for Tableau connectors. For example:   
`C:\tableau_connectors`
    - Put the folder containing your connector's manifest.xml file in this directory. Each connector should have its own folder. For example:    
`C:\tableau_connectors\my_connector`

1. Set the `native_api.connect_plugins_path` option. For example:  
    ```
    tsm configuration set -k native_api.connect_plugins_path -v C:/tableau_connectors
    ```   
    If you get a configuration error during this step, try adding the <span style="font-family: courier new">--force-keys</span> option to the end of the command.

1. Apply the pending configuration changes to restart the server:   
    `tsm pending-changes apply`    
    
    __Note:__ Whenever you add, remove, or update a connector, you must restart the server to see the changes.

For information about using TSM to set the option, see [tsm configuration set Options](https://onlinehelp.tableau.com/current/server-linux/en-us/cli_configuration-set_tsm.htm) in the Tableau Server Help.

