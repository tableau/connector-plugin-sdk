---
title: Connector API Reference
---

## Connection Resolver \*.tdr

Defines the connection to your data source.

**File extension:** .tdr

See [resolvers](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/components/resolvers) for examples.

The Connection Resolver is made up of several components:

---

### connection-builder

Builds the ODBC ConnectString or JDBC Connection URL. For a JDBC Connection URL, we require that the that the connection-builder contains only non-secure attributes, such as server, port, and dbname.

**Type:** JavaScript

#### JavaScript function call signature:

**Input:** attr, an object of key/value pairs

```javascript
{"server" : "myserver.somewhere.net"}
```

**Return:** array of formatted key=value pairs

```javascript
["DRIVER={My ODBC Driver}", "Host=myserver.somewhere.net"];
```

---

### connection-properties

Similar to connection-builder but is used to build the JDBC properties file. For JDBC Connection URL, we require that connection-properties contain secure attributes such as username and password.

**Type:** JavaScript

#### JavaScript function call signature (Recommended, added in 2019.4.1):

**Input:** attr, an object of key/value pairs

```javascript
{"server" : "myserver.somewhere.net", "username" : "myusername", "password" : "mypassword"}
```

**Return:** an object of key/value pairs that will be written to the properties file(recommended and available since 2019.4.1)

```javascript
["UID" : "myusername", "Host" : "myserver.somewhere.net", "PWD" : "mypassword"];
```

#### JavaScript function call signature (Deprecated):
**Note:** A bug in the JavaScript translation layer means that you cannot use values containing the '=' character. You can mitigate this by using the recomended API above. This API should only be used to maintain backwards compatibility with Tableau versions older than 2019.4.1.

**Input:** attr, an object of key/value pairs

```javascript
{"server" : "myserver.somewhere.net", "username" : "myusername", "password" : "mypassword"}
```

**Return:** an array of formatted key=value pairs that will be written to the properties file

```javascript
["UID=myusername", "Host=myserver.somewhere.net", "PWD=mypassword"]
```

---

### connection-normalizer

Defines the unique set of connection attributes which is used to generate a connection "key" and has important security considerations. Connections can be reused and shared within Tableau processes based on this key, so it must contain attributes whose values will be unique in a given security context. Username is a commonly used attribute that will make a unique connection for each user, for example.

Starting in Tableau 2021.1 a connector using Connection Dialog V2 style, connection-fields, can let the system determine at runtime the correct connection-normalizer by not defining it. Any connection-normalizer defined in the tdr file will take precedence at runtime. To use set min-version-tableau='2021.1' or newer in the manifest file.

**Type:** XML

The connection-normalizer is represented using a xml component in the [connectionResolver.tdr](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/plugins/postgres_odbc/connectionResolver.tdr) file. An example is :

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
The following table shows the most commonly used attributes in the attribute-list. Custom attributes may also be added.

_Attribute names_

| Attribute                  | Description                                                        |
| -------------------------- | ------------------------------------------------------------------ |
| authentication             | Connection attribute for the authentication mode                   |
| authentication-type        | Connection attribute for the authentication type                   |
| dbname                     | Connection attribute for the database                              |
| odbc-connect-string-extras | Connection attribute for extra connection string options           |
| password                   | Connection attribute for the password                              |
| port                       | Connection attribute for the port                                  |
| server                     | Connection attribute for the server                                |
| service                    | Connection attribute for the service                               |
| sslcert                    | Connection attribute for the SSL Certfile                          |
| sslmode                    | Connection attribute for the SSL Mode                              |
| username                   | Connection attribute for the user name                             |
| warehouse                  | Connection attribute for the Warehouse                             |

---

### driver-resolver

Determines the driver name to use when connecting. This is only used for ODBC connections. You can specify regex or string matches for the driver name, specify driver versions (if the driver correctly returns them through the ODBC interface), and have a list of multiple drivers that can be used in order.

Note: We do not recommend using ODBC driver version constraints, unless required for your scenario.  There are inconsistencies in the version values returned due to differences in the underlying operating and file systems on MacOS and Linux.

**Type:** XML

See [resolvers](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/components/resolvers) for examples.

---

## C++ objects and methods available to your JavaScript

### Logging

