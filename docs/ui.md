---
title: Building the Connection Dialog
---

## The Connection Dialog

The Connection Dialog prompts the user to enter connection and authentication information that is passed into the into the connector builder script to build the connection string. The dialog appears when creating a new connection or editing an existing connection on both Tableau Desktop and Tableau Server.

The Connection Dialog is mainly defined in the Tableau Custom Dialog (.tcd) file.

![]({{ site.baseurl }}/assets/connection-dialog.png)

## Connector Name and Vendor Information

The connector is displayed as "[Display Name] by [Company Name]" in the connection dialog and connection list.

"For support, contact [Company Name]" is displayed at the bottom left of the connector. Clicking this link sends the user to the support link defined in the manifest. This link also displays in error messages. The support link must use HTTPS to be packaged into a `.taco` file.

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

## Localizing you connector

For information on localizing your connection dialogs, see [Localize Your Connector]({{ site.baseurl }}/docs/localize)
