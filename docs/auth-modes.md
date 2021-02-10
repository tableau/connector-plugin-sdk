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
LDAP
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

### Database impersonation using embedded credentials (Tableau Server only)

This applies to databases which support a user(authenticated_user) that can delegate requests to another user(delegated_user) by enabling the client to pass a DelegationUID(delegated_user) to the database server. As a result of this, the query will run on the database with the privileges of the delegated_user. This form of delegation can be supported in Tableau Server by passing the identity of the logged in user as the DelegationUID to the database using JDBC driver properties or ODBC connection-string. This community [article](https://community.tableau.com/docs/DOC-11137) gives more information on Database Impersonation using Embedded credentials. At this time, connector-sdk only supports cases where the client connection to the database uses basic username-password authentication. Support for Kerberos authentication from client will be added later.

Below is an example of how to pass DelegationUID in a JDBC plugin in Tableau Server. Please note that some JDBC drivers may have a different name for this property so take a look at driver documentation for the appropriate property name.

 ```javascript
    // Connection properties
    function isEmpty(str) {
        return (!str || 0 === str.length);
    }

    var props = {};
    props["UID"] = attr[connectionHelper.attributeUsername];
    props["PWD"] = attr[connectionHelper.attributePassword];

    if (attr[connectionHelper.attributeTableauServerAuthMode] == connectionHelper.valueAuthModeDBImpersonate) {
        var str = attr[connectionHelper.attributeTableauServerUser];

        if (!isEmpty(str)){
            props["DelegationUID"] = str;
        }
    }
 ```

To enable the "Impersonate using embedded password" option in the publish dialog ensure CAP_AUTH_DB_IMPERSONATE is enabled in the plugin manifest.xml.
 ```xml
   // manifest.xml
    <customizations>
      <customization name="CAP_AUTH_DB_IMPERSONATE" value="yes"/>
    </customizations>
 ```

The connector plugin present on a Tableau Server instance MUST contain the above two code changes and the server admin should run "tsm pending-changes apply". After this, user should be able to use a vanilla plugin on a Tableau Desktop Client with the same class name and capable of doing basic username-password authentication. Thereafter, when the user tries to publish a workbook using Tableau Desktop to a Tableau Server instance, they should be able to publish it using the option "Impersonate using embedded password". When the workbook is opened in Tableau Server, the delegation should have taken place automatically if appropriate delegation permissions are configured for the authenticated_user and delegated_user(user logged into Tableau server) or else an error message of this sort is thrown from the database "User user1 is not authorized to delegate to user2". For more information on deploying connector plugins in Tableau Server, please refer this [document]({{ site.baseurl }}/docs/run-taco)

A [sample](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins/db_impersonation) JDBC plugin is provided using an Impala database as an example. For documentation on how to configure delegation in Impala, refer to database [documentation](https://impala.apache.org/docs/build/html/topics/impala_delegation.html).

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
