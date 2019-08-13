---
title: Authentication Modes
---

The authentication mode chosen below influences how and when a user is prompted to enter data source credentials. The primary scenarios where authentication occurs:

- Creating a new connection with the connection dialog
- Opening a workbook and reconnecting to the data source
- Publishing a workbook or data source to Tableau Server

A combination of Connection Dialog and Connection Resolver changes implement each of these modes.  

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

Sample connection dialog [noAuthOption.tcd](https://github.com/tableau/connector-plugin-sdk/blob/dev/samples/components/dialogs/noAuthOption.tcd)

### Username only

User is prompted for username during initial connection creation.

```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
    <connection-config>
        <authentication-mode value='BasicUserNameOnly' />
        <authentication-options>
            <option name="Username" default="true" value="no"/>
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

##### Tableau 2019.4 or newer

User is prompted for password during initial connection creation and reconnecting to the data source.

```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
    <connection-config>
        <authentication-mode value='PasswordOnly' />
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

Supported authentication options are below.  ```Password``` option is supported in 2019.4 or newer.
 
```
None
Username
Password
UsernameAndPassword
LDAP
```

```xml
<!-- Connection Dialog -->
<connection-dialog class='sample'>
    <connection-config>
        <authentication-mode value='ComboBoxIntegrated' />
        <authentication-options>
            <option name="None" value="auth-none" />
            <option name="Username" value="username" />
            <option name="UsernameAndPassword" value="username-password" default="true" />
        </authentication-options>
        ...
    </connection-config>
</connection-dialog>
```

Note: the ```value``` attribute value for all options is customizable by connector author, except None, which is required to be ```auth-none```.  These option values are the persisted value of the authentication attribute in a Tableau workbook (twb) or Tableau data source (tds) file. 

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
    else if (authAttrValue == "username")
        params["UID"] = attr[connectionHelper.attributeUsername];
    else if (authAttrValue == "username-password")
    {
        params["UID"] = attr[connectionHelper.attributeUsername];
        params["PWD"] = attr[connectionHelper.attributePassword];
    }

    ...
})
```

## Considerations for 'hadoophive' and 'spark' base classes

When using 'hadoophive' or 'spark' as a base class there are additional constraints and requirements in the Connection Dialog and Connection Resolver.

In the Connection Dialog, any authentication ```option``` elements used must match the definition below.

```xml
<!-- Connection Dialog -->

<!-- <authentication-options> -->
<option name="None" value="0" />
<option name="Username" value="2" />
<option name="UsernameAndPassword" value="3" />
<!-- </authentication-options> -->
```

The Connection Resolver needs to include the additional required attribute ```authentication-type```.
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
                    <attr>authentication-type</attr>
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
