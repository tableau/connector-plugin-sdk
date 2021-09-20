---
title: Run Manual QA Tests
---
After you create your connector and validate it using TDVT, run these manual quality assurance tests to confirm that your connector works as expected.

## Before you begin

Be sure that you complete all the following steps before you begin the manual tests for your connector.
1.	Make sure your computer or virtual machine is running Windows, macOS, or Linux.
1.	Install and run Tableau Desktop and Tableau Server.
1.	Install an ODBC or JDBC driver for your database on Tableau Desktop and Tableau Server.
1.	Set up your connectors following these [guidelines]({{ site.baseurl }}/docs/run-taco#run-your-under-development-connector).

### On Tableau Desktop

- Launch Tableau Desktop using `-DConnectPluginsPath` command-line argument, pointing to your connector directory. For example:

    On Windows:

    ```
       D:\>"C:\Program Files\Tableau <version>\bin\tableau.exe" -DConnectPluginsPath=D:\tableau_connectors
    ```

    On macOS:

    ```
       "/Applications/Tableau Desktop <version>.app/Contents/MacOS/Tableau" -"DConnectPluginsPath=/var/tmp/plugins"
    ```

    __Note:__ Replace `version` with the version of Tableau that you're running, for example, Tableau 2019.2.

### On Tableau Server

1. Set the native_api.connect_plugins_path option. For example:
    ```
    tsm configuration set -k native_api.connect_plugins_path -v D:/tableau_connectors
    ```
    If you get a configuration error during this step, try adding the `--force-keys` option to the end of the command.
    __Note:__ On Linux, make sure the connectors folder can be accessed by tsm. For example:
    ```
    tsm configuration set -k native_api.connect_plugins_path -v /var/tmp/plugins –force-keys
    ```
1. Run the following command to apply the pending configuration changes. This will restart the server.
    ```
    tsm pending-changes apply
    ```
For more information about tsm, see tsm Command-Line Reference in [Tableau Server on Windows Help](https://onlinehelp.tableau.com/current/server/en-us/cli_configuration-set_tsm.htm) or [Tableau Server on Linux Help](https://onlinehelp.tableau.com/current/server-linux/en-us/tsm.htm).


## Test your connector with Tableau Desktop

__Check company name__
- Open Tableau Desktop, and under **To a Server**, click **More…**.
![]({{ site.baseurl }}/assets/mt-company-name.png)

If your company name doesn't display, make sure your **company name** is defined in the manifest.xml file.

```
<vendor-information>
    <company name="Company Name"/>
</vendor-information>
```
__Connect to the database with valid credentials__

1. Connect and cancel.
After you click your connector, close the window. It should return to the previous window without error.<br/>
![]({{ site.baseurl }}/assets/mt-cancel.png)

1. Make valid entries in each field (Server, Username, Password, Port, and so on) and verify that you can connect.

1. Verify that the default connection name is correct, and that you can change it.<br/>
![]({{ site.baseurl }}/assets/mt-cconnection-name.png)

1. Verify that you can connect using all supported methods of authentication.<br/>
![]({{ site.baseurl }}/assets/mt-connect-auth.png)

1. Verify that you can connect to a data source with SSL, if applicable.
Select the **Require SSL** checkbox, and then click **Sign In**.<br/>
![]({{ site.baseurl }}/assets/mt-connect-ssl.png)

1. Verify that you can duplicate the data source and that the duplicate source name has "(copy)" appended to the end.<br/>
![]({{ site.baseurl }}/assets/mt-duplicate.png)<br/>
![]({{ site.baseurl }}/assets/mt-duplicate-copy.png)

1. Verify that the data source connection properties are correct.<br/>
![]({{ site.baseurl }}/assets/mt-prop-menu.png)<br/>
![]({{ site.baseurl }}/assets/mt-properties.png)

__Test extracts__

1. Create an extract.
Right-click the data source, then click **Extract Data**. Verify that you can create an extract without errors.<br/>
![]({{ site.baseurl }}/assets/mt-create-extract.png)

1. Refresh an extract.<br/>
![]({{ site.baseurl }}/assets/mt-refresh-extract.png)

For more information, see [Refresh Extracts](https://onlinehelp.tableau.com/current/pro/desktop/en-us/extracting_refresh.htm) in Tableau Desktop and Web Authoring Help.

__Edit your connection__

Change all possible items and verify that changes are applied.

1. Right-click the data source and click **Edit Data Source**.<br/>
![]({{ site.baseurl }}/assets/mt-edit-data-source.png)
The worksheet opens in Tableau.
1. In the left pane, under **Connections**, click the dropdown menu next to the server name and click **Edit Connection**.<br/>
![]({{ site.baseurl }}/assets/mt-edit-connection.png)
1. Change something. For example, change the server.<br/>
![]({{ site.baseurl }}/assets/mt-change-server.png)
1. After you click **Sign In**, you should see the new server name under **Connections**.<br/>
![]({{ site.baseurl }}/assets/mt-new-server.png)

__Open a workbook with the connector missing__

1. Create a workbook with a live connection using your connector.

1. Save the workbook. The file should have a .twb filename extension.

1. Close Tableau Desktop and remove your connector.

1. Open Tableau Desktop and open the workbook you created. Verify that an error message displays:<br/>
![]({{ site.baseurl }}/assets/mt-missing-connector-error.png)

__Connect to a published data source with the connector missing__

1. Remove your connector.

1. Use Tableau Desktop to connect to a published data source with an extract. You should be able to connect without errors.

1. Use Tableau Desktop to connect to a published data source without an extract. Verify that an error message displays:<br/>
![]({{ site.baseurl }}/assets/mt-no-extract-error.png)

__Download and open a workbook with the connector missing__

1. Remove your connector.

1. Download a workbook with an extract from Tableau Server and open it in Tableau Desktop. The workbook should open without errors.

1. Download a workbook without an extract from Tableau Server and open it in Tableau Desktop. Verify that an error message displays:<br/>
![]({{ site.baseurl }}/assets/mt-wkbk-no-extract-error.png)

__Test localization__
Change the language to any language but English (United States).

1. From **Help**, select **Choose Language**, and then select a language.<br/>
![]({{ site.baseurl }}/assets/mt-loc.png)

1. Restart Tableau Desktop.

1. Connect to your data source again and verify the localized text.

__Connect to the correct database with the wrong credentials__
- Verify that an error message appears, saying "Invalid username or password".
Some features may not work if Tableau cannot correctly interpret a bad password error. In this case, you will see a generic error message instead:<br/>
![]({{ site.baseurl }}/assets/mt-wrong-cred.png)

__[Optional] Test driver version__

If you defined a minimum driver version in your connector, test connecting to the correct database with the correct credentials, but with an old driver version installed.

- If applicable, install an older version of the driver, and then connect using your connector. The “Download and install the drivers” link should appear on the connection dialog.

For example, in Mariadb, &lt;driver-version min='3.0'/&gt; is defined in connection-resolver.tdr. You can install a 2.0 driver to test that the connector does not use the old driver and instead, shows the "Download and install the drivers" link.<br/>
![]({{ site.baseurl }}/assets/mt-no-connector-error.png)

## Test your connector with Tableau Server

__Publish to Tableau Server__

Perform the publishing tests listed below. For more information about publishing, see the publishing resources listed at the end of this section.

* Publish a workbook without an extract to Tableau Server *with the connector* installed on the server.
The workbook should publish without errors.

* Publish a data source with an extract to Tableau Server.
    - Be sure the the connector is installed on the server.
    - Make sure **Allow refresh access** is selected as an authentication option. To do this:
        1. In the Publish Data Source dialog box, under **Authentication**, click __Edit__ next to **Refresh not enabled**.
        1. Under **Authentication**, select **Allow refresh access** from the dropdown list.<br/>
        ![]({{ site.baseurl }}/assets/mt-pub-allow-refresh.png)<br/>
The workbook should publish without errors.

* Publish a workbook without an extract to Tableau Server.
    - Be sure the the connector is installed on the server.  *
    - Be sure not to embed credentials when you publish the workbook.
    - Open the published workbook.
    - Verify that a Sign In dialog opens.<br/>
    ![]({{ site.baseurl }}/assets/mt-embed-credentials.png)<br/>
    For more information, see [Set Credentials for Accessing Your Published Data](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publishing_sharing_authentication.htm) in the Tableau Desktop and Web Authoring Help.


__Find publishing resources__

For information about publishing a data source, see [Publish a Data Source](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publish_datasources.htm) in the Tableau Desktop and Web Authoring Help.

For information about publishing a workbook, see [Comprehensive Steps to Publish a Workbook](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publish_workbooks_howto.htm) in the Tableau Desktop and Web Authoring Help.


__Test extract refreshes__

Refresh the extract on Tableau Server with the connector installed on the server.

* Publish a workbook with an extract to Tableau Server.
    - Be sure the connector is installed on the server.
    - Open the workbook with an extract on Tableau Server and refresh the extract.<br/>
    ![]({{ site.baseurl }}/assets/mt-wkbk-extract-refresh.png)<br/>
    The extract should refresh without errors.

* Open a data source with an extract on Tableau Server and refresh the extract.<br/>
    ![]({{ site.baseurl }}/assets/mt-ds-extract-refresh.png)<br/>
    The extract should refresh without errors.

__Create and open workbooks and data sources on Tableau Server__

Create a workbook on Tableau Server with the connector installed on the server:

1. Sign in to Tableau Server.

1. Under **Explore**, click **Create**.

1. From the dropdown menu, select **Workbook**.<br/>
![]({{ site.baseurl }}/assets/mt-wkbk-explore.png)

1. Select your connector. In this example, the connector name is MariaDB.<br/>
![]({{ site.baseurl }}/assets/mt-wkbk-mariadb.png)

1. Enter the required information to sign in.<br/>
![]({{ site.baseurl }}/assets/mt-wkbk-signin.png)

1. After you connect to the data source, you should be able to create a workbook and save it on the server.

    **Note:** Web authoring (creating a connection from the web) is not currently available for all connector superclasses. In those cases, your connector won't appear on the list of connectors on Tableau Server. If you can publish a workbook or data source using your connector to your server, then your connector is loaded correctly, even if you can't see it on the list of connectors.

## OAuth Connector Test Cases
If your connector supports OAuth Authentication, besides the previous test steps, there are some extra steps you need to verify for OAuth on Tableau Desktop/Server.

### Test an OAuth Connector on Tableau Desktop

__Connect to the database with OAuth tokens__

1. Enter the required information to sign in.<br/>
![]({{ site.baseurl }}/assets/oauth-desktop-dialog.png)
1. A default browser should pop up and you will need authenticate yourself through OAuth, you should see a consent screen like this:(It's a google consent screen for illustration, the actual one you see depends on your Identity Provider)<br/>
![]({{ site.baseurl }}/assets/oauth-google-consent.png)
1. After you allow access, you should see this landing page on your browser:
![]({{ site.baseurl }}/assets/oauth-desktop-complete.png)
1. Then you can close your browser and you should be able to perform the normal manual test steps [here](#Test-your-connector-with-tableau-desktop)

### Test an OAuth Connector on Tableau Server

__Prerequisite__

Follow this [instruction](oauth.md#oauth-on-tableau-server-&-tableau-online) to set up OAuth client for your connector on Server first.

__Test refresing OAuth token on Tableau Server__

If your connector supports oauth, you need to perform this extra step to make sure Tableau can successfully refresh your token.
1. Go to user's server settings page and find the pane for Saved Credentials for Data Sources.

1. Find your connector in the connector list and click **Add** button next to it, which will invoke the OAuth flow, authenticate yourself and we will save the OAuth token securely in Tableau Server.

1. Examine the saved OAuth token. It should contain a username that uniquely identifies you. It can also contain a instanceUrl if your oauthConfig file has OAUTH_SUPPORTS_CUSTOM_DOMAIN enabled.

1. Click the **Test** button next to your saved credential, it will try to refresh the accessToken and you should see a success message.
![]({{ site.baseurl }}/assets/oauth-server-test-token.png)

__Publish OAuth resource to Tableau Server__

The publishing experience for OAuth is different than a username-password connection, 

* Publish a data source with an extract to Tableau Server.
    - Be sure the the connector is installed on the server.
    - Make sure **Embed <username>** is selected as an authentication option. To do this:
        1. For a data source using OAuth, go to the server settings page to add your credential for the data source.<br/>
        ![]({{ site.baseurl }}/assets/oauth-server-addtoken.png)

        1. Then under **Authentication** select **Embed <username>** from the dropdown list.<br/>
        ![]({{ site.baseurl }}/assets/oauth-desktop-publish.png)

The workbook should publish without errors.

* Publish a workbook without an extract to Tableau Server.
    - Be sure the the connector is installed on the server.  *
    - Be sure not to embed credentials when you publish the workbook.
    - Open the published workbook.
    - Verify that a Sign In dialog opens.<br/>
    ![]({{ site.baseurl }}/assets/oauth-server-prompt.png)<br/>
    - Click Signing in should invoke the OAuth flow and after authenticated you will be able to see the content.
