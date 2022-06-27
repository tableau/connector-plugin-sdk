---
title: Run Your Connector
---

Note: the below is intended for connector developers. Customer-facing documentation is available [here](https://help.tableau.com/current/pro/desktop/en-us/examples_connector_sdk.htm).

# Load order and class name collisions

## Tableau 2022.2 and newer
If a connector has the same class as a connector that has already been registered, Tableau will load the connector with the highest connector version number (the `plugin-version` attribute in the connector manifest).

If both connectors have the same version, connector loaded first will have precedence. See the load order below.
## Tableau versions older than 2022.2
If a connector has the same class as a connector that has already been registered, the new connector will be rejected. This means that connectors loaded first have precedence when two connectors share the same class name.

## Load order
Tableau loads connectors by directory in the following order:
1. Built-in Tableau connectors
1. Connectors located in ``C:\Program Files\Tableau\Connectors` (Windows) or `/opt/tableau/connectors` (Linux)
1. Connectors located in `My Tableau Repository/Connectors`
1. (Optional) Connectors in the dev path specified by `-DConnectPluginsPath`

# Run Your Packaged Connector (TACO file)

Starting in 2019.4, you can load packaged connectors (otherwise known as TACO files). To use a connector in earlier Tableau versions, or to run an unpackaged connector, see [Run Your "Under Development" Connector]({{ site.baseurl }}/docs/run-taco#run-your-under-development-connector) below.

## Run a packaged connector in Tableau Desktop
1. Copy the .taco file into your My Tableau Repository/Connectors directory.
    - Windows: `C:\Users\\[Windows User]\Documents\My Tableau Repository\Connectors`
    - macOS: `/Users/[user]/Documents/My Tableau Repository/Connectors`
1. Launch Tableau Desktop.

## Run a packaged connector in Tableau Prep Builder
1. Copy the .taco file to your My Tableau Prep Repository\Connectors directory:
    - Windows: `C:\Users\\[Windows User]\Documents\My Tableau Prep Repository\Connectors`
    - macOS: `/Users/[user]/Documents/My Tableau Prep Repository/Connectors`
1. Launch Tableau Prep Builder.

## Run a packaged connector in Tableau Server
### Option 1 (Preferred, available in Tableau 2021.2 and newer)
For each machine:
1. Drop your `.taco` file into the following directory:
    - Windows: `C:\Program Files\Tableau\Connectors`
    - Linux: `/opt/tableau/connectors`
1. Restart Tableau Server

### Option 2
For each machine:
1. Drop your `.taco` file into the following directory:
    - `[Tableau_Server_Installation_Directory]/data/tabsvc/vizqlserver/Connectors`
1. To enable your connector for Prep, you also need to add your taco to the following locations:
    - Tableau Prep Conductor: `[Tableau_Server_Installation_Directory]/data/tabsvc/flowprocessor/Connectors`
    - Tableau Flow Web Authoring: `[Tableau_Server_Installation_Directory]/data/tabsvc/flowqueryservice/Connectors` or `[Tableau_Server_Installation_Directory]/data/tabsvc/flowminerva/Connectors/`, depending on which directory exists
1. Restart your server.

### Option 2 (For in-development connectors)
1. Create a directory for Tableau connectors. This needs to be the same path on each machine, and on the same drive as the server is installed on. For example:
`C:\tableau_connectors`
1. Copy your packaged connector file (with a .taco filename extension) into  the folder your created on each node.
1. Set the `native_api.connect_plugins_path` option. For example:

    ```
    tsm configuration set -k native_api.connect_plugins_path -v C:/tableau_connectors
    ```

    If you get a configuration error during this step, try adding the `--force-keys` option to the end of the command.

1. Apply the pending configuration changes.  This restarts the server.

    ```
    tsm pending-changes apply
    ```

    Note that whenever you add, remove, or update a connector, you need to restart the server to see the changes.

For information about using TSM to set the option, see [tsm configuration set Options](https://onlinehelp.tableau.com/current/server-linux/en-us/cli_configuration-set_tsm.htm) in the Tableau Server Help.

## Verify the signature

To be loaded in Tableau, a packaged connector must be signed by a trusted certificate.

__Note:__ Signature verification was added to Tableau Desktop in 2019.4 and Tableau Server in 2020.1.

If the connector can't be verified, you will see the following error:
`Package signature verification failed during connection creation`

This can happen because the connector is unsigned, because the certificate's trust chain does not link back to a trusted certificate authority, or because a previously valid certificate has expired.

For more information about signing a packaged connector, see [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign) and [Signature Verification Log Entries]({{ site.baseurl }}/docs/log-entries)

### Disabling signature verification

To use an unsigned packaged connector, you can disable signature verification.

- On Tableau Desktop, you use this command:
`-DDisableVerifyConnectorPluginSignature=true`

- On server, you can disable signature verification by setting  `native_api.disable_verify_connector_plugin_signature` to true via TSM.

# Run Your Under Development Connector
## Set up Tableau Desktop

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
1. Run Tableau using the `-DConnectPluginsPath` command-line argument and pointing to your connector directory. For example:
    ```
    /Applications/Tableau\ Desktop\[version].app/Contents/MacOS/Tableau -DConnectPluginsPath=/Users/[username]/tableau_connectors

    ```

## Set up Tableau Server

1. For each server node:
    - Create a directory for Tableau connectors. This needs to be the same path on each machine, and on the same drive as the server is installed on. For example:
`C:\tableau_connectors`
    - Put the folder containing your connector's manifest.xml file in this directory. Each connector should have its own folder. For example:
`C:\tableau_connectors\my_connector`

1. Set the `native_api.connect_plugins_path` option. For example:
    ```
    tsm configuration set -k native_api.connect_plugins_path -v C:/tableau_connectors
    ```
    If you get a configuration error during this step, try adding the `--force-keys` option to the end of the command.

1. Apply the pending configuration changes to restart the server:
    `tsm pending-changes apply`

    __Note:__ Whenever you add, remove, or update a connector, you must restart the server to see the changes.

For information about using TSM to set the option, see [tsm configuration set Options](https://onlinehelp.tableau.com/current/server-linux/en-us/cli_configuration-set_tsm.htm) in the Tableau Server Help.
