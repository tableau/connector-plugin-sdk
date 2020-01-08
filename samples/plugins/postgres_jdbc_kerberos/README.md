
# Readme

The postgres jdbc kerberos sample plugin demonstrates how to incorporate the following authentication modes for your Tableau + postgres + jdbc use cases.
1. Use **SSPI** authentication to connect a postgres database with `Tableau Desktop on Windows`.
1. Use **Kerberos via JAAS and Java GSS-API** to connect a postgres database with `Tableau Desktop on Mac`.
1. Publish a tableau viz from `Tableau Desktop` using service account authentication for Tableau Server also known as **server run-as authentication** .
1. Publish a tableau viz from `Tableau Desktop` using kerberos delegation for Tableau Server also know as **viewer credentials authentication**.

Below I will describe what each of the above means and then how to use the sample plugin to enable one or a combination of them.

## What the auth ?

### GSS-API
GSS-API offers application programmers uniform access to security services atop a variety of underlying security mechanisms, including Kerberos. The GSSAPI, by itself, does not provide any security. Instead, security-service vendors provide GSSAPI implementations - usually in the form of libraries installed with their security software. These libraries present a GSSAPI-compatible interface to application writers who can write their application to use only the vendor-independent GSSAPI. If the security implementation ever needs replacing, the application need not be rewritten. The dominant GSSAPI mechanism implementation in use is Kerberos. (source - [wikipedia](https://en.wikipedia.org/wiki/Generic_Security_Services_Application_Program_Interface))
All the authentication modes described below use some flavor of GSS-API with Kerberos implementation. Read on to find which one is what OR skip to [How to plugin auth?](#how-to-plugin-auth) if you already know this.

#### SSPI authentication
Security Support Provider Interface (SSPI) is a proprietary variant of GSSAPI with extensions and very Windows-specific data types. It is a Win32 API used by Microsoft Windows systems to perform a variety of security-related operations such as authentication. SSPI functions as a common interface to several Security Support Providers (SSPs). A Security Support Provider is a dynamic-link library (DLL) that makes one or more security packages available to application.
Examples of common SSPs are Kerberos, NTLM, Negiotiate. (source - [wikipedia](https://en.wikipedia.org/wiki/Security_Support_Provider_Interface)). 

In my simple words - SSPI is used to configure Single-Sign On type of authentication to connect to a database using your Active Directory credentials. 

#### JAAS and Java GSS-API
The Java GSS-API contains the Java bindings for the GSS-API defined in [RFC 2853](http://www.ietf.org/rfc/rfc2853.txt). 
(source - [Oracle Java docs](https://docs.oracle.com/javase/8/docs/technotes/guides/security/jgss/tutorials/index.html)).  

JAAS(Java Authentication and Authorization Service) can be used for two purposes:

-   for authentication of users, to reliably and securely determine who is currently executing Java code, and
-   for authorization of users to ensure they have the access control rights (permissions) required to do security-sensitive operations.

JAAS authentication is typically performed prior to secure communication using Java GSS-API. In the case of postgres, the property `jaasLogin`(defaults to true) indicates whether to attempt a JAAS login before authenticating with GSSAPI.

#### Service account aka Server Runas

You can configure Tableau Server to use a Kerberos service account to access a database. In this scenario, Tableau Server connects to databases with a service account, also referred to as a "RunAs account". 

While configuring Tableau Server, users need to provide a user principal name and keytab file path (see Tableau KB [article](https://help.tableau.com/current/server-linux/en-us/kerberos_runas_linux.htm)). Tableau uses this info to login to kerberos KDC and passes the kerberos ticket info to the driver using GSSAPI to make the actual database connection.


#### Kerberos Delegation aka Viewer Credentials

Kerberos delegation enables Tableau Server to use the Kerberos credentials of the viewer of a workbook or view to execute a query on behalf of the viewer. This is useful in the following situations:

-   You need to know who is accessing the data (the viewer's name will appear in the access logs for the data source).
    
-   Your data source has row-level security, where different users have access to different rows

## <a id="how-to-plugin-auth"></a>How to plugin auth?

The postgres_jdbc_kerberos sample plugin is written in such a way that it supports all the three authentication methods listed here. However, the individual sections of the plugin components concern specific authentication modes and have been laid out here for the purposes of re-use and understanding. 
If you are publishing from Tableau Desktop, which is the most common use case, the Server RunAs and Viewer credentials will be visible in publish options only if you have `auth-integrated` as one of the authentication options in the `connection-dialog.tcd`. So if your choice of authentication is any of these two, then you have to configure SSPI as well. Otherwise, SSPI can be configured independently also.   

### SSPI authentication for Tableau on Windows Desktop
connection-dialog.tcd
```
<authentication-options>
    <option name="Integrated" value="auth-integrated" />
```
connectionProperties.js
```
if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
    if(connectionHelper.GetPlatform() === "win") {
            // property for SSPI on Tableau Desktop
            props["gsslib"] = "sspi";
```
Notes: 
1. The postgres jdbc driver uses waffle-jna library for SSPI authentication. Therefore, it is required to download waffle-jna and all its compile dependencies from the [maven repository](https://mvnrepository.com/artifact/com.github.waffle/waffle-jna/2.1.0).  The plugin code has been tested to work on waffle-jna 2.1.0.
2. It is recommended to use Postgres JDBC driver version 42.2.10+. The plugin was tested on previous versions of the driver and failed due to bug [#1482](https://github.com/pgjdbc/pgjdbc/issues/1482) which has since been fixed in version 42.2.10.    

### Kerberos via JAAS and Java GSS-API for Tableau on Mac Desktop
connection-dialog.tcd
```
<authentication-options>
    <option name="Integrated" value="auth-integrated" />
```
connectionProperties.js
```
if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
    if(connectionHelper.GetPlatform() === "mac") {
        // note that for postgres jdbc driver, jaasLogin defaults to true so we don't need to specify it here
        // just add this jaasApplicationName used by Tableau's embedded jaas.conf file
        props["jaasApplicationName"] = "com.sun.security.jgss.krb5.initiate";
```

Other Configuration:
* Only for postgres plugin - add this property `Settings.DisableNativeGSS` as a `Boolean/YES` to the Tableau plist on Mac at `/Library/Preferences/com.tableau.Tableau-<version>.plist` as described below. Here version is Tableau Desktop major version, for example, `com.tableau.Tableau-2019.4.plist`.
```
// Note - the below two commands require root privileges hence sudo is needed.
sudo defaults write /Library/Preferences/com.tableau.Tableau-<version>.plist Settings.DisableNativeGSS -bool YES
// clear the plist cache before opening Tableau 
sudo killall -u root cfprefsd
```
* Make sure a krb5.conf file is present at `/etc/krb5.conf`(/etc is a private directory, requires root privileges). Check for the existence of either of the following two files `/etc/krb5.conf` or `/Library/Preferences/edu.mit.Kerberos`. The recommended practice is to move/rename the file at /etc/krb5.conf. If the second file (edu.mit.Kerberos) is present it needs to be backed up and deleted.
* Before using the connector plugin, run `kinit user@REALM`  
* Next run `klist` to verify that the kerberos TGT appears in the cache. 
* Use the same user which is registered for kerberos in the database to open Tableau Desktop. From the terminal this can be achieved by the following commands 
```
sudo su 
su username
/Applications/Tableau\ Desktop\ [Tableau version].app/Contents/MacOS/Tableau -DConnectPluginsPath=/Users/[user name]/tableau_connectors
```

### Server RunAs authentication
connectionProperties.js
```
    function isEmpty(str) {
        return (!str || 0 === str.length); 
    }

    if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
        // if :tableau-server-user attribute is non-empty, it means the connector plugin is currently being accessed in a tableau server environment
        var str = attr[":tableau-server-user"];
        if (!isEmpty(str)) {
            props["user"] = str;
            props["gsslib"] = "gssapi";  
            props["jaasLogin"] = "false";    
        }   
```
Note: Tableau supports RunAs authentication only on Linux. For configuring Runas authentication on Tableau Server, see this [article](https://help.tableau.com/current/server-linux/en-us/kerberos_runas_linux.htm). 

### Viewer Credentials authentication
connectionProperties.js
```
    function isEmpty(str) {
        return (!str || 0 === str.length); 
    }

    if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
        // if :tableau-server-user attribute is non-empty, it means the connector plugin is currently being 
        // accessed in a tableau server environment
        var str = attr[":tableau-server-user"];
        if (!isEmpty(str)) {
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
1. For configuring Kerberos delegation on Tableau Server Linux, refer to this [article](https://help.tableau.com/current/server-linux/en-us/kerberos_delegation.htm). 
2. For configuring Kerberos delegation on Tableau Server Windows. in addition to the steps mentioned [here](https://help.tableau.com/current/server/en-us/kerberos_delegation.htm), also execute the below steps before running `tsm pending-changes apply`
```
    tsm configuration set -k native_api.datasource_impersonation_runas_principal -v <delegation/Run As account user or principal>
    tsm configuration set -k native_api.datasource_impersonation_runas_keytab_path -v <path-to-file>kerberos.keytab
```
