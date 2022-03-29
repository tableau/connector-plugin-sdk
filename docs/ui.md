---
title: Connection Dialog v1
---

Connection Dialog v2 is the recommended pattern for new connectors. For more details see the [Connection Dialog v2]({{ site.baseurl }}/docs/mcd) page.

## Define Tableau Custom Dialog file elements

The TCD file defines which UI elements display in the dialog.  The Connection Dialog V1 is a fixed list as defined by the file [XSD](https://github.com/tableau/connector-plugin-sdk/blob/master/validation/tcd_latest.xsd).

Here's an example of a TCD file:

```xml
<connection-dialog class='postgres_odbc'>
  <connection-config>
    <authentication-mode value='Basic' />
    <authentication-options>
      <option name="UsernameAndPassword" default="true" value="auth-user-pass" />
    </authentication-options>
    <db-name-prompt value="Database: " />
    <has-pre-connect-database value="true" />
    <port-prompt value="Port: " default="5432" />
    <show-ssl-checkbox value="true" />
  </connection-config>
</connection-dialog>
```

The ```authentication-mode``` and ```authentication-options``` tags control how a user is prompted to enter data source credentials. For more information on authentication modes, see [Authentication modes]({{ site.baseurl }}/docs/auth-modes).

The other tags control what prompts show up in the connection dialog. For example, this shows the Port prompt with the label of Port and a default value of 5432:

`<port-prompt value="Port: " default="5432" />`

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

**Vendor defined attributes will be logged and persisted to Tableau workbook XML in plain text.** This means the input for these fields cannot contain any Personally Identifiable Information (PII), as they are not secure and could leak sensitive customer information.

See examples below.

__connection-resolver.tdr__

```xml
    ...
    <required-attributes>
      <attribute-list>
        ...
        <attr>vendor1</attr>
        <attr>vendor2</attr>
        <attr>vendor3</attr>

      </attribute-list>
    </required-attributes>
    ...
```

__connection-dialog.tcd__

```xml
<connection-dialog class='postgres_jdbc'>
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
    ...
    params["loglevel"] = attr[connectionHelper.attributeVendor1];
    params["protocolVersion"] = attr[connectionHelper.attributeVendor2];
    params["charSet"] = attr[connectionHelper.attributeVendor3];
    ...

```

__connectionProperties.js (JDBC only)__
```js
      ...
      props["logLevel"] = attr[connectionHelper.attributeVendor1];
      props["protocolVersion"] = attr[connectionHelper.attributeVendor2];
      props["charSet"] = attr[connectionHelper.attributeVendor3];
      ...

```

See complete files [here](https://github.com/tableau/connector-plugin-sdk/tree/dev/samples/components/dialogs/new_text_field).

## Supported Authentication Modes

### No Authentication
User is never prompted for credentials.

```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
    <connection-config>
        <authentication-mode value='None' />
        <authentication-options>
            <option name="None" default="true" value="auth-none" />
        </authentication-options>
        ...
    </connection-config>
</connection-dialog>
```

```xml
<!-- Connection Resolver -->
<tdr class='sample'>
    <connection-resolver>
        ...
        <connection-normalizer>
            <required-attributes>
                <attribute-list>
                    ...
                    <attr>authentication</attr>
                    ...
                </attribute-list>
            </required-attributes>
        </connection-normalizer>
    </connection-resolver>
    ...
</tdr>
```

Sample connection dialog [noAuthOption.tcd](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/components/dialogs/noAuthOption.tcd)

### Username only

User is prompted for username during initial connection creation.  Before Tableau 2020.3 the ```option``` element required ```value='no'``` instead of example below.

```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
    <connection-config>
        <authentication-mode value='BasicUserNameOnly' />
        <authentication-options>
            <option name="Username" default="true" value="auth-user"/>
        </authentication-options>
        ...
    </connection-config>
</connection-dialog>
```

```xml
<!-- Connection Resolver -->
<tdr class='sample'>
    <connection-resolver>
        ...
        <connection-normalizer>
            <required-attributes>
                <attribute-list>
                    ...
                    <attr>authentication</attr>
                    <attr>username</attr>
                    ...
                </attribute-list>
            </required-attributes>
        </connection-normalizer>
    </connection-resolver>
    ...
</tdr>
```

### Password only

##### Tableau 2019.4 and later

User is prompted for password during initial connection creation and reconnecting to the data source.

```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
    <connection-config>
        <authentication-mode value='PasswordOnly' />
        <authentication-options>
            <option name="Password" default="true" value="auth-pass"/>
        </authentication-options>
        ...
    </connection-config>
</connection-dialog>
```

```xml
<!-- Connection Resolver -->
<tdr class='sample'>
    <connection-resolver>
        ...
        <connection-normalizer>
            <required-attributes>
                <attribute-list>
                    ...
                    <attr>authentication</attr>
                    <attr>password</attr>
                    ...
                </attribute-list>
            </required-attributes>
        </connection-normalizer>
    </connection-resolver>
    ...
</tdr>
```


### Username and Password

User is prompted for username and password during initial connection creation, and password only when reconnecting to the data source.  If the username can be blank replace ```value='Basic'``` with ```value='BasicNoValidateFields'``` below.

```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
    <connection-config>
        <authentication-mode value='Basic' />
        <authentication-options>
            <option name="UsernameAndPassword" default="true" value="auth-user-pass"/>
        </authentication-options>
        ...
    </connection-config>
</connection-dialog>
```

```xml
<!-- Connection Resolver -->
<tdr class='sample'>
    <connection-resolver>
        ...
        <connection-normalizer>
            <required-attributes>
                <attribute-list>
                    ...
                    <attr>authentication</attr>
                    <attr>username</attr>
                    <attr>password</attr>
                    ...
                </attribute-list>
            </required-attributes>
        </connection-normalizer>
    </connection-resolver>
    ...
</tdr>
```

### Multiple Authentication Modes

User is prompted for which authentication option to use, then a set of fields appear, conditional on that option.  Depending on the option selected the user may or may not be prompted for credentials when reconnecting to the data source.

Supported authentication options are below.  Starting in Tableau 2019.4, ```Password``` option is supported.

```
None
Username
Password
UsernameAndPassword
```

```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
    <connection-config>
        <authentication-mode value='ComboBoxIntegrated' />
        <authentication-options>
            <option name="None" value="auth-none" />
            <option name="Username" value="auth-user" />
            <option name="UsernameAndPassword" value="auth-user-pass" default="true" />
        </authentication-options>
        ...
    </connection-config>
</connection-dialog>
```

Note: the ```value``` attribute value for all options is customizable by connector author, except None, which is required to be ```auth-none```.  These option values are the persisted value of the authentication attribute in a Tableau workbook (twb) or Tableau data source (tds) file.  Starting in Tableau 2020.3, the recommendation is to standardize ```value``` to the following when possible:

Option | ```value```
-|-
None | auth-none
Username | auth-user
UsernameAndPassword | auth-user-pass
Password | auth-pass

```xml
<!-- Connection Resolver -->
<tdr class='sample'>
    <connection-resolver>
        ...
        <connection-normalizer>
            <required-attributes>
                <attribute-list>
                    ...
                    <attr>authentication</attr>
                    <attr>username</attr>
                    <attr>password</attr>
                    ...
                </attribute-list>
            </required-attributes>
        </connection-normalizer>
    </connection-resolver>
    ...
</tdr>
```

```javascript
// Connection Builder
(function dsbuilder(attr)
{
    ...
    var authAttrValue = attr[connectionHelper.attributeAuthentication];
    if (authAttrValue == "auth-none")
        // no-op
    else if (authAttrValue == "auth-user")
        params["UID"] = attr[connectionHelper.attributeUsername];
    else if (authAttrValue == "auth-user-pass")
    {
        params["UID"] = attr[connectionHelper.attributeUsername];
        params["PWD"] = attr[connectionHelper.attributePassword];
    }

    ...
})
```
