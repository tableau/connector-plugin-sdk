---
title: Build the Connection Dialog with Connection Dialog v1
---

The connection dialog prompts the user to enter connection and authentication information. That information is passed into the Connector Builder script to build the connection string. The dialog appears when creating a new connection or editing an existing connection and is used by both Tableau Desktop and Tableau Server.

The connection dialog is mainly defined in the Tableau Custom Dialog (.tcd) file.

Here's an example of a connection dialog:

![]({{ site.baseurl }}/assets/connection-dialog.png)

## Set connector name and vendor information

The connector is displayed as "[Display Name] by [Company Name]" in the connection dialog and connection list.

"For support, contact [Company Name]" is displayed at the bottom left of the connector. Clicking this link sends the user to the support link defined in the manifest. This link also displays in error messages. The support link must use HTTPS to be packaged into a TACO file.

These elements are defined in the manifest.xml file:
```xml
<connector-plugin class='postgres_odbc' superclass='odbc' plugin-version='0.0.0' name='PostgreSQL ODBC' version='20.1'>
  <vendor-information>
      <company name="Company Name"/>
      <support-link url = "http://example.com"/>
  </vendor-information>
  ...
</connector-plugin>
```

## Define custom vendor attributes
Vendors can add customized attributes (fields) to their connector plugin by using the vendor attributes.

These fields have a custom label and can be used for attributes in the connection strings that are not available in the attribute list. You can currently add three custom fields in your connector plugin.

To add a custom vendor attribute for an ODBC-based connector, you must modify these files:
- connection-dialog.tcd
- connectionResolver.tdr
- connectionBuilder.js

To add a custom vendor attribute for an JDBC-based connector, you must modify these files:
- connection-dialog.tcd
- connectionResolver.tdr
- connectionProperties.js

See examples below.

__connection-resolver.tdr__

```xml
    ...
      <required-attributes>
      <attribute-list>
        ...
        <attr> vendor1 </attr>
        <attr> vendor2 </attr>
        <attr> vendor3 </attr>

      </attribute-list>
      </required-attributes>
    ...
```

__connection-dialog.tcd__

```xml
 <connector-plugin class='postgres_jdbc' superclass='jdbc' plugin-version='0.0.0' name='PostgreSQL JDBC' version='18.1'>
          <connection-config>
            ...
            <vendor1-prompt value="Log Level: "/>
            <vendor2-prompt value="Protocol Version: "/>
            <vendor3-prompt value="Char Set: "/>

        </connection-config>
      </connection-dialog>
```

__connectionBuilder.js (ODBC only)__
```js
(function dsbuilder(attr)
  {
    var params = {};

    params["SERVER"] = attr[connectionHelper.attributeServer];
    params["PORT"] = attr[connectionHelper.attributePort];
    params["DATABASE"] = attr[connectionHelper.attributeDatabase];
    params["UID"] = attr[connectionHelper.attributeUsername];
    params["PWD"] = attr[connectionHelper.attributePassword];
    params["loglevel"] = attr[connectionHelper.attributeVendor1];
    params["protocolVersion"] = attr[connectionHelper.attributeVendor2];
    params["charSet"] = attr[connectionHelper.attributeVendor3];
    ...

```

__connectionProperties.js (JDBC only)__
```js
      ...
      props["password"] = attr[connectionHelper.attributePassword];
      props["logLevel"] = attr[connectionHelper.attributeVendor1];
      props["protocolVersion"] = attr[connectionHelper.attributeVendor2];
      props["charSet"] = attr[connectionHelper.attributeVendor3];

      if (attr[connectionHelper.attributeSSLMode] == "require")
      {
      ...

```

See complete files [here](https://github.com/tableau/connector-plugin-sdk/tree/dev/samples/components/dialogs/new_text_field).

## Define Tableau Custom Dialog file elements

The TCD file defines which UI elements display in the dialog.

Here's an example of a TCD file:

```xml
<connection-dialog class='postgres_odbc'>
  <connection-config>
    <authentication-mode value='Basic' />
    <authentication-options>
      <option name="UsernameAndPassword" default="true" />
    </authentication-options>
    <db-name-prompt value="Database: " />
    <has-pre-connect-database value="true" />
    <port-prompt value="Port: " default="5432" />
    <show-ssl-checkbox value="true" />
  </connection-config>
</connection-dialog>
```

The <span style="font-family: courier new">authentication-mode</span> and <span style="font-family: courier new">authentication-options</span> tags control how a user is prompted to enter data source credentials. For information on authentication modes, see [Authentication modes]({{ site.baseurl }}/docs/auth-modes).

The other tags control what prompts show up in the connection dialog. For example, this shows the Port prompt with the label of Port and a default value of 5432:

`<port-prompt value="Port: " default="5432" />`

## Localize your connector

For information on localizing your connection dialogs, see [Localize Your Connector]({{ site.baseurl }}/docs/localize).
