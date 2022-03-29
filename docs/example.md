---
title: Connector Example
---

A Tableau connector is a set of files that describe the UI elements needed to collect user input for creating a connection to a data source, any dialect or customizations needed, a connection string builder, driver resolver, and the ODBC- or JDBC-based driver.

Tableau connector files include:
- __Manifest file__ that tells Tableau about the connector. Tableau uses the name from this file to add it to the list of available connectors in the UI.
- __Tableau Connection Dialog file__ customizes the connection dialog as needed for this connection.
- __Tableau Connection Resolver file__ creates the connection to your file using JavaScript files to define and make the connection.
- __Tableau Dialect file__ identifies which SQL dialect to use.

Tableau provides a base set of connector files that you use to create your own customized connector. You can use the connectivity test harness to validate the connector behavior as you build it.

This diagram shows how the connector interacts with Tableau and the database. Details and examples for these component files are below the diagram.

![]({{ site.baseurl }}/assets/files-sequence.png)

Most of the following examples use the connector for the PostGre SQL database, located in the [postgres_odbc or postgres_jdbc folder](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins).

## ![1]({{ site.baseurl }}/assets/pce-1.png) Manifest File

The Manifest file (manifest.xml)  informs Tableau about your connector and displays the connector name in the Tableau Connect pane.
It's a required file that defines the connector class and description.
The <span style="font-family: courier new">class</span> value is a unique key for your connector and is used in other XML files to apply their customizations and in Tableau workbooks to match connection types.

Each connector is typically based on a "class" such as ODBC or JDBC, and provides additional customizations.

- The <span style="font-family: courier new">class</span> value is a unique key for your connector and is used in other XML files to apply their customizations and in Tableau workbooks to match connection types.
- The <span style="font-family: courier new">name</span> value displays the connector name in the Tableau **Connect** pane.
- You may also specify the vendor information.
- The <span style="font-family: courier new">company name</span> value displays the name of the connector's creator next to the connector name on the Tableau **Connect** pane (for example, Connector Name by Creator).
- The <span style="font-family: courier new">support link</span> value is the URL of a website where users of the connector can get support.


![]({{ site.baseurl }}/assets/manifest-xml.png)

![]({{ site.baseurl }}/assets/pce-connect-pane.png)

## ![2]({{ site.baseurl }}/assets/pce-2.png) Tableau Connection Dialog File

