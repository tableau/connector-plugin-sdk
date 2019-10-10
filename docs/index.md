---
title: Tableau Connector SDK
---

With the Tableau Connector SDK, you can add a new connector that you can use to visualize your data from any database through an ODBC or JDBC driver.
When you create a connector, you can add customizations to the connector, use the connectivity test harness to validate the connector behavior during the development process, and then package and distribute the connector to users.
This document describes the files that make up a connector.

## What is a connector?

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

- Install the ODBC or JDBC driver that you’ll use with the connector you’ll create.
- Install Tableau Desktop 2019.2 or later on a Windows or Mac computer.

## Using a Connector

You must start Tableau Desktop or Tableau Server with a special command line argument that tells Tableau where to find your Connector. See [Run Your Connector]({{ site.baseurl }}/docs/share) for more information.

**Tableau Desktop:** 

For Windows:
1. Create a directory for Tableau connectors. For example: `C:\tableau_connectors`
1. Put the folder containing your connector's manifest.xml file in this directory. Each connector should have its own folder. For example: `C:\tableau_connectors\my_connector`
1. Run Tableau using the `-DConnectPluginsPath` command line argument, pointing to your connector directory. For example: 

    ```
    tableau.exe -DConnectPluginsPath=C:\tableau_connectors
    ```

For macOS:

In the following examples, replace [user name] with your name (for example /Users/agarcia/tableau_connectors) and [Tableau version] with the version of Tableau that you’re running (for example, 2019.3.app).

1. Create a directory for Tableau connectors. For example: `/Users/[user name]/tableau_connectors`
1. Put the folder containing your connector's manifest.xml file in this directory. Each connector should have its own folder. For example: `/Users/[user name]/tableau_connector/my connector`
1. Run Tableau using the `-DConnectPluginsPath` command line argument, pointing to your connector directory. For example: 

    ```
    /Applications/Tableau\ Desktop\ [Tableau version].app/Contents/MacOS/Tableau -DConnectPluginsPath=/Users/[user name]/tableau_connectors
        
    ```

