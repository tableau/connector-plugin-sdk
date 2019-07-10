---
title: Connector Example
---

A connector is a set of files that describe the UI elements needed to collect user input for creating a connection to a data source, any dialect or customizations needed, a connection string builder, driver resolver, and the ODBC- or JDBC-based driver.
Starting with the set of base connector files, you can add customizations to each file, while using the connectivity test harness to validate the connector behavior along the way.
The base connector files are described below.

![]({{ site.baseurl }}/assets/files-sequence.png)

## ![1]({{ site.baseurl }}/assets/pce-1.png) manifest.xml

The manifest.xml file informs Tableau about your connector and displays the connector name in the Tableau Connect pane.
It's a required file that defines the connector class and description.
The <span style="color:red">class</span> value is a unique key for your connector and is used in other XML files to apply their customizations and in Tableau workbooks to match connection types.

Each connector is typically based on a "class" such as ODBC or JDBC, and provides additional customizations beyond the class.
The <span style="color:blue; font-family: courier new">name</span> value displays the connector name in the Tableau **Connect** pane.

You may also specify the vendor information. The <span style="font-family: courier new">company name</span> value displays the name of the connector's creator next to the connector name on the Tableau **Connect** pane (for example, Connector Name by Creator), and the <span style="color:blue; font-family: courier new">support link</span> value is the URL of a website where users of the connector can get support.


![]({{ site.baseurl }}/assets/manifest-xml.png)

![]({{ site.baseurl }}/assets/pce-connect-pane.png)

## ![2]({{ site.baseurl }}/assets/pce-2.png) \*.tcd

(Optional) You can use the Tableau Custom Dialog (.tcd) file to customize the connection dialog, or your connector can inherit a dialog from its parent.
For example, if you include <span style="color:red">show-ssl-check box</span> and set the value to "true", the **Require SSL** check box will display on the sign-in dialog.

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

## ![3]({{ site.baseurl }}/assets/pce-3.png) \*.tdr

(Optional) Tableau uses the Connector Resolver (.tdr) file to create a connection to your data.
The .tdr file calls several javascript files, and includes the driver-resolver section.

Tableau database connections have a unique type, the class attribute.
For example, all Postgres connections have the same class.
Each connection also has a set of _connection attributes_ with unique values.
Typically these attributes include the database server, username, and password.
If the attributes and their values are identical then the connections are considered the same and can be reused and shared within the Tableau process.

Connection attributes are also used to pass values from the connection dialog or the saved Tableau workbook to the _Connection Resolver_.
The Connection Resolver knows how to use these attributes to format an ODBC or JDBC connection string.

![]({{ site.baseurl }}/assets/pce-tdr.png)

## ![4]({{ site.baseurl }}/assets/pce-4.png) connectionBuilder.js

The ODBC connection string and the JDBC connection URL are created by calling the Connection Builder script and passing in a map of attributes that define how the connection is configured.
Some values come from the connection dialog and are entered by the user (like username, password, and database name).
They are mapped to ODBC connection string values that the PostgreSQL driver understands.
Other attributes (like BOOLSASCHAR and LFCONVERSION) have values set to useful defaults.
You may also set any other connection string options that you would like to pass to the driver.

### Example ODBC Connection Builder

![]({{ site.baseurl }}/assets/pce-connectionbuilder.png)

### Example JDBC Connection Builder

```
(function dsbuilder(attr) {
    var urlBuilder = "jdbc:postgresql://" + attr["server"] + ":" + attr["port"] + "/" + attr["dbname"] + "?";
    var params = [];
    params["user"] = attr["username"];
    params["password"] = attr["password"];
    var formattedParams = [];
    for (var key in params) {
        formattedParams.push(connectionHelper.formatKeyValuePair(key, params[key]));
    }
    urlBuilder += formattedParams.join("&")
    return [urlBuilder];
})
```

## ![5]({{ site.baseurl }}/assets/pce-5.png) connectionProperties.js

This script is needed only if you're using a JDBC driver.

### Example connectionProperties.js

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

## ![6]({{ site.baseurl }}/assets/pce-6.png) connectionMatcher.js

This script defines how connections are matched.
In most cases, the default behavior works, so you don't have to include the <span style= "font-family: courier new">connection-matcher</span> section in your \*.tdr file.

## ![7]({{ site.baseurl }}/assets/pce-7.png) connectionRequired.js

This script defines what makes up a unique connection. The following values work for most cases.

```
(function requiredAttrs(attr) {
    return ["class", "server", "port", "dbname", "username", "password"];
})
```

## ![8]({{ site.baseurl }}/assets/pce-8.png) Example connection

The Tableau Connection Resolver file (\*.tdr) generates an ODBC ConnectString or a JDBC Connection URL, which you can find in tabprotosvr.txt.

For ODBC, search for <span style= "font-family: courier new">ConnectString</span> to find something like this example:

```
ConnectString: DRIVER={PostgreSQL Unicode(x64)};SERVER=postgres;PORT=5432;DATABASE=TestV1;UID=test;PWD=********;BOOLSASCHAR=0;LFCONVERSION=0;UseDeclareFetch=1;Fetch=2525
```

For JDBC, search for <span style= "font-family: courier new">Connection URL</span> to find something like this example:

```
JDBCProtocol Connection URL: jdbc:postgresql://postgres:5342/TestV1?user=test&password=********
```

## ![9]({{ site.baseurl }}/assets/pce-9.png) \*.tdd

After connection, Tableau uses your _.tdd dialect file to determine which SQL to generate when retrieving information from your database.
You can define your own dialect in the _.tdd file, or your connector can inherit a dialect from its parent.

### Example dialect.tdd

```
<?xml version="1.0" encoding="utf-8"?>
<dialect name='SimplePostgres'
    class='postgres_odbc'
    base='PostgreSQL90Dialect'
    version='18.1'>
<!-- You can add dialect files here. See the documentation for more information. -->
</dialect>
```
