---
title: Test Your Connector Using Manual Tests
---
After you create your connector and validate it using TDVT (Tableau Datasource Verification Tool), Tableau's automated testing tool for testing Tableau connnectivity to a database, you should confirm that your connector works as expected by completing a series of manual tests for quality assurance. This article outlines the manual tests to perform.

## Before you begin  

Be sure that you complete all the following steps before you begin the manual tests for your connector.
1.	Make sure your computer or virtual machine is running Windows, macOS or Linux.
1.	Install and run Tableau Desktop and Tableau Server.
1.	Install an ODBC or JDBC driver for your database on Tableau Desktop and Tableau Server
1.	Create a directory for Tableau connectors. Each connector must have its own folder.

    For example: D:\tableau_connectors contains two subfolders (postgres_jdbc and postgres_odbc), one for each connector.

    ![]({{ site.baseurl }}/assets/mt-folders.png)

### On Tableau Desktop

5. Launch Tableau Desktop using `-DConnectPluginsPath` command line argument, pointing to your connector directory. For example:

    On Windows:

    ```
       D:\>"C:\Program Files\Tableau <version>\bin\tableau.exe" -DConnectPluginsPath=D:\tableau_connectors
    ```

    On macOS:

    ```
       "/Applications/Tableau Desktop <version>.app/Contents/MacOS/Tableau" -"DConnectPluginsPath=/var/tmp/plugins"
    ```

    Replace `version` with the version of Tableau that you're running, for example, Tableau 2019.2.

### On Tableau Server

6.	For each server node, follow step 4 above under **Before you begin**.
7.	Set the native_api.connect_plugins_path option. For example:

    ```
    tsm configuration set -k native_api.connect_plugins_path -v D:/tableau_connectors 
    ```

    If you get a configuration error during this step, try adding the `--force-keys` option to the end of the command.

    Note: On Linux, make sure the connectors folder can be accessed by tsm. For example,

    ```
    tsm configuration set -k native_api.connect_plugins_path -v /var/tmp/plugins –force-keys
    ```

8.	Run the following command to apply the pending configuration changes. This will restart the server.

    ```
    tsm pending-changes apply
    ```

