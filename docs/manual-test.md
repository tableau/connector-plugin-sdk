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

6.	For each server node, follow step 4 above.
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

* After you click your connector, close the window. It should return to previous window without error.
 
   ![]({{ site.baseurl }}/assets/mt-cancel.png) 

Make valid entries in each field (Server, Username, password, Port etc.) and verify that you can connect.

* Verify that the default Connection name is correct, and that you can change it.
 
  ![]({{ site.baseurl }}/assets/mt-cconnection-name.png) 

* Verify that you can connect using all supported methods of authentication.
 
   ![]({{ site.baseurl }}/assets/mt-connect-auth.png) 

* Verify that you can connect to a data source with SSL, if applicable.

   Select the **Require SSL** check box, and then click **Sign In**.

   ![]({{ site.baseurl }}/assets/mt-connect-ssl.png) 
 
* Duplicate the data connection.

   ![]({{ site.baseurl }}/assets/mt-dup.png) 

   Verify that data source was duplicated and the duplicate data source name has “(copy)” appended to the end.

   ![]({{ site.baseurl }}/assets/mt-copy.png)  
 
* Verify that the data source connection properties are correct.
 
    ![]({{ site.baseurl }}/assets/mt-prop-menu.png) 

    ![]({{ site.baseurl }}/assets/mt-properties.png) 

