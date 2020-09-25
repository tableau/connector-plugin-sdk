
# Readme

The postgres jdbc kerberos sample plugin demonstrates how to incorporate the following authentication modes for your Tableau + postgres + jdbc use cases.
1. Use **SSPI** authentication to connect a postgres database with `Tableau Desktop on Windows`.
1. Use **Kerberos SSO via GSS-API** to connect a postgres database with `Tableau Desktop on Mac`.
1. Publish a tableau viz from `Tableau Desktop` using service account authentication for Tableau Server also known as **server run-as authentication** .
1. Publish a tableau viz from `Tableau Desktop` using kerberos delegation for Tableau Server also know as **viewer credentials authentication**.

Below I will describe what each of the above means and then how to use the sample plugin to enable one or a combination of them.

## What the auth ?

### GSS-API
GSS-API offers application programmers uniform access to security services atop a variety of underlying security mechanisms, including Kerberos. The GSSAPI, by itself, does not provide any security. Instead, security-service vendors provide GSSAPI implementations - usually in the form of libraries installed with their security software. These libraries present a GSSAPI-compatible interface to application writers who can write their application to use only the vendor-independent GSSAPI. If the security implementation ever needs replacing, the application need not be rewritten. The dominant GSSAPI mechanism implementation in use is Kerberos. (source - [wikipedia](https://en.wikipedia.org/wiki/Generic_Security_Services_Application_Program_Interface))
All the authentication modes described below use some flavor of GSS-API with Kerberos implementation. Read on to find which one is what OR skip to [How to plugin auth?](#how-to-plugin-auth) if you already know this.

#### SSPI authentication
Security Support Provider Interface (SSPI) is a proprietary variant of GSSAPI with extensions and very Windows-specific data types. It is a Win32 API used by Microsoft Windows systems to perform a variety of security-related operations such as authentication. SSPI functions as a common interface to several Security Support Providers (SSPs). A Security Support Provider is a dynamic-link library (DLL) that makes one or more security packages available to application.
Examples of common SSPs are Kerberos, NTLM, Negiotiate. (source - [wikipedia](https://en.wikipedia.org/wiki/Security_Support_Provider_Interface)). Tableau uses [native GSS-API](https://docs.oracle.com/en/java/javase/11/security/accessing-native-gss-api.html) to make SSO work on Windows.

In simple words - SSPI is used to configure Single-Sign On type of authentication to connect to a database using your Active Directory credentials. 

#### Java GSS-API and JAAS
Java GSS-API is used for securely exchanging messages between communicating applications. The Java GSS-API contains the Java bindings for the GSS-API defined in [RFC 5653](https://tools.ietf.org/html/rfc5653). 
(source - [Oracle Java docs](https://docs.oracle.com/en/java/javase/11/security/java-generic-security-services-java-gss-api1.html)).  

JAAS(Java Authentication and Authorization Service) can be used for two purposes:

-   for authentication of users, to reliably and securely determine who is currently executing Java code, and
-   for authorization of users to ensure they have the access control rights (permissions) required to do security-sensitive operations.

JAAS authentication is typically performed prior to secure communication using Java GSS-API. In the case of postgres, the property `jaasLogin` indicates whether to attempt a JAAS login before authenticating with GSSAPI.

From Tableau desktop, there are the two publish options available for Kerberos authentication, namely, "Server run-as" and "Viewer Credentials/Kerberos Delegation".

## <a id="how-to-plugin-auth"></a>How to plugin auth?

This sample plugin has been written in such a way that it supports all the three authentication methods listed here. However, the individual sections of the plugin components concern specific authentication modes and have been laid out here for the purposes of re-use and understanding. 
If you are publishing from Tableau Desktop, which is the most common use case, then Server RunAs and Viewer credentials auth will be visible in publish options only if you have logged into tableau using Integrated Authentication.  

### SSPI authentication for Tableau Desktop on Windows
connection-fields.xml
```
<field name="authentication" label="Authentication" category="authentication" value-type="selection">
  <selection-group>
    <option value="auth-integrated" label="Integrated" />
    <!-- other auth options -->
  </selection-group>
</field>
```
connectionProperties.js
```
     props["gsslib"] = "gssapi";	 
     props["jaasLogin"] = "false";  
     props["jaasApplicationName"] = "com.sun.security.jgss.krb5.initiate";
```

1. It is recommended to use Postgres JDBC driver version 42.2.10+. The plugin was tested on previous versions of the driver and failed due to bug [#1482](https://github.com/pgjdbc/pgjdbc/issues/1482) which has since been fixed in version 42.2.10.    

### Kerberos SSO for Tableau Desktop on Mac
connection-fields.xml
```
<field name="authentication" label="Authentication" category="authentication" value-type="selection">
  <selection-group>
    <option value="auth-integrated" label="Integrated" />
    <!-- other auth options -->
  </selection-group>
</field>
```

connectionProperties.js
```
        props["gsslib"] = "gssapi";	 
        props["jaasLogin"] = "false";  
        props["jaasApplicationName"] = "com.sun.security.jgss.krb5.initiate";
```

Other Configuration:
* Only for postgres plugin - add this property `Settings.DisableNativeGSS` as a `Boolean/YES` to the Tableau plist on Mac at `/Library/Preferences/com.tableau.Tableau-<version>.plist` as described below. Here version is Tableau Desktop major version, for example, `com.tableau.Tableau-2020.4.plist`.
```
// Note - the below command requires root privileges hence sudo is needed.
sudo defaults write /Library/Preferences/com.tableau.Tableau-<version>.plist Settings.DisableNativeGSS -bool YES
```
* Make sure a krb5.conf file is present at `/etc/krb5.conf`(/etc is a private directory, requires root privileges). Check for the existence of either of the following two files `/etc/krb5.conf` or `/Library/Preferences/edu.mit.Kerberos`. If the second file (edu.mit.Kerberos) is present it needs to be backed up and deleted.
* Before using the connector plugin, run `kinit user@REALM`  
* Next run `klist` to verify that the kerberos TGT appears in the kerberos ticket cache. 


### Server RunAs authentication - Linux Only
You can configure Tableau Server to use a Kerberos service account to access a database. In this scenario, Tableau Server connects to databases with a service account, also referred to as a "RunAs account". 

While configuring Tableau Server, users need to provide a user principal name and keytab file path (see Tableau KB [article](https://help.tableau.com/current/server-linux/en-us/kerberos_runas_linux.htm)). Tableau uses this info to login to kerberos KDC using JAAS and the database driver uses the TGT obtained before to make the actual database connection.

These are the changes needed to support server RunAs authentication.

connectionProperties.js
```
    function isEmpty(str) {
        return (!str || 0 === str.length); 
    }

    if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
        // if attributeTableauServerUser is non-empty, it means the connector plugin is currently being accessed in a tableau server environment
        var serverUser = attr[connectionHelper.attributeTableauServerUser];
        if (!isEmpty(serverUser)) {
            props["user"] = str;
            props["gsslib"] = "gssapi";  
            props["jaasLogin"] = "false";    
        }   
```
Note: Tableau supports RunAs authentication only on Linux Server. For configuring Runas authentication on Tableau Server, see this [article](https://help.tableau.com/current/server-linux/en-us/kerberos_runas_linux.htm). 

### Viewer Credentials authentication

Kerberos delegation enables Tableau Server to use the Kerberos credentials of the viewer of a workbook or view to execute a query on behalf of the viewer. This is useful in the following situations:

-   You need to know who is accessing the data (the viewer's name will appear in the access logs for the data source).
    
-   Your data source has row-level security, where different users have access to different rows

While configuring Tableau Server for kerberos delegation, users need to provide impersonation_runas_principal and keytab which will be used to impersonate the viewer.

These are the changes needed to support Kerberos Delegation.

connectionProperties.js
```
    function isEmpty(str) {
        return (!str || 0 === str.length); 
    }

    if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
        // if attributeTableauServerUser attribute is non-empty, it means the connector plugin is currently being accessed in a tableau server environment
        var serverUser = attr[connectionHelper.attributeTableauServerUser];
        if (!isEmpty(serverUser)) {
            props["user"] = str;
            props["gsslib"] = "gssapi";  
            props["jaasLogin"] = "false";    
        }   
```
manifest.xml
```
<!-- This capability is needed to support kerberos delegation on tableau server --> 
      <customization name="CAP_AUTH_KERBEROS_IMPERSONATE" value="yes"/>
```

Notes: 
1. For configuring Kerberos delegation on Tableau Server for Linux, refer to this [article](https://help.tableau.com/current/server-linux/en-us/kerberos_delegation.htm). 
2. For configuring Kerberos delegation on Tableau Server for Windows. in addition to the steps mentioned [here](https://help.tableau.com/current/server/en-us/kerberos_delegation.htm), also execute the below steps before running `tsm pending-changes apply`
```
    tsm configuration set -k native_api.datasource_impersonation_runas_principal -v <delegation/Run As account user or principal>
    tsm configuration set -k native_api.datasource_impersonation_runas_keytab_path -v <path-to-file>kerberos.keytab
```
