---
title: Tableau Connector SDK
---

With the Tableau Connector SDK, you can create a new connector that you can use to visualize your data from any database through an ODBC or JDBC driver.
You can customize connector behavior, finely tune SQL generation, use the connectivity test harness to validate the connector behavior during the development process, and then package and distribute the connector to users.
This document provides and overview of what a connector is and how it is created.

# What is a Connector?

A connector is a set of files that describe:

- UI elements needed to collect user input for creating a connection to a data source
- Any dialect or customizations needed for the connection
- How to connect using the ODBC or JDBC driver

A connector can have most of the same features that any built-in Tableau connector supports, including publishing to a server if the server has the connector, creating extracts, data sources, vizzes, and so on.

A connector developed using this SDK is appropriate for connecting to an ODBC or JDBC driver which interfaces using SQL. The underlying technology works well with relation databases.

See the relationship between the connector files (in blue) and the Tableau **Connect** pane and connection dialog:

![]({{ site.baseurl }}/assets/files-overview.png)

# Why build a Connector?

You can user the 'Other Databases (ODBC)' and 'Other Databases (JDBC)' connectors to connect to your database. The Connector SDK is similar but offers the following advantages:
- Better live query support. You can customize the dialect used to generate SQL queries so they are compatabile and optimized for your database. The Other Database connectors rely on higher level standard SQL which may not always be appropriate.
- Simpler connection experience. An SDK connector can provide it's own customized dialect and you do not need to rely on using DSNs. Users will not need to enter in obscure JDBC URL strings or create a DSN or configure odbc.ini files. Your connector can provide a simple customized connection dialog.
- Runs in Tableau Desktop and Tableau Server. No configuration is required once you install the Connector.

If your datasource does not fit the relational ODBC/JDBC model then it may be worth looking into [Web Data Connectors](https://tableau.github.io/webdataconnector).

# What is a Taco?
A `.taco` file is a packaged Tableau Connector file that can be dropped into your `My Tableau Repository/Connectors` folder. They will be automatically loaded by Tableau.

For more information about packaging your connector into a Taco, refer to [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign)

# Before you Begin

## Recommended Workflow

At a high level, these are the general steps you will need to follow to create a fully functional connector.

First, look at one of the sample connectors located in the [postgres_odbc or postgres_jdbc folder](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins). These connectors can make a good starting point if you copy the connector files to your workspace.

Second, customize the connector files as needed to name your connector and allow it to connect to your database. See the [Example]({{ site.baseurl }}/docs/example) for more information. The following files are required for all connectors:
- a manifest to define the connector.
- a connection resolver. ODBC connectors should include a driver-resolver element but JDBC connectors do not currently support the driver-resolver.
- a connection builder JavaScript file. JDBC connectors can make use of a properties builder JavaScript file.
- a dialect.
- a connection dialog.

Once your connector is able to connect, you're ready to start running the test tool [TDVT]({ site.baseurl }}/docs/tdvt) to verify your connector is compatible with Tableau. Load the test data into your database, [for example](https://github.com/tableau/connector-plugin-sdk/blob/master/tests/datasets/TestV1/postgres/README.md).

When the TDVT tests are passing you are ready to [package and sign your connector]({{ site.baseurl }}/docs/package-sign).

## Prerequisites:

To develop connectors, you need the following installed on your machine:
- Windows or Mac
- Tableau Desktop or Server 2019.2 or higher
- Python 3.7 or higher
- An ODBC or JDBC data source and driver
- The provided test data loaded in your data source

To package the connector into a `.taco` file, you will additionally need:
- Tableau Desktop or Server 2019.4 or higher
- JDK 8 or higher

## Install the Connector SDK tools:
- Install TDVT, our test harness. Refer to the "Installation" section of the [Test Your Connector Using TDVT]({{ site.baseurl }}/docs/tdvt) page.
- Install the packaging tool. Refer to the "Set up the virtual environment for packaging and signing" section of the [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign) page.

The resulting connector will work on Tableau Desktop and Tableau Server on Windows, Linux, and Mac.

# Using a Connector

## Packaged Connector (Taco)
Drop your packaged `.taco` file into your `My Tableau Repository/Connectors` and launch Tableau. See [Run your Packaged Connector (.taco)]({{ site.baseurl }}/docs/share) for more information.

Note: Support for loading Taco files was added in the 2019.4 release of Tableau.

## Developer Path
You can tell Tableau to load un-packaged connectors with a special command line argument that tells Tableau where to find your Connector. See [Run Your "Under Development" Connector]({{ site.baseurl }}/docs/share) for more information.