The Tableau Connection Dialog file (.tcd) is optional. By default, your connector inherits a connection dialog from its parent (defined by <span style="font-family: courier new">superclass</span> You can use the TCD file to customize the connection dialog.
For example, if you set <span style="font-family: courier new">show-ssl-check box</span> to "true", the **Require SSL** checkbox will display on the connection dialog.

Here's an example:

```
<connection-dialog class='postgres_odbc'>
    <connection-config>
        <authentication-mode value='Basic' />
        <authentication-options>
            <option name="UsernameAndPassword" default="true" />
        </authentication-options>
        <db-name-prompt value='Database: " />
        <has-pre-connect-database value="true" />
        <port-prompt value="Port: " default="5432" />
        <show-ssl-checkbox value="true" />
    </connection-config>
</connection-dialog>
```

![]({{ site.baseurl }}/assets/pce-connection-dialog-box.png)

## ![3]({{ site.baseurl }}/assets/pce-3.png) Tableau Connector Resolver File

The Connector Resolver file (.tdr) is optional. Tableau uses it to create a connection to your data.

The TDR file calls these scripts (described in the following sections):
- Connection Builder
- Connection Properties

The TDR file also contains the connection-normalizer and the driver-resolver section. The <span style="font-family: courier new">connection-normalizer</span> component defines what makes up a unique connection. An example of the component :

```
<connection-normalizer>
    <required-attributes>
        <attribute-list>
            <attr>server</attr>
            <attr>port</attr>
            <attr>dbname</attr>
            <attr>username</attr>
            <attr>password</attr>
        </attribute-list>               
    </required-attributes>
</connection-normalizer>

```

Starting in Tableau 2021.1 a connector using [Connection Dialog V2]({{ site.baseurl }}/docs/mcd) can let the system determine at runtime the correct <span style="font-family: courier new">connection-normalizer</span> by not defining it. See [API Reference]({{ site.baseurl }}/docs/api-reference#connection-normalizer) for more details.

The <span style="font-family: courier new">driver-resolver</span> is only used for ODBC drivers. JDBC connectors can specify the driver name in the URL built by the connection builder JavaScript.

Tableau database connections have a unique type, the <span style="font-family: courier new">class</span> attribute.
For example, all Postgres connections have the same <span style="font-family: courier new">class</span>.
Each connection also has a set of _connection attributes_ with unique values.
Typically these attributes include the database server, username, and password.
If the attributes and their values are identical then the connections are considered the same and can be reused and shared within the Tableau process.

Connection attributes pass values from the connection dialog or the saved Tableau workbook to the _Connection Resolver_.
In turn, the Connection Resolver uses these attributes to format an ODBC or JDBC connection string.

```
<tdr class='postgres_odbc'>
    <connection-resolver>
        <connection-builder>
            // This is the component number 4 in the diagram above
            <script file='connectionBuilder.js'/>
        </connection-builder>
        <connection-properties>
            // This is the component number 5 in the diagram above
            // It is only used for JDBC Connectors
            <script file="connectionProperties.js">
        </connection-properties>
        <connection-normalizer>
            <required-attributes>
                <attribute-list>
                    <attr>server</attr>
                    <attr>port</attr>
                    <attr>dbname</attr>
                    <attr>username</attr>
                    <attr>password</attr>
                </attribute-list>
            </required-attributes>
        </connection-normalizer>
    </connection-resolver>
    // The driver resolver defines the rules for locating the ODBC driver
    // You don't need a driver resolver for JDBC plugins
    <driver-resolver>
        <driver-match>
            <driver-name type='regex'>PostgreSQL Unicode*</driver-name>
        </driver-match>
    </driver-resolver>
</tdr>

```

## ![4]({{ site.baseurl }}/assets/pce-4.png) Connection Builder

Tableau uses the Connection Builder script (connectionBuilder.js) to create the ODBC connection string and the JDBC connection URL. The script maps attributes that define how the connection is configured.
Some values -- such as username, password, and database name -- are user entries from the connection dialog.
They are mapped to ODBC or JDBC connection string values that the driver (in this case, PostgresSQL) uses.
Other attributes (such as BOOLSASCHAR and LFCONVERSION in this example) have values set to useful defaults. These depend on which driver you are using to connect to your database.
You can use this script to set any other connection string options that you would like to pass to the driver.

This is an example Connection Builder script for ODBC:

```
(function dsbuilder(attr)
{
    var params = {};

    // The values below come from the connection dialog and are entered by the user.
    // Here they are mapped to the ODBC connection string values the the driver can use.
    params["SERVER"] = attr[connectionHelper.attributeServer];
    params["PORT"] = attr[connectionHelper.attributePort];
    params["DATABASE"] = attr[connectionHelper.attributeDatabase];
    params["UID"] = attr[connectionHelper.attributeUsername];
    params["PWD"] = attr[connectionHelper.attributePassword];
    params["BOOLSASCHAR"] = "0";

    // The values below can be set to useful defaults.
    params["LFCONVERSION"] = "0";
    params["UseDeclareFetch"] = "1";
    params["Fetch"] = "2048";

    var formattedParams = [];

    // The driver resolver is invoked below to find the matching ODBC driver
    formattedParams.push(connectionHelper.formatKeyValuePair(driverLocator.keywordDriver, driverLocator.locateDriver(attr)));

    for (var key in params)
    {
        // This formats the params map into a set of ODBC key value pairs
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    return formattedParams;
})

```

This is an example Connection Builder script for JDBC:

```
(function dsbuilder(attr) {
    var urlBuilder = "jdbc:postgresql://" + attr[connectionHelper.attributeServer] + ":" + attr[connectionHelper.attributePort] +
        "/" + attr[connectionHelper.attributeDatabase] + "?";

    return [urlBuilder];
})
```

## ![5]({{ site.baseurl }}/assets/pce-5.png) Connection Properties

The Connection Properties script (connectionProperties.js) is optional. You need this script only if you're using a JDBC driver.

This example is for a connector to Amazon Athena.

```
(function propertiesBuilder(attr) {
    //This script is only needed if you are using a JDBC driver.
    var params = {};

    // Set keys for properties needed for connecting using JDBC.
    var KEY_USER = "user";
    var KEY_PASSWORD = "password";
    var KEY_WAREHOUSE = "s3_staging_dir"

    // Set connection properties from existing attributes.
    params[KEY_USER] = attr[connectionHelper.attributeUsername];
    params[KEY_PASSWORD] = attr[connectionHelper.attributePassword];
    params[KEY_WAREHOUSE] = attr[connectionHelper.attributeWarehouse];

    //Format the attributes as 'key=value'. By default some values are escaped or wrapped in curly braces to follow the JDBC standard, but you can also do it here if needed.
    var formattedParams = [];
    for (var key in params) {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }

    //The result will look like (search for jdbc-connection-properties in tabprotosrv.log):
    //"jdbc-connection-properties","v":{"password":"********","s3_staging_dir":"s3://aws-athena-s3/","user":"admin"}
    return formattedParams;
})
```

## ![6]({{ site.baseurl }}/assets/pce-8.png) Connection example

The Tableau Connection Resolver file (.tdr) generates an ODBC ConnectString or a JDBC Connection URL, which you can find in tabprotosrv.txt.

For ODBC, search for <span style= "font-family: courier new">ConnectString</span> to find something like this example:

```
ConnectString: DRIVER={PostgreSQL Unicode(x64)};SERVER=postgres;PORT=5432;DATABASE=TestV1;UID=test;PWD=********;BOOLSASCHAR=0;LFCONVERSION=0;UseDeclareFetch=1;Fetch=2048
```

For JDBC, search for <span style= "font-family: courier new">Connection URL</span> to find something like this example:

```
JDBCProtocol Connection URL: jdbc:postgresql://postgres:5342/TestV1
```

## ![7]({{ site.baseurl }}/assets/pce-9.png) Tableau Dialect File

After connection, Tableau uses your Tableau Dialect file (.tdd) to determine which SQL to generate for data retrieval from your database.
You can define your own dialect in the TDD file, or your connector can inherit a dialect from its parent (defined by the superclass). If you are using the "odbc" or "jdbc" superclass, you must define a dialect, since those superclasses do not have dialects.

This is an example Tableau Dialect (.tdd) file:

```
<?xml version="1.0" encoding="utf-8"?>
<dialect name='SimplePostgres'
    class='postgres_odbc'
    base='PostgreSQL90Dialect'
    version='18.1'>
<!-- You can add dialect files here. See the documentation for more information. -->
</dialect>
```
