---
title: Run your Packaged Connector (.taco)
---

Starting in 2019.4 Beta 1, you can load .taco files. To use a connector in earlier Tableau versions, see  [Run Your "Under Development" Connector]({{ site.baseurl }}/docs/share)

# Tableau Desktop
Simply drop your `.taco` file into your `My Tableau Repository/Connectors` and launch Tableau.

# Tableau Server
1. Create a directory for Tableau connectors. For example: `C:\tableau_connectors`
1. Drop your `.taco` file into the folder your created
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

# Signature Verification

To be loaded in Tableau, a `.taco` must be signed by a trusted certificate. If you get the following error:

```
Package signature verification failed during connection creation.
```

the connector couldn't be verified. This can be because the connector is unsigned, or because the certificate's trust chain does not link back to a trusted certificate authority.

For more information about signing a .taco file, see [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign) and [Signature Verification Log Entries]({{ site.baseurl }}/docs/log-entries)

Signature verification was added to Tableau Desktop in 2019.4 and Tableau Server in 2020.1.

## Disabling signature verification

To use an unsigned `.taco` file, you can disable signature verification.

On Tableau Desktop, you use the following command line argument: `-DDisableVerifyConnectorPluginSignature=true`.

On server, you can disable signature verification by setting the `native_api.disable_verify_connector_plugin_signature` option to 'true' via TSM.