You can write to the Tableau log file (tabprotosrv.txt). Writing to the log file requires Debug level logging (-DLogLevel=Debug).

Use care when logging so that you don’t expose sensitive information like passwords and other authentication information.

    logging.Log("Hi")

---

### Connection Helper

_Attribute names_

| Function                       | Description                                                    |
| ------------------------------ | -------------------------------------------------------------- |
| attributeAuthentication        | Connection attribute for the authentication type               |
| attributeClass                 | Connection attribute for the connection type                   |
| attributeDatabase              | Connection attribute for the database                          |
| attributeInitialSQL            | Connection attribute for initial SQL                           |
| attributePassword              | Connection attribute for the password                          |
| attributePort                  | Connection attribute for the port                              |
| attributeServer                | Connection attribute for the server                            |
| attributeService               | Connection attribute for the service                           |
| attributeSSLCert               | Connection attribute for the SSL Certfile                      |
| attributeSSLMode               | Connection attribute for the SSL Mode                          |
| attributeTableauServerAuthMode | Connection attribute for tableau server authentication mode    |
| attributeTableauServerUser     | Connection attribute for tableau server user                   |
| attributeUsername              | Connection attribute for the user name                         |
| attributeWarehouse             | Connection attribute for the Warehouse                         |
| keywordODBCUsername            | ODBC Username keyword                                          |
| keywordODBCPassword            | ODBC Password keyword                                          |
| valueAuthModeDBImpersonate     | Attribute value for database impersonation authentication mode |

_Functions_

    String FormatKeyValuePair(String key, String value);

Format the attributes as 'key=value'. By default, some values are escaped or wrapped in curly braces to follow the ODBC standard, but you can also do it here if needed.

    bool MatchesConnectionAttributes(Object attr, Object inKey);

Invokes attribute matching code.

    Map ParseODBCConnectString(String odbcConnectString);

Returns a map of the key value pairs defined in the ```odbc-connect-string-extras``` string.

    String GetPlatform();

Returns the name of the os Tableau is running on. Possible values are:
- win
- mac
- linux

Example:

    formattedParams.push(connectionHelper.FormatKeyValuePair(key, params[key]));

    params[connectionHelper.keywordODBCUsername] = attr[connectionHelper.attributeUsername];

    odbcConnectStringExtrasMap = connectionHelper.ParseODBCConnectString(attr["odbc-connect-string-extras"]);

    if (attr[connectionHelper.attributeTableauServerAuthMode] == connectionHelper.valueAuthModeDBImpersonate) {
         props["DelegationUID"] = attr[connectionHelper.attributeTableauServerUser];
    }

_Throw Tableau Exception_

Normally, throwing an exception in a JavaScript component will show the user a more generic error message in the product. To have a custom error message appear in Tableau, use the following format:

    return connectionHelper.ThrowTableauException("Custom Error Message");

The full error is always logged.

---

### Driver Locator

_Functions_

    String LocateDriver (Object attr);

Get the name of your chosen driver that was matched using the rules in your TDR file.

    String LocateDriverVersion(Object attr);

Get the version number of the chosen driver as a string.

Example:

    formattedParams.push(connectionHelper.FormatKeyValuePair(driverLocator.keywordDriver, driverLocator.LocateDriver(attr)));

## Deprecated API

### ConnectionNormalizer and ConnectionMatcher JavaScript files
The JavaScript files for connection normalizer and connection matcher are deprecated as of Tableau 2020.3. In Tableau 2021.2 support was removed and an error will occur when loading the connector. The element `<script file="fileName.js"/>`, which was added inside the `<connection-matcher>` and `<connection-normalizer>` element, and the `<connection-matcher>` element itself, are the deprecated APIs. The `<connection-normalizer>` element is still supported in the connectionResolver.tdr file as shown in the connection-normalizer section above.

### SetImpersonateAttributes connection helper
This connection helper is deprecated as of Tableau 2020.1, since we always set impersonate attributes for all connectors. Trying to use this in a JavaScript component will throw an error when attempting to connect.

### <setImpersonateAttributes/> XML tag
This xml tag is deprecated as of Tableau 2020.1, though it has not yet been removed from the XSD. Since we always set this property starting with 2020.1, this tag is redundant.
