---
title: Build the Connection Dialog
---

The connection dialog prompts the user to enter connection and authentication information. That information is passed into the Connector Builder script to build the connection string. The dialog appears when creating a new connection or editing an existing connection and is used by both Tableau Desktop and Tableau Server.

The connection dialog can be defined in two different ways:
- [Connection Dialog v1]({{ site.baseurl }}/docs/ui) 
- [Connection Dialog v2]({{ site.baseurl }}/docs/mcd) in Tableau 2020.3 or later

**Connection Dialog v2 is the recommended pattern for new connectors.**

## Set connector name and vendor information

The connector is displayed as "[Display Name] by [Company Name]" in the connection dialog and connection list.

"For support, contact [Company Name]" is displayed at the bottom left of the connector. Clicking this link sends the user to the support link defined in the manifest. This link also displays in error messages. The support link must use HTTPS to be packaged into a TACO file.

These elements are defined in the manifest.xml file:
```xml
<connector-plugin class='postgres_odbc' superclass='odbc' plugin-version='0.0.0' name='PostgreSQL ODBC' version='20.1'>
  <vendor-information>
      <company name="Company Name"/>
      <support-link url = "https://example.com"/>
      <driver-download-link url="https://drivers.example.com"/>
  </vendor-information>
  ...
</connector-plugin>
```

## Define how the connector authenticates 

The ```authentication``` attribute is a required field and controls how a user is prompted to enter data source credentials. For more information on authentication modes, see [Authentication modes]({{ site.baseurl }}/docs/auth-modes).

## Define custom vendor attributes

Vendors can add customized attributes (fields) to their connector plugin by using the a ```field``` element in V2 or the pre-defined ```vendor*``` elements in V1.  Ensure the vendor defined fields do not duplicate functionality defined in the [Connection Field Platform Integration]({{ site.baseurl }}/docs/mcd#connection-field-platform-integration) section.

These fields have a custom label and can be used for attributes in the connection strings.  

To add a custom vendor attribute for an ODBC-based connector, you must modify these files:
- connectionFields.xml or connection-dialog.tcd
- connectionResolver.tdr
- connectionBuilder.js

To add a custom vendor attribute for an JDBC-based connector, you must modify these files:
- connectionFields.xml or connection-dialog.tcd
- connectionResolver.tdr
- connectionBuilder.js
- connectionProperties.js

**Vendor defined attributes will be logged and persisted to Tableau workbook xml in plain text.** This means the input for these fields cannot contain any Personally Identifiable Information (PII), as they are not secure and could leak sensitive customer information.

See examples below.

__connectionResolver.tdr__

```xml
    ...
    <required-attributes>
      <attribute-list>
        ...
        <attr>v-char-set</attr>

      </attribute-list>
    </required-attributes>
    ...
```

__connectionFields.xml__

```xml
<connection-fields>
  ...
  <field name="v-char-set" label="Char Set" value-type="string" category="general" default-value="" />
  ...
</connection-fields>
```

__connectionBuilder.js (ODBC)__
```js
(function dsbuilder(attr)
  {
    var params = {};

    ...
    params["charSet"] = attr['v-char-set'];
    ...

```

__connectionProperties.js (JDBC only)__
```js
      ...
      params["charSet"] = attr['v-char-set'];
      ...

```

## Localize your connector

For information on localizing your connection dialogs, see [Localize Your Connector]({{ site.baseurl }}/docs/localize).
