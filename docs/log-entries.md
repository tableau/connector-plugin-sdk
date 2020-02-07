---
title: Signature Verification Log Entries
---
 
When the signature verification completes and the connector loads, entries are made to the logs. This page describes the log entries. 

The log file is called log.txt and is located in the \My Tableau Repository\Logs folder.
 
## Connector loads after the signature is verified

### Log entry examples

#### .taco verified.

The certificate used for signing is a valid and a trusted one, and the signature verification succeeded. Since the integrity and identity of the connector is verified, Tableau loads the connector. 

#### Signed by: CN=A, OU=B, O=C, L=D, ST=E, C=F 

This displays information about the connector .taco developer:

   **CN=A** is the first and last name of the developer   
   **OU=B** is the organizational unit   
   **O=C** is the organization  
   **L=D** is the organization's city  
   **ST=E** is the organization's state  
   **C=F** is the organization's country

## Connector fails to load because the signature isn't verified
Unexpected Error: Error Code 14D18B1F. Package signature verification failed during connection creation.
If this error dialog opens when you try to connect, it means that the connector couldn't be verified. Look at the logs for more information on the reason for the failure.

![]({{ site.baseurl }}/assets/log-entries-error.png) 

### Log entry examples

#### .taco is not signed.

The connector hasn't been signed with a certificate. As a result, the integrity and the identity of the connector cannot be verified, and Tableau won't load the connector.taco package. 

#### There are unsigned files in the .taco.

The connector.taco package has files that haven't been signed with a certificate. As a result, the integrity of the package file cannot be authenticated, and Tableau won't load the connector.taco. 

#### The signer certificate chain is not validated.

The .taco package has been signed with a certificate, but the authenticity of the certificate cannot be verified because this is a self-signed certificate. Because it isn't a trusted certificate, Tableau won't load the connector.taco. If you trust the connector.taco developers, you can contact them for the public certificate so that you can import it in the trusted keystore. For detailed steps, see ‘Import a certificate to the trusted keystore.’

#### Failed to get trusted certificates from JRE keystore.

Tableau was not able to load the trusted JRE keystore. This can happen if the JRE is not installed or the file "$PATH_TO_JRE\lib\security" (for example, "C:\Program Files (x86)\Java\jre1.8.0_221\lib\security") is not accessible 

#### The signer certificate has expired.

The certificate that the connector.taco developer used to sign the package is expired. Tableau doesn't rely on expired certificates because of security concerns. As a result, Tableau won't load the connector. To resolve this issue, contact the connector.taco developer. 

#### The signer certificate is not yet valid.

The certificate that the connector.taco developer used to sign the package is not yet valid and is meant to be used at a later date. Tableau doesn't rely on certificates not yet valid. As a result, Tableau won't load the connector. To resolve this issue, contact the connector.taco developer. 
 
## Import a certificate to the trusted keystore 
 
For signature verification, Tableau relies on public certificates being present in the JRE truststore.

If the connector.taco developer uses a self-signed certificate or a certificate issued from a certificate authority that doesn't have its public certificate in the JRE truststore, the signed .taco package won't pass the signature verification process. As a result, Tableau won't load the connector. 

If you trust the connector.taco developer, then you can import the public certificate provided by the connector.taco developer into the JRE truststore. After this is done, the certificate that the connector.taco developer used is trusted and the signature verification step passes if the connector.taco has not been tampered with, otherwise it will fail.

Follow these steps to add the certificate from the connector.taco developer to the JRE truststore. Before you begin, JRE must be installed.

1. Contact the connector.taco developer for the public certificate to be imported into the JRE truststore.

1. Execute the following command:  

   ```
   keytool -importcert -file [path_public_certificate] -keystore [path_to_JRE_truststore] -alias [alias_name] 
   ```
   In the command above: 

   **path_public_certificate** is the path to the public certificate provided by the connector.taco developer to be imported to the JRE truststore. 
 
   **path_to_JRE_truststore** is the path to the JRE truststore. The JRE truststore is located here by default:

      $PATH_TO_JRE\lib\security

      For example: C:\Program Files (x86)\Java\jre1.8.0_221\lib\security 
 
   **alias_name** is any alias name that you want the certificate to be stored as.

 
1. On the prompt to enter the password, enter the password for the JRE truststore. The default password is `changeit`.
 
1. After running the command, when prompted if the certificate should be trusted, type in `yes`. 

