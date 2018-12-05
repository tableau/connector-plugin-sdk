# Tableau Connector Plugin SDK - BETA

![Tableau Supported](https://img.shields.io/badge/Support%20Level-Tableau%20Supported-53bd92.svg)

This project consists of a set of documentation, example files, and a Python based test harness that allows you to create and customize a Tableau Connector that uses ODBC or JDBC.

* [Why Connector Plugins?]()
* [Get started](#get-started)
* [Samples](#samples)
* [Prerequisites](#prerequisites)
* [FAQ](#faq)
* [Contributions](#contributions)

# Why Connector Plugins?

At Tableau, we pride ourselves in helping people see and understand their data... wherever it may be. A key investment for us has been creating a way to enable both partners and customers help us in this mission. Thank you for expressing your interest in joining us on that mission.  On behalf of the Connectivity team at Tableau, I’d like to announce the early release of our Connector Plugin SDK! 

For more information please submit a GitHub Issue here.

# Get started

We have created an extensive getting started guide to design, and test your Connector Plugin that can be found here: https://tableau.github.io/connector-plugin-sdk/

# Samples

We have created two standalone Postgres example connectors using ODBC and JDBC that can be found here [SAMPLES_LINK] 

# Prerequisites

To work with Connector Plugins, you need the following:

* Windows Mac or Linux
* Tableau Desktop or Server V. 2019.1 Beta 2 or higher
* Python [Version??]
* An ODBC or JDBC data source and driver

# FAQ
**If I build a plugin, will Tableau include it?**  

Not necessarily. We plan to include connector plugins on a case by case basis. The work needed to include connectors with a shipping Tableau product extends well beyond the code itself and into continuous integration and supportability concerns. We are looking at providing a way to include third-party connectors in the future through some exciting new features as well as a more formal certification program.

**Why would I build a plugin instead of just telling users to use Other ODBC/JDBC?**
   
Connector Plugins allow for a much more extensive level of customization than using generic “Other ODBC”, and it is possible to apply many of the optimizations that current "named" connectors in Tableau go through.  
 
**Can I make a plugin for OLAP Cubes, file-based, or REST API-based connections?**
We intend for the Connector Plugin SDK to eventually support additional connector types, but we're starting with ODBC and JDBC.  

**How would I distribute plugins to my customers?**
Until v1.0 is officially released, we do NOT recommend distributing Connector Plugins to customers. Based on your feedback we expect to iterate for the next two quarters with breaking changes to a number of plugin aspects.  

After v1.0, we expect to work with partners to review test results and discuss customer support processes.

**What types of things might change during the v1.0 of plugin development?**
Many things may change, but most likely how a Connector Plugin is packaged as well as the components associated with enterprise authentication. We highly encourage you to sign up here in GitHub or email us to get the latest information. Partners participating in the open sprint demos will get notice of any breaking changes in real-time.

# Contributions

Code contributions and improvements by the community are welcomed!
See the LICENSE file for current open-source licensing and use information.

Before we can accept pull requests from contributors, we require a signed [Contributor License Agreement (CLA)](http://tableau.github.io/contributing.html)
