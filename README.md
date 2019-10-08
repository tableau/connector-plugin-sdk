# Tableau Connector SDK - BETA

![Tableau Supported](https://img.shields.io/badge/Support%20Level-Tableau%20Supported-53bd92.svg) [![Build Status](https://travis-ci.org/tableau/connector-plugin-sdk.svg?branch=master)](https://travis-ci.org/tableau/connector-plugin-sdk)

This project consists of documentation, example files, and a Python-based test harness that you can use to build and customize a Tableau Connector that uses an ODBC or JDBC driver.

* [Why Connectors?](#why-connectors)
* [Get started](#get-started)
* [Samples](#samples)
* [Prerequisites](#prerequisites)
* [Get Help](#get-help)
* [FAQ](#faq)
* [Contributions](#contributions)

# Why Connectors?

At Tableau, we pride ourselves in helping people see and understand their data... wherever it may be. A key investment for us has been creating a way to enable both partners and customers help us in this mission. Thank you for expressing your interest in joining us on that mission. On behalf of the Connectivity team at Tableau, I’d like to announce the early release of our Connector SDK!

# Get started

Review the [Tableau Connector SDK developer guide](https://tableau.github.io/connector-plugin-sdk/) to help you design, build, and test your connector.

# Samples

There are two [standalone Postgres example connectors](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins) that use ODBC and JDBC.

# Prerequisites

To work with connectors, you need the following:

* Windows or Mac
* Tableau Desktop or Server 2019.1 Beta 2 or higher
* Python 3.7 or higher
* An ODBC or JDBC data source and driver
* The provided test data loaded in your data source

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

# Contributions

Code contributions and improvements by the community are welcomed!
See the LICENSE file for current open-source licensing and use information.

Before we can accept pull requests from contributors, we require a signed [Contributor License Agreement (CLA)](http://tableau.github.io/contributing.html)
