---
title: Building the Connection Dialog
---

## The Connection Dialog

The Connection Dialog prompts the user to enter connection and authentication information that will passed into the connector builder script to build the connection string. The dialog appears when creating a new connection or editing an existing connection on both Tableau Desktop and Server. 

The Connection Dialog is mainly defined in the Tableau Custom Dialog (.tcd) file.

![]({{ site.baseurl }}/assets/connection-dialog.png)

## Connector Name and Vendor Information

The connector is displayed as "[Display Name] by [Company Name]" in the connection dialog and connection list.

"For support, contact [Company Name]" is displayed at the bottom left of the connector. Clicking on this link will send the user to the support link defined in the manifest. This link also displays in error messages.

These elements are defined in the manifest.xml file:
```
<connector-plugin class='postgres_odbc' superclass='odbc' plugin-version='0.0.0' name='PostgreSQL ODBC' version='18.1'>
  <vendor-information>
      <company name="Company Name"/>
      <support-link url = "http://example.com"/>
  </vendor-information>
  ...
</connector-plugin>
```

## Vendor Attributes (Custom Fields)
Vendors can add customized attributes to their connector plugin by using the vendor attributes.

These fields have a custom label and can be used for attributes in the connection strings that are not available in the attribute list. You can currently add 3 custom fields in your connector plugin.

To add a custom vendor-attribute, you will need to modify your connection-dialog.tcd, connectionResolver.tdr and connectionBuilder.js.
**For JDBC based plugins, you will need to modify connectionProperties.js instead of connectionBuilder.js**

connection-resolver.tdr

```
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

connection-dialog.tcd

```
 <connector-plugin class='postgres_jdbc' superclass='jdbc' plugin-version='0.0.0' name='PostgreSQL JDBC' version='18.1'>
          <connection-config>
            ...
            <vendor1-prompt value="Log Level: "/>
            <vendor2-prompt value="Protocol Version: "/>
            <vendor3-prompt value="Char Set: "/>

        </connection-config>
      </connection-dialog>
```

connectionBuilder.js (Non-JDBC)
```
   ...
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
      
```

connectionProperties.js (For JDBC only)
```
   ...
      props["password"] = attr[connectionHelper.attributePassword];
      props["logLevel"] = attr[connectionHelper.attributeVendor1];
      props["protocolVersion"] = attr[connectionHelper.attributeVendor2];
      props["charSet"] = attr[connectionHelper.attributeVendor3];

      if (attr[connectionHelper.attributeSSLMode] == "require")
      {
      ...
      
```


For complete files, [Click Here](https://github.com/tableau/connector-plugin-sdk/tree/dev/samples/components/dialogs/new_text_field)

## The Tableau Custom Dialog File

The UI elements you see in the dialog are determined in the .tcd file:
```
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

The `authentication-mode` and `authentication-options` tags control how a user is prompted to enter data source credentials. For information on authentication modes, see [Authentication modes]({{ site.baseurl }}/docs/auth-modes).

The other tags control what prompts show up in the connection dialog. For example, `<port-prompt value="Port: " default="5432" />` shows the Port prompt with the label of Port and a default value of 5432.

## Localizing your connector

For information on localizing your connection dialogs, see [Localize Your Connector]({{ site.baseurl }}/docs/localize)
