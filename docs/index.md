---
title: Tableau Connector SDK
---

With the Tableau Connector SDK, you can add a new connector that you can use to visualize your data from any database through an ODBC or JDBC driver.
When you create a connector, you can add customizations to the connector, use the connectivity test harness to validate the connector behavior during the development process, and then package and distribute the connector to users.
This document describes the files that make up a connector.

## What is a connector plugin?

A connector is a set of files that describe:

- UI elements needed to collect user input for creating a connection to a data source
- Any dialect or customizations needed for the connection

And include:

- A connection string builder
- A driver resolver

A connector supports the same things any other connector supports, including publishing to a server if the server has the connector, creating extracts, data sources, vizzes, and so on.

See the relationship between the connector files (in blue) and the Tableau **Connect** pane and connection dialog:

![]({{ site.baseurl }}/assets/files-overview.png)

## Before you begin

You need to do these things before you start:

- Install the ODBC or JDBC driver that you’ll use with the plugin connector you’ll create.
- Install Tableau Desktop on a Windows or Mac computer.