* Check that you can refresh the data source. Right-click the data source, then click **Refresh** in the context menu, or press **F5**.

   ![]({{ site.baseurl }}/assets/mt-refresh.png) 
 
   For more information, see [Refresh Data Sources](https://onlinehelp.tableau.com/current/pro/desktop/en-us/refreshing_data.htm) in Tableau Desktop and Web Authoring Help. 

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
 
### Create a workbook

1. Create a workbook connected to your connector using a live connection and save it as a .twb file. 

1. Close Tableau Desktop and remove the connector before launching Desktop again. 

1. Open the workbook. 

1. Check the error message. Here is an example:

      ![]({{ site.baseurl }}/assets/mt-twb-error.png) 
 

### Test localization

Change the language to any language but English (United States).

1. From **Help**, select **Choose Language**, and then select a language.

      ![]({{ site.baseurl }}/assets/mt-loc.png) 

1. Restart Tableau Desktop with your connector from a command window using the `-DConnectPluginsPath` argument.

1. Connect to your data source again.
 

### Connect to the correct database with valid credentials, but without the driver installed

Verify that the "Download and install the drivers" link appears in the Sign In dialog box:

![]({{ site.baseurl }}/assets/mt-download-driver.png) 
 
### Connect to the correct database with the wrong credentials

Verify that an error message appears: 

![]({{ site.baseurl }}/assets/mt-wrong-cred.png) 

### Test without the connector installed 

* Access a published *data source with an extract* from Tableau Desktop *without the connector* installed.

   You should be able to connect to the data source with an extract without errors.

* Access a published *data source without an extract* from Tableau Desktop *without the connector* installed.

   Verify that an error message appears:

    ![]({{ site.baseurl }}/assets/mt-no-connector-error.png)   

* Download a workbook *without an extract* from Tableau Server, and then re-open it in Tableau Desktop *without the connector* installed.

   Verify that an error message appears:

    ![]({{ site.baseurl }}/assets/mt-no-plugin-error.png)    
  

* Download a workbook *with an extract* from Tableau Server, and then re-open it in Tableau Desktop *without the connector* installed.

   The workbook should open without errors.

### [Optional] Test driver version

If you defined a minimum driver version in your connector, test connecting to the correct database with the correct credentials, but with an old driver version installed. 

If applicable, install an older version of the driver, and then connect using your connector. The “Download and install the drivers” link should appear on the Sign In dialog.

For example, in Mariadb, &lt;driver-version min='3.0'/&gt; is defined in connection-resolver.tdr. You can install a 2.0 driver to test that the connector does not use the old driver and instead, shows the "Download and install the drivers" link.
 
![]({{ site.baseurl }}/assets/mt-no-connector-error.png)  

## Test your connector with Tableau Server 

### Publish to Tableau Server

Perform the publishing tests listed below. For more information about publishing, see the publishing resources listed at the end of this section.

* Publish a data source to Tableau Server *without* the connector installed on the server. (If the connector is on Tableau Server, you need to remove it for this test.)

    Verify that an error message appears:

    ![]({{ site.baseurl }}/assets/mt-publish-fail.png) 

* Publish a workbook to Tableau Server *without* the connector installed on the server. (If the connector is on Tableau Server, you need to remove it for this test.)

    Like the preceding test, you should see a publish failure error message.

    
* Publish a *workbook without an extract* to Tableau Server *with the connector* installed on the server.

    The workbook should publish without errors.

   
* Publish a *workbook with an extract* to Tableau Server *with the connector* installed on the server.

    The workbook should publish without errors.

 
* Publish a *data source with an extract* to Tableau Server *with the connector* installed on the server.

    The workbook should publish without errors.

    Make sure **Allow refresh access** is selected as an authentication option. To do this, 

    1. In the **Authentication** section in the Publish Data Source dialog box, next to **Refresh not enabled**, click **Edit**. 

    1. Under **Authentication**, select **Allow refresh access** from the drop-down list.

        ![]({{ site.baseurl }}/assets/mt-pub-allow-refresh.png)  


* Publish a *data source without an extract* to Tableau Server *with the connector* installed on the server.

    The workbook should publish without errors.

    
* Publish a *workbook without an extract* to Tableau Server *without the driver* installed on the server.

    Verify that an error message appears:

    ![]({{ site.baseurl }}/assets/mt-missing-driver.png)  

* Publish a *workbook with an extract* to Tableau Server *without the driver* installed on the server.

    The workbook with an extract should publish without errors.

* Publish a *data source without an extract* to Tableau Server *without the driver* installed on the server.

    Verify that an error message appears:

     ![]({{ site.baseurl }}/assets/mt-driver-error.png)  

* Publish a *data source with an extract* to Tableau Server *without the driver* installed on the server.

    The data source with an extract should publish without errors.

* Verify that a Sign In dialog opens if you didn't embed credentials when you published the workbook.

    Open a published workbook that doesn't have embedded credentials. 

    ![]({{ site.baseurl }}/assets/mt-embed-credentials.png)  
 
    For more information, see [Set Credentials for Accessing Your Published Data](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publishing_sharing_authentication.htm) in the Tableau Desktop and Web Authoring Help.


#### Publishing resources

For information about publishing a data source, see [Publish a Data Source](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publish_datasources.htm) in the Tableau Desktop and Web Authoring Help. 

For information about publishing a workbook, see [Comprehensive Steps to Publish a Workbook](https://onlinehelp.tableau.com/current/pro/desktop/en-us/publish_workbooks_howto.htm) in the Tableau Desktop and Web Authoring Help.


### Test extract refreshes

Refresh the extract on Tableau Server with the connector installed on the server.

* Open the workbook with an extract on Tableau Server and refresh the extract.

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


* Open a published workbook on Tableau Server *with the connector* installed on the server.

    The workbook should open without errors.

* Create a new workbook on Tableau Server *without the driver* installed on the server.

    Verify that an error message appears.

    ![]({{ site.baseurl }}/assets/mt-wkbk-driver-error.png)

* Open a published workbook on Tableau Server *without the connector* installed on the server.

    Verify that an error message appears.

    ![]({{ site.baseurl }}/assets/mt-wkbk-signin.png)

* Open a published data source on Tableau Server and create a new workbook *without the connector* installed on the server.

    Verify that an error message appears.

     ![]({{ site.baseurl }}/assets/mt-ds-error.png)

 
### [Optional] Test driver version 

If you defined a minimum driver version in your connector, install an older version of that driver and try making a connection with your connector.

Verify that an error message appears:

 ![]({{ site.baseurl }}/assets/mt-driver-required.png)


### Restart the server with and without your connector

Launch tsm with the connector installed, then remove the connector and re-launch tsm.

1. If you haven't already, do steps 6 and 7 in **Before you begin** under the **On Tableau Server** section to launch tsm with your connector. 
1. Then delete the directory that contains your connector. 
1. Run the following command to re-launch tsm.

    ```
    tsm restart 
    ```

    Server should restart.
