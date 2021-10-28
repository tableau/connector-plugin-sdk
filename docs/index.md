---
title: Tableau Connector SDK
---
Tableau has great connectivity that allows you to visualize data from virtually anywhere. Tableau includes dozens of connectors already, and also gives you the tools to build a new connector with the Tableau Connector SDK.

With this SDK, you can create a connector that you can use to visualize your data from any database through an ODBC or JDBC driver.
You can customize connector behavior, fine-tune SQL generation, use the connectivity test harness to validate the connector behavior during the development process, and then package and distribute the connector to users.

# What is a Tableau connector?

A connector is a set of files that describe:

- UI elements needed to collect user input for creating a connection to a data source
- Any dialect or customizations needed for the connection
- How to connect using the ODBC or JDBC driver

A connector can have most of the same features that any built-in Tableau connector supports, including publishing to a server if the server has the connector, creating extracts, data sources, vizzes, and so on.

A connector developed using this SDK is appropriate for connecting to an ODBC or JDBC driver that interfaces using SQL. The underlying technology works well with relation databases.

See the relationship between the connector files (in blue) and the Tableau **Connect** pane and connection dialog:

![]({{ site.baseurl }}/assets/files-overview.png)

# Why build a connector?

You can user the "Other Databases (ODBC)" and "Other Databases (JDBC)" connectors to connect to your database. The Tableau Connector SDK is similar, but offers the following advantages:
- Better live query support. You can customize the dialect used to generate SQL queries so they are compatible and optimized for your database. The Other Database connectors rely on higher-level standard SQL that may not always be appropriate.
- Simpler connection experience. An SDK connector can provide its own customized dialect and you do not need to rely on using DSNs. Users will not need to enter in obscure JDBC URL strings or create a DSN or configure odbc.ini files. Your connector can provide a simple customized connection dialog.
- Runs in Tableau Desktop and Tableau Server. No configuration is required after you install the connector.

If your data source does not fit the relational ODBC/JDBC model, then it may be worth looking into [Web data connectors](https://tableau.github.io/webdataconnector).

# What is a TACO file?
A TACO file (.taco)  is a packaged Tableau connector file that can be placed in your "My Tableau Repository/Connectors" folder. From there, Tableau automatically loads all connectors it finds.

For more information about packaging your connector into a TACO, see [Package and sign your connector for distribution]({{ site.baseurl }}/docs/package-sign)

# Overview of the process

These are the general steps you will follow to create a fully functional connector.

1. Have a look at one of the sample connectors located in the [postgres_odbc or postgres_jdbc folder](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins). These connectors can make a good starting point if you copy the connector files to your workspace.

2. Customize the connector files as needed to name your connector and allow it to connect to your database. See the [Example]({{ site.baseurl }}/docs/example) for more information.

3. Make sure your connector has all the required files:
> * __Manifest file__. This defines the connector.
> * __Connection resolver (ODBC-based connectors only)__. ODBC connectors should include a driver-resolver element. JDBC connectors do not currently support the driver-resolver.
> * __Connection builder JavaScript file__. JDBC connectors can make use of a properties builder JavaScript file.
> * __Dialect definition file__.
> * __Connection dialog__.

4. After your connector is able to connect, start running the test tool [TDVT]({{ site.baseurl }}/docs/tdvt) to verify your connector is compatible with Tableau. Load the test data into your database, [for example](https://github.com/tableau/connector-plugin-sdk/blob/master/tests/datasets/TestV1/postgres/README.md).

5. When the TDVT tests are passing you are ready to [package and sign your connector]({{ site.baseurl }}/docs/package-sign).

## Prerequisites for development

To develop connectors, be sure you have the following installed on your computer:
- Windows or Mac operating system
- Tableau Desktop or Tableau Server 2019.2 or higher
- __Note:__ Tableau 2019.4 is required to run TACO files
- Python 3.7 or higher
- An ODBC or JDBC data source and driver that meets the requirements listed [here]({{ site.baseurl }}/docs/drivers)
- The provided test data loaded in your data source
- JDK 8 or higher

## Install the SDK tools
Install the following:
 - __TDVT.__ This is our test harness. See the "Installation" section of [Test Your Connector Using TDVT]({{ site.baseurl }}/docs/tdvt) for details.
 - __The packaging tool__. See the "Set up the virtual environment for packaging and signing" section of [Package and sign your connector for distribution]({{ site.baseurl }}/docs/package-sign) for details.

The resulting connector will work on Tableau Desktop and Tableau Server on Windows, Linux, and Mac.

# Using a connector

## Packaged connector (TACO)
Place your packaged TACO file in the My Tableau Repository/Connectors folder and launch Tableau. See [Run your packaged connector (.taco)]({{ site.baseurl }}/docs/run-taco) for more information.

Note: Support for loading TACO files was added in the 2019.4 release of Tableau.

## Developer path
You can tell Tableau to load unpackaged connectors with a special command-line argument that tells Tableau where to find your connector. See [Run Your "Under Development" Connector]({{ site.baseurl }}/docs/run-taco#run-your-under-development-connector) for more information.
