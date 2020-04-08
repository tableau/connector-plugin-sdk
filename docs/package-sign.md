---
title: Package and Sign Your Connector for Distribution 
---

Packaging provides a convenient way to distribute your connector as a single .taco (Tableau Connector) file.  Signing ensures that Tableau will load only .taco files that have been signed, ensuring that they haven't been tampered with. Signing is done using the JDK and a certificate trusted by a root certificate authority (CA) that has been installed in your Java environment. Tableau Desktop verifies and loads signed connectors from a standard location (My Tableau Repository\\Connectors) or from a user supplied directory. 

This document explains how to package and sign your connector using the Connector SDK. 

## Before you begin 

Make sure you have the following:

-   Python version 3.7.3 or later 

-   Java JDK is installed, JAVA\_HOME is set, and the JDK is in your PATH environment variable 

-   Tableau Desktop 2019.4 or later   

-   A connector developed with the SDK that you would like to package or sign 

-   [Git](https://git-scm.com/downloads)

### Ensure your connector is ready to be packaged

As part of the packaging process, the packager ensures that:

-   All xml files are valid against the XSD files located in the validate folder of the SDK

-   All files referenced exist

-   All files are smaller than 3 MB

-   The connection class is the same in all places

However, this validation does not guarantee that the connector will work in Tableau. The packager does not validate JavaScript, for example, or that the connection class is unique. To ensure that your connector works before packaging it, you can [run your unpackaged connector]({{ site.baseurl }}/docs/share), or test it using [TDVT]({{ site.baseurl }}/docs/tdvt). 

### Set up the virtual environment for packaging

Follow these steps to get the packaging tool and set up the virtual environment. 

1.  Get the [Connector SDK repository](https://github.com/tableau/connector-plugin-sdk) on GitHub.

    For example, open a terminal in the directory where you want to copy the Tableau Connector SDK. Then run the following command to clone the Tableau Connector SDK git repository:

    ```
    git clone https://github.com/tableau/connector-plugin-sdk.git
    ```

1.  Set up the virtual environment by going to the connector-packager folder and running python –m venv .venv  

    For example: 

    ```
    C:\connector-plugin-sdk\connector-packager> python -m venv .venv
    ```

    For more information about venv, see [venv – Creation of virtual environments](https://docs.python.org/3/library/venv.html) on the Python website.

1.  Activate the virtual environment using the activate command. For example:

    On Windows:

    ```
    C:\connector-plugin-sdk\connector-packager>.\.venv\Scripts\activate  

    ```

    On Mac:

    ```
    mac-3:connector-packager qa.auto$ source ./.venv/bin/activate
    ```

    On Linux:

    ```
    [centos@ip-10-177-53-47 connector-packager]$ source ./.venv/bin/activate

    ```

1.  Install the packaging module in the virtual environment: 

    ```
    (.venv) C:\connector-plugin-sdk\connector-packager>python setup.py install  
    ```

## Package the connector

The connector-packager tool must be run from the connector-plugin-sdk/connector-packager/ directory. The packaged .taco file in default will be generated within packaged-connector folder. There are several ways to run the tool:

-   To package the connector, run this command: 
 
    ```
    python -m connector_packager.package [path_to_plugin_folder]
    ```

-   To validate that the .xml files are valid without packaging the connector, run this command:

    ```
    python -m connector_packager.package --validate-only [path_to_plugin_folder] 
    ```

Review the following examples:

### Example 1: .taco file is generated into connector-plugin-sdk\connector-packager\packaged-connector 

```
(.venv) E:\connector-plugin-sdk\connector-packager>python -m connector_packager.package ..\samples\plugins\mysql_odbc

Validation succeeded.

mysql_odbc_sample.taco was created in E:\connector-plugin-sdk\connector-packager\packaged-connector

```

### Example 2: .taco file is generated into user supplied location and log file is generated into user supplied location 

```
(.venv) E:\connector-plugin-sdk\connector-packager>python -m connector_packager.package ..\samples\plugins\mysql_odbc  --dest e:\temp -l e:\temp

Validation succeeded.

mysql_odbc_sample.taco was created in e:\temp

```

## Signing your packaged connector using jarsigner

At this point, your connector has been packaged into a single `.taco` file. However, it will not be loaded automatically into Tableau unless you sign the file, or disable signature verification.

### Why we require connectors to be signed

Connectors are sensitive parts of the Tableau code. They handle database authentication and communicate directly with your driver. By signing the connector, Tableau can verify the authenticity and integrity of the connector, and customers can be confident the the plugin author is who they say they are, and the `.taco` file itself has not been tampered with since it was signed.

### Getting your connector signed

A packaged Tableau Connector (`.taco`) file is, functionally, a `.jar` file. Tableau checks that packaged connectors are signed by a trusted certificate authority before loading them, using the default java keystore in the JRE. Because a `.taco` file is fundamentally a `.jar` file, you can follow Java documentation for signing jar files.

To sign a taco file, you must:
1. Generate a certificate signature request (csr). You can use java's [keytool](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/keytool.html) to generate this.
1. Send the csr to a certificate authority that is trusted by the java keystore. Make sure that certificate you get is a code-signing certificate.
1. Sign your `.taco` file using [jarsigner](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/jarsigner.html).
1. Verify that your `.taco` file is signed using jarsigner

### Verifying that .taco is properly signed

First, check tha the .taco is signed using jarsigner using the following command:

```
jarsigner -verify path_to_taco -verbose -certs -strict
```

If `jar verified` appears, your `.taco` file should be ready to be used in Tableau. Double check the certificate chain to make sure that the final certificate is that of your certificate authority.

### Example: Sign a .taco with a basic signed certificate

Getting a certificate is a multi-step process.

#### Step 1: Generate a Certificate Signing Request (csr) file

A certificate signing request (CSR) is a request for a certificate authority (CA) to create a public certificate for your organization.

First, generate a key pair using this command:

```
keytool -genkeypair -alias your_alias -keystore your_keystore
```

Next, export the key to a certificate file:
```
keytool -export -alias your_alias -file cert_file -keystore your_keystore
```

Now you can generate your certificate signing request:

```
keytool -certreq -alias your_alias -keystore your_keystore -file certreq_file
```

Keep all files you've generated (the key pair, the keystore, and the csr) secure, you will need them later.

For more information about keytool arguments, see the Java Documentation about [keytool](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/keytool.html) on the Oracle website.


#### Step 2: Get the CSR signed by the certificate authority

Send the certificate signing request to the CA you want to create a certificate for you (for example, Verisign, Thawte, or some other CA). The CA will sign the CSR file with their own signature and send that certificate back to you. You can then use this signed certificate to sign the .taco file.

After you receive/fetch the new certificate from the CA, along with any applicable 'chain' or 'intermediate' certificates, run the following command to install the new cert and chain into the keystore:

```
keytool -importcert cert_from_ca -keystore your_keystore
```

#### Step 3: Use jarsigner to sign .taco file

Using the keystore you imported your signed certificate to, use jarsigner to sign your `.taco` file:

```
jarsigner -keystore your_keystore path_to_taco your_alias
```

For more information about jarsigner arguments, see the Java Documentation about [jarsigner](https://docs.oracle.com/javase/8/docs/technotes/tools/windows/jarsigner.html).

### Historical Note

Earlier versions of the packager would sign your connector using jarsigner internally. This functionality was removed in favor of the connector author calling jarsigner directly, which provides more control over how your connector is signed.

## Troubleshoot connector packaging and signing


### Where to find log files 

By default, a log file packaging_log.txt will be generated at connector-plugin-sdk/connector-packager/

### XML Validation failed for manifest.xml  

Packaging failed. Check [your_path]\connector-plugin-sdk\connector-packager\packaging_log.txt for more information. 

Check your manifest.xml file. You can do validate only with –v to get more details and make sure your package is valid. For example: 

```
(.venv) E:\packagetest\connector-plugin-sdk\connector-packager>python -m connector_packager.package --validate-only e:\badplugins\mysql_odbc –v 
```

### Java Error: jdk_create_jar: no jdk set up in PATH environment variable, please download JAVA JDK and add it to PATH 

Check your PATH environment variable and make sure that JAVA_HOME is in PATH.

