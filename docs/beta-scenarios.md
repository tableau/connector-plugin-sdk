# Beta Testing Connectors in the Extension Gallery  
-------

Welcome to the Beta of the Connectors in the Extension Gallery. Tableau has worked closely with a number of its Technology Partners to create connectors for their platform. These connector plugins will replace having to connect to your data using the "Other ODBC/JDBC" connector, and provide a smooth and performant connection to these databases. Installing the new connector only takes a few minutes and you'll be able to see the difference for yourself.
We've provided a few test scenarios below, which may take between 10 and 20 minutes to run through to ensure the connector will work with your environment.

Once you've downloaded a connector and tried these scenarios we'd love to hear from you about your experience! **Please submit feedback to us through the connector-specific feedback form found on the [Extension Gallery](https://extensiongallery.tableau.com/connectors).** Thanks for  participating!

### Gaining access to Beta Connectors in the Gallery:
* Go to https://extensiongallery.tableau.com/
On the top right hand corner of the screen, click 'Sign In' and follow the sign in process using your tableau.com login credentials.
* Click on your user icon in the top right hand corner and select 'Sign up for Connectors Beta'.
* Click the 'Sign Up' button (the page will automatically refresh and you will now see any Beta connectors available for testing)  

### Notes and Known Issues
* The Connectors are compatible with Tableau Desktop and Tableau Server versions 2019.4 and later unless otherwise stated.
* As of version 2020.3, Connectors in the Extension Gallery are not compatible with Tableau Online or Tableau Prep

### FAQs and Troubleshooting
If you run into issues, please share in the survey, but also feel free to reach out directly to our team.

## Test Scenario 1 - Installing the Connector
### Tableau Desktop
From the [Extension Gallery](https://extensiongallery.tableau.com/connectors), download a connector and follow the instructions listed on the Extension Gallery for the connector to become available in Tableau Desktop.

Depending on the Connector, you may also need to download the database driver. Instructions to do so are listed in the Extension Gallery for the given connector. Make sure to follow the driver instructions found on the Extension Gallery installation instructions.

### Tableau Server
**Option 1: Single Node**  
1. Drop your .taco file into <code>[Your Tableau Server Install Directory]/data/tabsvc/vizqlserver/Connectors</code>  
On a default install, this will be in the ProgramData folder. For example: <code>C:\ProgramData\Tableau\Tableau Server\data\tabsvc\vizqlserver\Connectors</code>  
2. Restart your server.  
**Option 2: Multiple Node**  
1. Create a directory for Tableau connectors. This needs to be the same path on each machine. For example:
<code>C:\tableau_connectors</code>
2. Copy your packaged connector file (with a .taco filename extension) into the folder your created on each node.  
3. Set the <code>native_api.connect_plugins_path</code> option. For example:  
        tsm configuration set -k native_api.connect_plugins_path -v C:/tableau_connectors  
If you get a configuration error during this step, try adding the '--force-keys' option to the end of the command.  

4. Apply the pending configuration changes. This restarts the server.
        tsm pending-changes apply  
*Note that whenever you add, remove, or update a connector, you need to restart the server to see the changes.*

### Driver Installations for JDBC Drivers
**Windows:**
1. Download the JDBC driver
2. Move the downloaded .jar file to <code>C:\Program Files\Tableau\Drivers.</code>
**Linux:**  
Download the JDBC driver. After you download the .jar file, copy it to this location on the Linux computer: <code>/opt/tableau/tableau_driver/jdbc</code>  
If the directory does not exist, create it and make sure it is readable by the "tableau" user. To do this:
1. Create the directory:
        sudo mkdir -p /opt/tableau/tableau_driver/jdbc
2. Copy the downloaded driver file to the location, replacing <code>[/path/to/file]</code> with the path and <code>[driver file name]</code> with the name of the driver you downloaded:
        sudo cp [/path/to/file/][driver file name].jar /opt/tableau/tableau_driver/jdbc
3. Set permissions so the file is readable by the "tableau" user, replacing [driver file name] with the name of the driver you downloaded:
        sudo chmod 755 /opt/tableau/tableau_driver/jdbc/[driver file name].jar

## Test Scenario 2 - Replacing a Datasource to an Existing Workbook
### Tableau Desktop
If you have a Workbook that connects to the database already via ODBC/JDBC, replace the existing datasource with the new connector.
1. Make sure you've completed Scenario 1.
2. Open an existing Workbook.
3. Create a new datasource <code>Data > New Data</code>, and select the new connector.
4. Select the connector you downloaded from the Extension Gallery and fill out the information in the dialog box once prompted.
5. Create an identical data source as the one you are about to replace (same tables and joins, or customer SQL).
6. Navigate to a Sheet within the Workbook (or create a new one). You should have two data sources now.
        DB - New Connector
        DB - ODBC
7. Replace the datasource <code>Data > Replace Data Source...</code>
8. Interact with the Sheets and Dashboard as you had previously to verify the performance and the accuracy of the data.

## Test Scenario 3 - Publishing that Workbook to Tableau Server
After completing test scenarios 1 and 2, the next step is to publish your Workbook with the new datasource to Tableau Server

1. From the Workbook in Test Scenario 2 select <code>Server > Publish Workbook</code> from the main menu.
2. Make sure you are already logged in to the server you published the connector to in Test Scenario 1.
3. Select a relevant Project and Name for your Workbook and click Publish.
4. View the Workbook on Tableau Server and verify the Workbook performance and accuracy.

## Test Scenario 4 - Replacing a published datasource for a Workbook on Tableau Server
After completing the previous steps, verify that you can replace a published datasource from Tableau Server for a Workbook already in use. This is effectively a combination of Test Scenario 2 and 3 except performed on an existing Workbook connected to an existing published datasource. We recommend keeping a local copy with the original connector available for comparison/roll-back in case of an issue.

1. Navigate to Tableau Server and download a Workbook connected to a published datasource.
2. Create a new datasource <code>Data > New Data</code>, and select the new connector.
3. Select the connector you downloaded from the Extension Gallery and fill out the information in the dialog box once prompted.
4. Create an identical data source as the one you are about to replace (same tables and joins, or customer SQL).
Navigate to a Sheet within the Workbook (or create a new one). You should have two data sources:
   * DB - New Connector
   * DB - ODBC
5. Replace the datasource (Data > Replace Data Source...)
Interact with the Sheets and Dashboard as you had previously to verify the performance and the accuracy of the data.
6. From the Workbook select <code>Server > Publish Workbook</code> from the main menu.
7. Make sure you are already logged in to the server you published the connector to in Test Scenario 1.
8. Keep the existing Project and Name for your Workbook and click Publish.
9. Click Okay to overwrite the existing Workbook when prompted.
10. View the Workbook on Tableau Server and once again verify the Workbook performance and accuracy.

<br>

*Thank you for validating your connector through the Beta Test Scenarios!*

**Please share your feedback using the connector-specific survey on the [Extension Gallery](https://extensiongallery.tableau.com/Connectors)**
