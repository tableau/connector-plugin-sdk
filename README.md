# Tableau Connector SDK - BETA

![Tableau Supported](https://img.shields.io/badge/Support%20Level-Tableau%20Supported-53bd92.svg) [![Connector Packaging CI Status](https://github.com/tableau/connector-plugin-sdk/workflows/Connector%20Packager%20CI/badge.svg?branch=master)](https://github.com/tableau/connector-plugin-sdk/actions?query=workflow%3A%22Connector+Packager+CI%22+branch%3Amaster++) [![TDVT CI Status](https://github.com/tableau/connector-plugin-sdk/workflows/TDVT%20CI/badge.svg?branch=master)](https://github.com/tableau/connector-plugin-sdk/actions?query=workflow%3A%22TDVT+CI%22+branch%3Amaster)

This project consists of documentation, example files, the Tableau Datasource Verification Tool (TDVT) test harness, and a packaging tool that you can use to build and customize a Tableau Connector that uses an ODBC or JDBC driver.

| Tool                                             | Latest Version     |
|--------------------------------------------------|--------------------|
| Connector Packager SDK (Beta) for Tableau 2019.3 | 12-11-2019         |
| TDVT                                             | 2.1.7 (02-04-2020) |
| Connector Packager                               | 0.0.1 (10-03-2019) |

* [Why Connectors?](#why-connectors)
* [Get started](#get-started)
* [Samples](#samples)
* [Prerequisites](#prerequisites)
* [Get Help](#get-help)
* [FAQ](#faq)
* [Known Issues](#known-issues)
* [Contributions](#contributions)

# Why Connectors?

At Tableau, we pride ourselves in helping people see and understand their data... wherever it may be. A key investment for us has been creating a way to enable both partners and customers help us in this mission. Thank you for expressing your interest in joining us on that mission. On behalf of the Connectivity team at Tableau, I’d like to announce the early release of our Connector SDK!

# Get started

Review the [Tableau Connector SDK developer guide](https://tableau.github.io/connector-plugin-sdk/) to help you design, build, and test your connector.

You can also watch our [Tableau Conference 2019 talk](https://www.youtube.com/watch?v=_rfQtHLWWxU), where two of our developers walk through the basics of creating a custom Tableau connector and packaging it into a single `.taco` file.

# Samples

The SDK includes several [standalone example connectors](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins) that use ODBC and JDBC.

# Prerequisites

To work with connectors, you need the following:

* Windows or Mac
* Tableau Desktop or Server 2019.1 Beta 2 or higher
* Python 3.7 or higher
* An ODBC or JDBC data source and driver
* The provided test data loaded in your data source

To package the connector into a .taco file, you will also need:

* Tableau Desktop or Server 2019.4 Beta 1 or higher
* JDK 8 or higher

For a JDBC connector, your driver must fulfill the following requirements:

* You must have read permissions on the .jar file.
* Tableau requires a JDBC 4.0 or later driver.
* Tableau requires a Type 4 JDBC driver.

# Get Help

This SDK is supported, so if you have problems getting the test harness set up, find defects, or have questions related to the configuration or testing of your connector:
* Start by submitting a GitHub Issue here in this project
* or you can reach us on the [Developer Forums](https://community.tableau.com/community/developers/content) in Tableau Community.


# FAQ
**If I build a connector, will Tableau include it?**

Not necessarily. We plan to include connectors on a case by case basis. The work needed to include connectors with a shipping Tableau product extends well beyond the code itself and into continuous integration and supportability concerns. We are looking at providing a way to include third-party connectors in the future through some exciting new features, as well as a more formal certification program.

**Why would I build a connector instead of just telling users to use the Other Databases (ODBC/JDBC) connector?**

Connectors allow for a much more extensive level of customization than using the generic Other Databases (ODBC/JDBC) connector does. When you build a connector, it's possible to apply many of the optimizations that current "named" connectors in Tableau use.

**Can I make a connector for OLAP Cubes, file-based, or REST API-based connections?**
We intend for the Connector SDK to eventually support additional connector types, but we're starting with ODBC and JDBC.

**How do I distribute a connector to my customers?**
Until v1.0 is officially released, we do NOT recommend distributing connectors to customers. Based on your feedback, we expect to iterate for the next two quarters with breaking changes to a number of connector aspects.

After v1.0, we expect to work with partners to review test results and discuss customer support processes.

**What types of things might change during the v1.0 of connector development?**
Many things might change, but the most likely changes are how a connector is packaged, and the components associated with enterprise authentication. We highly encourage you to sign up here in GitHub or email us to get the latest information. Partners participating in the open sprint demos will get notice of any breaking changes in real-time.

[Visit the project website and documentation here.](https://tableau.github.io/connector-plugin-sdk/)


# Known Issues

## Current
**Support links that are not fully qualified throw error when clicked on**
Support links that are not fully qualified (ie include the https:// header) will throw an error when the user clicks on them. This only affects in-development connectors, as we check for this when packaging a connector into a Taco.


## Recently Fixed
**(Mac Only) Packaged Connectors (.taco files) throws unexpected error in 2019.4**
You can work around this by skipping signature verification with the command line argument `-DDisableVerifyConnectorPluginSignature=true`.
Fixed in 2019.4.1.

**The properties builder JavaScript truncates values containing the equals sign '=' in 2019.4**
A bug in the JavaScript translation layer means that you cannot return values containing the '=' character from the JavaScript properties builder.
Fixed in 2019.4.1.

# Contributions

Code contributions and improvements by the community are welcomed!
See the LICENSE file for current open-source licensing and use information.

Before we can accept pull requests from contributors, we require a signed [Contributor License Agreement (CLA)](http://tableau.github.io/contributing.html)
