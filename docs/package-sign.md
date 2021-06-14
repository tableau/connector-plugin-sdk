---
title: Package and Sign Your Connector for Distribution 
---

Packaging provides a convenient way to distribute your connector as a single .taco (Tableau Connector) file.  Signing ensures that Tableau will load only .taco files that have been signed with a currently valid certificate, ensuring that they haven't been tampered with. Signing is done using the JDK and a certificate trusted by a root certificate authority (CA) that has been installed in your Java environment. When the certificate expires, Tableau will reject the .taco file unless there is a valid timestamp.

Tableau Desktop verifies and loads signed connectors from a standard location (My Tableau Repository\\Connectors) or from a user supplied directory. 

This document explains how to package and sign your connector using the Connector SDK. 

## Before you begin 

Be sure your system includes the following:

-   Python version 3.7.3 or later 

-   Java JDK is installed, JAVA\_HOME is set, and the JDK is in your PATH environment variable 

-   Tableau Desktop 2019.4 or later   

-   A connector, developed with the Tableau Connector SDK, that you would like to package or sign 

-   [Git](https://git-scm.com/downloads)

###  Make sure your connector is ready for packaging

As part of the packaging process, the packager ensures that:

-   All XML files are valid against the XSD files located in the validate folder of the SDK.

-   All files referenced exist.

-   All files are smaller than 3 MB.

-   The connection class is the same in all places.

However, this validation does not guarantee that the connector will work in Tableau. The packager does not validate JavaScript, for example.
To ensure that your connector works before packaging it, you can do one of the following:
- [Run Your "Under Development" Connector]({{ site.baseurl }}/docs/run-taco#run-your-under-development-connector)
- Test it using [TDVT]({{ site.baseurl }}/docs/tdvt) 

### Set up the virtual environment for packaging

Follow these steps to get the packaging tool and set up the virtual environment. 

1.  Get the [Tableau Connector SDK repository](https://github.com/tableau/connector-plugin-sdk) on GitHub.
Here's one method to do that:
    1. Open a terminal in the directory where you want to copy the Tableau Connector SDK.
    1. Run the following command to clone the Tableau Connector SDK git repository:
    `git clone https://github.com/tableau/connector-plugin-sdk.git`

1.  Set up the virtual environment by going to the connector-packager folder and running `python –m venv .venv`.     
For example: 
    `C:\connector-plugin-sdk\connector-packager> python -m venv .venv`
    For more information about venv, see [venv – Creation of virtual environments](https://docs.python.org/3/library/venv.html) on the Python website.

1.  Activate the virtual environment using the activate command. 
For example, on Windows:
`C:\connector-plugin-sdk\connector-packager>.\.venv\Scripts\activate`  
Or, on Mac:
`mac-3:connector-packager qa.auto$ source ./.venv/bin/activate`
Or, on Linux:
`[centos@ip-10-177-53-47 connector-packager]$ source ./.venv/bin/activate`


1.  Install the packaging module in the virtual environment: 

    ```
    (.venv) C:\connector-plugin-sdk\connector-packager>python setup.py install  
    ```

## Package the connector

You must run the connector-packager tool from the connector-plugin-sdk/connector-packager/ directory. The packaged TACO file, by  default, will be generated within packaged-connector folder. There are several ways to run the tool:

-   To package the connector, run this command: 
 `python -m connector_packager.package [path_to_plugin_folder]`

-   To validate that the XML files are valid without packaging the connector, run this command:
`python -m connector_packager.package --validate-only [path_to_plugin_folder]`

### Packager examples
__Example 1__

This example shows how a TACO file is generated in connector-plugin-sdk\connector-packager\packaged-connector:

```
(.venv) E:\connector-plugin-sdk\connector-packager>python -m connector_packager.package ..\samples\plugins\mysql_odbc

Validation succeeded.

mysql_odbc_sample.taco was created in E:\connector-plugin-sdk\connector-packager\packaged-connector

```

__Example 2__

This example shows how a TACO file and log file are generated in a user-supplied locations:

```
(.venv) E:\connector-plugin-sdk\connector-packager>python -m connector_packager.package ..\samples\plugins\mysql_odbc  --dest e:\temp -l e:\temp

Validation succeeded.

mysql_odbc_sample.taco was created in e:\temp

```

## Sign your packaged connector with jarsigner

At this point, your connector is packaged into a single TACO file. Now you must sign the file or disable signature verification to allow it to be loaded automatically into Tableau.

__Why we require connectors to be signed__

Connectors are sensitive parts of the Tableau code. They handle database authentication and communicate directly with your driver. By signing the connector, Tableau can verify the authenticity and integrity of the connector, and customers can be confident the the plugin author is who they say they are, and the TACO file itself has not been tampered with since it was signed.

### Get your connector signed

A packaged Tableau Connector (.taco) file is, functionally the same as a JAR file. Tableau checks that packaged connectors are signed by a trusted certificate authority before loading them, using the default java keystore in the JRE. Because a TACO file is fundamentally a JAR file, you can follow Java documentation for signing JAR files.

**Important note**: Certificates are only valid for a certain amount of time, and Tableau does not load connectors with expired certificates. To mitigate this, use a timestamp as described in the signing example below. Timestamps use a timestamp authority to confirm that the certificate was valid when it was signed, even if the certificate is now expired, and timestamps are valid for much longer.

To sign a TACO file:
1. Generate a certificate signature request (CSR). You can use Java's [keytool](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/keytool.html) to generate this.
1. Send the CSR to a certificate authority that is trusted by the Java key store. Make sure that certificate you get is a code-signing certificate.
1. Sign your TACO file using [jarsigner](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/jarsigner.html).
1. Verify that your TACO file is signed using jarsigner as follows:
     1. Use the following command:
     `jarsigner -verify path_to_taco -verbose -certs -strict`
    If "jar verified" appears, your TACO file should be ready to be used in Tableau.
    1. Double-check the certificate chain to make sure that the final certificate is from your certificate authority.
    1. Take note of when the TACO file will expire. Once it does, users will no longer be able use the connector in Tableau without disabling verification and you will need to provide a new signed TACO file.

### Signing example

Getting a certificate is a multi-step process. This example illustrates how to sign a TACO file with a basic signed certificate.

__Step 1: Generate a Certificate Signing Request (CSR) file__

A certificate signing request (CSR) is a request for a certificate authority (CA) to create a public certificate for your organization.
1. Generate a key pair using this command:
`keytool -genkeypair -alias your_alias -keystore your_keystore`

1. Export the key to a certificate file:
`keytool -export -alias your_alias -file cert_file -keystore your_keystore`

1. Now you can generate your certificate signing request:
`keytool -certreq -alias your_alias -keystore your_keystore -file certreq_file`

Keep all files you've generated (the key pair, the keystore, and the csr) secure, you will need them later.

For more information about keytool arguments, see the Java Documentation about [keytool](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/keytool.html) on the Oracle website.


__Step 2: Get the CSR signed by the certificate authority__

Send the certificate signing request to the CA you want to create a certificate for you (for example, Verisign or Thawte). The CA will sign the CSR file with their own signature and send that certificate back to you. You can then use this signed certificate to sign the TACO file.

After you receive/fetch the new certificate from the CA, along with any applicable "chain" or intermediate certificates, run the following command to install the new certificate and chain into the keystore:
`keytool -importcert cert_from_ca -keystore your_keystore`

__Step 3: Use jarsigner to sign TACO file__

Using the keystore you imported your signed certificate to, use jarsigner to sign your TACO file:
`jarsigner -keystore your_keystore path_to_taco your_alias -tsa url`

The `-tsa url` argument is optional, but **strongly encouraged**. It's the url to a Timestamp Authority, and by adding this argument you will stamp the signed TACO file with a timestamp, extending its period of validity. While there are several free options for timestamp authority, the CA you got the certificate from will most likely have a timestamp authority you can use.

For more information about jarsigner arguments, see the Java Documentation about [jarsigner](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/jarsigner.html).

__Note:__ Earlier versions of the packager signed your connector using jarsigner internally. This functionality was removed in favor of the connector author calling jarsigner directly, which provides more control over how your connector is signed.

## Troubleshoot connector packaging and signing

__Where to find log files__

By default, a log file packaging_log.txt is generated in connector-plugin-sdk/connector-packager/.

__XML validation failed for manifest.xml__  

This means that the packaging process failed.

- Check [your_path]\connector-plugin-sdk\connector-packager\packaging_log.txt for more information. 

- Check your manifest.xml file. You can do validate only with –v to get more details and make sure your package is valid. 
For example: 

```
(.venv) E:\packagetest\connector-plugin-sdk\connector-packager>python -m connector_packager.package --validate-only e:\badplugins\mysql_odbc –v 
```

__Java error__

If you get this error:
_Java error: jdk_create_jar: no jdk set up in PATH environment variable, please download JAVA JDK and add it to PATH_

Check your PATH environment variable and make sure that JAVA_HOME is in PATH.

