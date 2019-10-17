---
title: How to Run your Packaged Connector (Taco)
---

The ability to load taco files was added in 2019.4 Beta 1. For loading un-packaged connectors in earlier versions of Tableau, refer to [How to Run Your "Under Development" Connector]({{ site.baseurl }}/docs/share)

# Tableau Desktop
Simply drop your taco file into your `My Tableau Repository/Connectors` and launch Tableau.

# Tableau Server
1. Create a directory for Tableau connectors. For example: `C:\tableau_connectors`
1. Drop your taco file into the folder your created
1. Set the `native_api.connect_plugins_path` option. For example:

    ```
    tsm configuration set -k native_api.connect_plugins_path -v C:/tableau_connectors
    ```

    If you get a configuration error during this step, try adding the `--force-keys` option to the end of the command.

1. Apply the pending configuration changes.  This will restart the server.

    ```
    tsm pending-changes apply
    ```

    Note that whenever you add, remove, or update a connector, you need to restart the server to see the changes.

For information about using TSM to set the option, see [tsm configuration set Options](https://onlinehelp.tableau.com/current/server-linux/en-us/cli_configuration-set_tsm.htm) in the Tableau Server help.

# Troubleshooting

## Package signature verification failed during connection creation.
This means that the connector couldn't be verified. To be loaded in Tableau, a .taco must be signed by a trusted certificate. For more information about signing tacos, refer to [How to Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign) and [Signature Verification Log Entries]({{ site.baseurl }}/docs/log-entries)

As a workaround, you can disable taco verification in Tableau by using the command line argument `-DDisableVerifyConnectorPluginSignature=true`.
