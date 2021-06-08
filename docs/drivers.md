---
title: Driver Requirements
---

Connectors built with the Connector SDK use either an ODBC or a JDBC driver to communicate with the database.

In general, we prefer JDBC connectors to ODBC connectors, as JDBC is cross-platform.


# JDBC Drivers
To learn more about JDBC drivers and Tableau, check *Specify the right JDBC driver* section in  the  [user documentation](https://help.tableau.com/current/pro/desktop/en-us/examples_otherdatabases_jdbc.htm).

## Requirements
- You must have read permissions on the JAR file.
- Tableau requires a JDBC 4.0 or later driver.
- Tableau requires a Type 4 JDBC driver.

## JDBC Driver Class Isolation
If the driver only includes a single jar file, copy it to the JDBC driver location. <br/>
If the driver includes more than a single file, create a unique subfolder under JDBC driver location and include all required files.
- Windows: C:\Program Files\Tableau\Drivers
- Mac: ~/Library/Tableau/Drivers
- Linux: /opt/tableau/tableau_driver/jdbc
<br/>

 This will create an isolated classloader for that driver.

# ODBC Drivers
To learn more about ODBC drivers and Tableau, check the *Tableau and ODBC* page in the [user documentation](https://help.tableau.com/current/pro/desktop/en-us/odbc_tableau.htm)

## Requirements
- Tableau requires an ODBC version of 3 or higher

# Important SQLStates

Tableau expects correct SQLStates to be returned in certain situations. Inaccurate SQLStates (for example, returning a generic error instead of SLQState 28000 for invalid credentials) may cause bugs in the connector.

SQLSTATE | Error | Scenario
- | - | -
1002 | Disconnect Error | Connection is disconnected
08001 | Unable to Connect | Client unable to connect to server
28000 | Invalid Authorization Specialization | User enters invalid credentials (Bad username\password, etc)

You can see the full list of SQLSTATES in the official [ODBC documentation](https://docs.microsoft.com/en-us/sql/odbc/reference/appendixes/appendix-a-odbc-error-codes?view=sql-server-ver15) and official [JDBC documentation](https://docs.oracle.com/cd/E15817_01/appdev.111/b31228/appd.htm).