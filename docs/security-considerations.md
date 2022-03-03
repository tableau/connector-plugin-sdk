---
title: Security Considerations
---

Connectors built with the Connector SDK handle authentication and customer data, and handling these incorrectly can cause security vulnerabilities and leakage of sensitive data.

During the connector review for the Tableau Exchange, the connector will go through a security review. Addressing these security concerns is a requirement for the connector to be approved for the Exchange.

Tableau will also pull any connector from the Tableau Exchange that is found to have a security vulnerability. That vulnerability must be addressed before the connector can return to the Exchange.


# Secure Attributes on the Connection Dialog

The Connector SDK allows the connection dialog to be customized, using platform-defined fields as well as the creation of new, vendor-specific fields. It is important to note that these fields, with the exception of the built-in `password` field, are not secure. **The values of every non-secure UI field on the connection dialog will be logged in plain text by Tableau as well as persisted in easily-inspectable XML in Tableau workbooks, datasources and Prep flows.**

Currently the only field that can be marked secure is `password`. This means that the values customers enter for vendor-specific fields **must not contain secrets, credentials or personally identifiable information (PII),** and connectors with such fields will not be approved for the Tableau Exchange. This is a known limitation of the SDK and we are looking at ways to remove this constraint in the long term.

Examples of problematic UI fields that will be rejected:
- Proxy Password
- OAuth secrets (Use the official [Tableau OAuth flow](({{ site.baseurl }}/docs/oauth)) instead)
- **Freeform Driver Properties** (See following section)

## Freeform Driver Properties

**Freeform Driver Properties fields are not supported in the Connector SDK, and connectors using them will not be approved for the Tableau Exchange.** A "Freeform Driver Properties" field allows the user to manually enter key-value pairs that will be passed directly to the driver. However, because all vendor-defined fields are non-secure, these key-value pairs will be logged in plain text and persisted in easily-inspectable XML in Tableau workbooks, datasources and Prep flows. Many driver properties are considered sensitive, and we cannot enforce that users will not enter these sensitive key-value pairs, therefore we consider "Freeform Driver Properties" fields a security vulnerability.

We recommend the following workarounds instead of an "Freeform Driver Properties" field:
- To unblock users needing to set non-sensitive driver properties, add them as separate fields on the Advanced tab using [Connection Dialogs V2 framework](({{ site.baseurl }}/docs/mcd))
- For JDBC, Customers can set driver properties using [JDBC Properties files](https://kb.tableau.com/articles/howto/Customizing-JDBC-Connections)

# Driver Vulnerabilities

The Tableau Exchange does not host drivers, and the responsibility of ensuring the driver is secure falls onto the driver authors.

There is an additional process for connectors that are hosted in Tableau Online. Tableau will need to host the driver in our environments, so the driver will be scanned for security vulnerabilities, including out-of-date and vulnerable third-party libraries.

# JDBC Connectors not using connection-properties component

While ODBC connectors only have a connection-builder script that builds the connection string, JDBC has a connection-builder script that builds the JDBC URL and a connection-properties script that passes properties directly to the driver.

**The JDBC URL will be logged in plain text by Tableau in the std_jprotocolserver.txt file**. This means that anything added to the JDBC URL in the connection-builder script will be logged, including username and password if the connector incorrectly handles these fields (despite password being a secure field). To avoid this, make sure all authentication-related attributes are sent to the driver as properties in the connection-properties script, and not appended to the JDBC URL in the connection-builders script.

