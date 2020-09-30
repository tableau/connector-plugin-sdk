
# Readme

This sample connector plugin demonstrates how to incorporate different Kerberos-based authentication modes for your "Tableau + Postgres + JDBC" use cases. This sample plugin code has been tested for all the authentication methods listed here with all platforms (Mac Desktop, Windows Desktop and Server, Linux Server). You can directly incorporate the plugin if your use case matches the ones below. However, the individual sections of the plugin components concern specific authentication modes and have been laid out here for the purposes of understanding and re-use.


## <a id="purpose"/> Use case(s) of this connector plugin
1. Use **SSPI** authentication to connect a Postgres database with `Tableau Desktop on Windows`. See [Kerberos SSO for Tableau Desktop](#desktop)   
1. Use **Kerberos SSO** to connect a Postgres database with `Tableau Desktop on Mac`. See [Kerberos SSO for Tableau Desktop](#desktop)
1. Publish a viz from `Tableau Desktop` using **Server RunAs/Kerberos RunAs authentication** and open it in Tableau Server. See [Kerberos RunAs and Delegation on Server](#server)
1. Publish a viz from `Tableau Desktop` using **Kerberos Delegation/Viewer Credentials authentication** and open it in Tableau Server. See [Kerberos RunAs and Delegation on Server](#server) 


## <a id="desktop"></a>Kerberos SSO for Tableau Desktop

Tableau Desktop uses [native GSS-API](https://docs.oracle.com/en/java/javase/11/security/accessing-native-gss-api.html) to accomplish this. On Windows specifically, Tableau uses JDK's [sspi-bridge](https://bugs.openjdk.java.net/browse/JDK-8199569) library to accomplish this. However, all of this has been abstracted out for plugin developers so just make sure you have the below code changes in place and it should work magically.   
**connection-fields.xml**
```
<field name="authentication" label="Authentication" category="authentication" value-type="selection">
  <selection-group>
    <option value="auth-integrated" label="Kerberos" />
    <!-- other auth options -->
  </selection-group>
</field>
```
**connectionProperties.js**
```
props["gsslib"] = "gssapi";	 
props["jaasLogin"] = "false";  
props["jaasApplicationName"] = "com.sun.security.jgss.krb5.initiate";
```

![Image](images/DesktopConnectionDialog.png)

Other Configurations for Mac:
* Only for Postgres JDBC plugin on Mac - add this property `Settings.DisableNativeGSS` as a `Boolean/YES` to the Tableau plist on Mac at `/Library/Preferences/com.tableau.Tableau-<version>.plist` as described below. Here version is Tableau Desktop major version, for example, `com.tableau.Tableau-2020.4.plist`.
```
// Note - the below command requires root privileges hence sudo is needed.
sudo defaults write /Library/Preferences/com.tableau.Tableau-<version>.plist Settings.DisableNativeGSS -bool YES
```
A [bug](https://github.com/pgjdbc/pgjdbc/issues/1662) has been opened on pgjdbc repository to fix this issue.
* Make sure a krb5.conf file is present at `/etc/krb5.conf`(/etc is a private directory, requires root privileges). Check for the existence of either of the following two files `/etc/krb5.conf` or `/Library/Preferences/edu.mit.Kerberos`. If the second file (edu.mit.Kerberos) is present it needs to be backed up and deleted.
* Before connecting, run `klist` to verify Kerberos TGT for the user principal is present in the Kerberos ticket cache. If not, run `kinit user@REALM` before opening Tableau Desktop.  

## <a id="server"/> Kerberos RunAs and Delegation on Server
When a user opens Tableau Desktop and login to Postgres using Kerberos there are the two publish options available, namely, "Server run-as" and "Viewer Credentials/Kerberos Delegation".

![Image](images/PublishKerberosAuthOptions.png)

These are the code changes needed for both the Kerberos RunAs and Delegation authentication on Tableau Server.  

**connectionProperties.js**
```
    function isEmpty(str) {
        return (!str || 0 === str.length); 
    }

    if (attr[connectionHelper.attributeAuthentication] == "auth-integrated") {
        // if attributeTableauServerUser is non-empty, it means the connector plugin is currently being accessed in a Tableau Server environment
        var serverUser = attr[connectionHelper.attributeTableauServerUser];
        if (!isEmpty(serverUser)) {
            props["user"] = serverUser;
            props["gsslib"] = "gssapi";  
            props["jaasLogin"] = "false";    
        }
    }        
```

In case of Kerberos RunAs, attributeTableauServerUser which is passed down by Tableau is the Service RunAsUser configured on the Tableau Server instance. In case of Kerberos Delegation, attributeTableauServerUser maps to the user/viewer currently logged into Tableau Server.

Additionally, for enabling Kerberos Delegation, CAP_AUTH_KERBEROS_IMPERSONATE needs to be enabled in the manifest file.

**manifest.xml**
```
<!-- This capability is needed to support Kerberos Delegation on Tableau Server --> 
      <customization name="CAP_AUTH_KERBEROS_IMPERSONATE" value="yes"/>
```

* Important Tableau Server configuration needed for Kerberos RunAs   
For Kerberos RunAs authentication, users need to provide RunAs user principal name and a keytab file path. Tableau Server uses the keytab to login to Kerberos KDC and the TGT thus obtained is used by JDBC driver for making a database connection.
For configuring a Tableau Server on Linux, see this Tableau [article](https://help.tableau.com/current/server-linux/en-us/kerberos_runas_linux.htm). 
For configuring a Tableau Server on Windows, see this Tableau [article](https://help.tableau.com/current/server/en-us/kerberos_runas_jdbc.htm). 

* Important Tableau Server configuration for Kerberos Delegation  
While configuring Tableau Server for Kerberos Delegation, users need to provide impersonation_runas_principal and keytab path which will be used to impersonate the viewer. 
For configuring Tableau Server on Linux, refer to this [article](https://help.tableau.com/current/server-linux/en-us/kerberos_delegation.htm). 
For configuring Tableau Server on Windows, refer to this [article](https://help.tableau.com/current/server/en-us/kerberos_delegation_jdbc.htm) 