For more information about tsm, see tsm Command Line Reference in [Tableau Server on Windows Help](https://onlinehelp.tableau.com/current/server/en-us/cli_configuration-set_tsm.htm) or [Tableau Server on Linux Help](https://onlinehelp.tableau.com/current/server-linux/en-us/tsm.htm).


## Test your connector with Tableau Desktop 

### Check Company Name
Open Tableau Desktop and under **To a Server**, click **More…**

![]({{ site.baseurl }}/assets/mt-company-name.png)
 
If your company name doesn't display, check to see if **company name** is defined in your manifest.xml file. 

```
<vendor-information>
    <company name="Company Name"/>
</vendor-information>
```
### Connect to the database with valid credentials

Connect and cancel. 

* After you click your connector, close the window. It should return to the previous window without error.
 
   ![]({{ site.baseurl }}/assets/mt-cancel.png) 

Make valid entries in each field (Server, Username, Password, Port, etc.) and verify that you can connect.

* Verify that the default Connection name is correct, and that you can change it.
 
  ![]({{ site.baseurl }}/assets/mt-cconnection-name.png) 

* Verify that you can connect using all supported methods of authentication.
 
   ![]({{ site.baseurl }}/assets/mt-connect-auth.png) 

* Verify that you can connect to a data source with SSL, if applicable.

   Select the **Require SSL** check box, and then click **Sign In**.

   ![]({{ site.baseurl }}/assets/mt-connect-ssl.png) 
   
* Verify that you can duplicate the data source and that the duplicate source name has "(copy)" appended to the end.

   ![]({{ site.baseurl }}/assets/mt-duplicate.png) 
  
   ![]({{ site.baseurl }}/assets/mt-duplicate-copy.png) 
 
* Verify that the data source connection properties are correct.
 
   ![]({{ site.baseurl }}/assets/mt-prop-menu.png) 

   ![]({{ site.baseurl }}/assets/mt-properties.png) 

### Test extracts

* Create an extract. 

  Right-click the data source, then click **Extract Data** in the context menu. Verify that you can create an extract without errors.

  ![]({{ site.baseurl }}/assets/mt-create-extract.png) 

* Refresh an extract.

   ![]({{ site.baseurl }}/assets/mt-refresh-extract.png) 
 
   For more information, see [Refresh Extracts](https://onlinehelp.tableau.com/current/pro/desktop/en-us/extracting_refresh.htm) in Tableau Desktop and Web Authoring Help.

### Edit your connection 

Change all possible items and verify that changes are applied.

   * Right-click the data source and click **Edit Data Source**.

      ![]({{ site.baseurl }}/assets/mt-edit-data-source.png) 
 
   * The worksheet opens in Tableau. In the left pane, under **Connections**, click the drop-down menu next to the server name and click **Edit Connection**.

      ![]({{ site.baseurl }}/assets/mt-edit-connection.png) 
 
   * Change something, for example, change the server.

      ![]({{ site.baseurl }}/assets/mt-change-server.png) 
 
   * After you click **Sign In**, you should see the new server name under **Connections**.

      ![]({{ site.baseurl }}/assets/mt-new-server.png) 
 
### Open a workbook with the connector missing

1. Create a workbook with a live connection using your connector and save as a .twb file. 

1. Close Tableau Desktop and remove your connector.

1. Open Tableau Desktop and open the workbook you created. Verify that an error message displays:

   ![]({{ site.baseurl }}/assets/mt-missing-connector-error.png) 
 
### Connect to a published data source with the connector missing

1. Remove your connector.

1. Use Tableau Desktop to connect to a published data source with an extract. You should be able to connect without errors.

1. Use Tableau Desktop to connect to a published data source without an extract. Verify that an error message displays:

   ![]({{ site.baseurl }}/assets/mt-no-extract-error.png) 

### Download a workbook

1. Remove your connector.

1. Download a workbook with an extract from Tableau Server and open it in Tableau Desktop. The workbook should open without errors.

1. Download a workbook without an extract from Tableau Server and open it in Tableau Desktop. Verify that an error message displays:

   ![]({{ site.baseurl }}/assets/mt-wkbk-no-extract-error.png) 

### Test localization

Change the language to any language but English (United States).

1. From **Help**, select **Choose Language**, and then select a language.

      ![]({{ site.baseurl }}/assets/mt-loc.png) 

1. Restart Tableau Desktop.

1. Connect to your data source again and verify the localized text.
 

### Connect to the correct database with the wrong credentials.

Verify that an error message appears and that it says 'Invalid username or password'. Some features may not work if Tableau cannot correctly interpret a bad password error. In this case you will see a generic error message instead of 'Invalid username or password': 

![]({{ site.baseurl }}/assets/mt-wrong-cred.png) 

### [Optional] Test driver version

If you defined a minimum driver version in your connector, test connecting to the correct database with the correct credentials, but with an old driver version installed. 

If applicable, install an older version of the driver, and then connect using your connector. The “Download and install the drivers” link should appear on the Sign In dialog.

For example, in Mariadb, &lt;driver-version min='3.0'/&gt; is defined in connection-resolver.tdr. You can install a 2.0 driver to test that the connector does not use the old driver and instead, shows the "Download and install the drivers" link.
 
![]({{ site.baseurl }}/assets/mt-no-connector-error.png)  

## Test your connector with Tableau Server 

### Publish to Tableau Server

Perform the publishing tests listed below. For more information about publishing, see the publishing resources listed at the end of this section.

* Publish a *workbook without an extract* to Tableau Server *with the connector* installed on the server.


    The workbook should publish without errors.

   
* Publish a *data source with an extract* to Tableau Server *with the connector* installed on the server.

    The workbook should publish without errors.

    Make sure **Allow refresh access** is selected as an authentication option. To do this, 

    1. In the **Authentication** section in the Publish Data Source dialog box, next to **Refresh not enabled**, click **Edit**. 

    1. Under **Authentication**, select **Allow refresh access** from the drop-down list.

        ![]({{ site.baseurl }}/assets/mt-pub-allow-refresh.png)  


* Publish a *workbook without an extract* to Tableau Server *with the connector* installed on the server.  Do not embed credentials when you publish the workbook.

    Open the published workbook that doesn't have embedded credentials. 

    Verify that a Sign In dialog opens.

    ![]({{ site.baseurl }}/assets/mt-embed-credentials.png)  
 
    For more information, see [Set Credentials for Accessing Your Published Data](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publishing_sharing_authentication.htm) in the Tableau Desktop and Web Authoring Help.


#### Publishing resources

For information about publishing a data source, see [Publish a Data Source](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publish_datasources.htm) in the Tableau Desktop and Web Authoring Help. 

For information about publishing a workbook, see [Comprehensive Steps to Publish a Workbook](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publish_workbooks_howto.htm) in the Tableau Desktop and Web Authoring Help.


### Test extract refreshes

Refresh the extract on Tableau Server with the connector installed on the server.

* Publish a *workbook with an extract* to Tableau Server *with the connector* installed on the server.

    Open the workbook with an extract on Tableau Server and refresh the extract.

    ![]({{ site.baseurl }}/assets/mt-wkbk-extract-refresh.png)  

    The extract should refresh without errors.
 

* Open a data source with an extract on Tableau Server and refresh the extract.

    ![]({{ site.baseurl }}/assets/mt-ds-extract-refresh.png)  

    The extract should refresh without errors.
 
### Create and open workbooks and data sources on Tableau Server

* Create a new workbook on Tableau Server with the connector installed on the server. For example:

    1. Sign in to Tableau Server.
    1. Go to **Explore**, then click **Create**.
    1. Select **Workbook** in the drop-down menu.

        ![]({{ site.baseurl }}/assets/mt-wkbk-explore.png)

    1. Select your connector. In this example, the connector name is MariaDB.

        ![]({{ site.baseurl }}/assets/mt-wkbk-mariadb.png)

    1. Enter the required information to sign in.

        ![]({{ site.baseurl }}/assets/mt-wkbk-signin.png)

    1. After you connect to the data source, you should be able to create a new workbook and save it on the server.

    **Note:** Web authoring (creating a new connection from the web) is not currently available for all connector superclasses, and in those cases your connector won't appear on the list of connectors on Tableau Server. If you can publish a workbook or data source using your connector to your server, then your connector is loaded correctly, even if you can't see it on the list of connectors.

