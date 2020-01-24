---
title: Tableau Connector SDK
---

With the Tableau Connector SDK, you can add a new connector that you can use to visualize your data from any database through an ODBC or JDBC driver.
When you create a connector, you can add customizations to the connector, use the connectivity test harness to validate the connector behavior during the development process, and then package and distribute the connector to users.
This document describes the files that make up a connector.

# What is a Connector?

A connector is a set of files that describe:

- UI elements needed to collect user input for creating a connection to a data source
- Any dialect or customizations needed for the connection

And include:

- A connection string builder
- A driver resolver

A connector supports the same things any other connector supports, including publishing to a server if the server has the connector, creating extracts, data sources, vizzes, and so on.

See the relationship between the connector files (in blue) and the Tableau **Connect** pane and connection dialog:

![]({{ site.baseurl }}/assets/files-overview.png)

# What is a Taco?
A `.taco` file is a packaged Tableau Connector file that can be dropped into your `My Tableau Repository/Connectors` folder. They will be automatically loaded by Tableau.

For more information about packaging your connector into a Taco, refer to [Package and Sign Your Connector for Distribution]({{ site.baseurl }}/docs/package-sign)

# Before you Begin

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
