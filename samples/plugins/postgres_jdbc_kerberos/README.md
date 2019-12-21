# Readme

The postgres jdbc kerberos sample plugin demonstrates how to incorporate the following authentication modes for your Tableau + postgres + jdbc use cases.
1. Use **SSPI** authentication to connect a postgres database with Tableau Desktop. 
2. Use service account for Tableau Server authentication also known as **server run-as authentication** .
3. Use kerberos delegation for Tableau Server authentication also know as **viewer credentials authentication**.

Below I will describe what each of the above means and then how to use the sample plugin to enable one or a combination of them.

## What the auth ?
### SSPI authentication
Security Support Provider Interface (SSPI) is a Win32 API used by Microsoft Windows systems to perform a variety of security-related operations such as authentication. SSPI functions as a common interface to several Security Support Providers (SSPs). A Security Support Provider is a dynamic-link library (DLL) that makes one or more security packages available to application.
Examples of common SSPs are Kerberos, NTLM, Negiotiate. (source - [wikipedia](https://en.wikipedia.org/wiki/Security_Support_Provider_Interface))

In my simple words - SSPI is used to configure Single-Sign On type of authentication to connect to a database using your Active Directory credentials. 

### Service account aka Server Runas

You can configure Tableau Server to use a Kerberos service account to access a database. In this scenario, Tableau Server connects to databases with a service account, also referred to as a "RunAs account". 

While configuring Tableau Server, users need to provide a user principal name and keytab file path (see Tableau KB [article](https://help.tableau.com/current/server-linux/en-us/kerberos_runas_linux.htm)). Tableau uses this info to login to kerberos KDC and passes the kerberos ticket info to the driver using GSSAPI to make the actual database connection.


### Kerberos Delegation aka Viewer Credentials

Kerberos delegation enables Tableau Server to use the Kerberos credentials of the viewer of a workbook or view to execute a query on behalf of the viewer. This is useful in the following situations:

-   You need to know who is accessing the data (the viewer's name will appear in the access logs for the data source).
    
-   Your data source has row-level security, where different users have access to different rows

## How to plugin auth ?

The postgres_jdbc_kerberos sample plugin is written in such a way that it supports all the three authentication methods listed here. However, the individual sections of the plugin components concern specific authentication modes and have been laid out here for the purposes of re-use and understanding. 
If you are publishing from Tableau Desktop, which is the most common use case, the Server RunAs and Viewer credentials will be visible in publish options only if you have "auth-integrated" as one of the authentication options in the connection-dialog.tcd. So if your choice of authentication is any of these two, then you have to configure SSPI as well. Otherwise, SSPI can be configured independently also.   

### SSPI authentication
connection-dialog.tcd
```
<authentication-options>
    <option name="UseWindows" value="auth-integrated" />
```
connectionProperties.js
```
if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
    props["gsslib"] = "sspi";
```
Notes: 
1. The postgres jdbc driver uses waffle-jna library for SSPI authentication. Therefore, it is required to download waffle-jna and all its compile dependencies from the [maven repository](https://mvnrepository.com/artifact/com.github.waffle/waffle-jna/2.1.0).  The plugin code has been tested to work on waffle-jna 2.1.0.
2. It is recommended to use Postgres JDBC driver version 42.2.10+. The plugin was tested on previous versions of the driver and failed due to bug [#1482](https://github.com/pgjdbc/pgjdbc/issues/1482) which has since been fixed in version 42.2.10.    

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

Note: For Tableau Server configuration, refer to these articles [server-on-linux](https://help.tableau.com/current/server-linux/en-us/kerberos_delegation.htm),  [server-on-windows](https://help.tableau.com/current/server/en-us/kerberos_delegation.htm) 
