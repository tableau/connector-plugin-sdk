---
title: Run Your Packaged Connector (TACO file)
---

This section describes how to load packaged connectors (otherwise known as TACO files). A TACO file has a .taco filename extension. 

**Note:** To use a connector in a version of Tableau before 2019.4 Beta 1, see  [Run Your "Under Development" Connector]({{ site.baseurl }}/docs/share)

## Run a packaged connector in Tableau Desktop
1. Copy your TACO file into your My Tableau Repository/Connectors directory. 
1. Launch Tableau Desktop.

## Run a packaged connector in Tableau Prep
1. Copy your TACO file into your My Tableau Prep Repository/Connectors directory. 
1. Launch Tableau Prep.

## Run a packaged connector in Tableau Server
### Option 1
For each machine:
1. Drop your TACO file into [Your Tableau Server Install Directory]/data/tabsvc/vizqlserver/Connectors. On a default install, this will be in the ProgramData folder. For example:
`C:\ProgramData\Tableau\Tableau Server\data\tabsvc\vizqlserver\Connectors`
1. Restart your server.


### Option 2
1. Create a directory for Tableau connectors. This needs to be the same path on each machine. For example:   
`C:\tableau_connectors`
1. Copy your TACO file into  the folder your created on each node.
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

This can happen because the connector is unsigned, or because the certificate's trust chain does not link back to a trusted certificate authority.

For more information about signing a packaged connector, see [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign) and [Signature Verification Log Entries]({{ site.baseurl }}/docs/log-entries)

### Disabling signature verification

To use an unsigned packaged connector, you can disable signature verification.

- On Tableau Desktop, you use this command:    
`-DDisableVerifyConnectorPluginSignature=true`

- On server, you can disable signature verification by setting  `native_api.disable_verify_connector_plugin_signature` to true via TSM.
