---
title: Connector Design Considerations
---

The choices you make when creating a connector can include which superclass and dialect to use, and how you want to tune your connection using Tableau capabilities.

## Choose a connection class

The <span style="font-family: courier new">class</span> attribute is a unique key for your connector. Make it something that is unlikely to be used by another connector. When Tableau loads the connectors at startup, if the class is already registered, the connector will not be loaded. The class is also stamped in Tableau Workbook (.twb or .twbx) files and Tableau Datasource (.tds) files to identify what connector that particular connection was using.

## Choose a superclass

Connectors work using an inheritance pattern. The superclass refers to the Tableau native connector from which your connector inherits behavior.

Because Tableau’s native connectors have special code and optimizations that may not be appropriate for your connection, we recommend using "odbc" or "jdbc" for your superclass. These connect to and retrieve data in a standard way and can be further customized as needed.

These are available <span style="font-family: courier new">superclass</span> values:

- odbc
- jdbc
- mysql_odbc

You might find other superclass values in the workbook XML from an existing Tableau connection, but we don't recommend using them. They haven't been tested.

## Choose a dialect

The dialect determines what SQL is generated for various Tableau actions. 

Choosing the right dialect is a critical part of writing a connector. For example:

- If you set <span style="font-family: courier new">base</span> to "mysql_odbc' as the parent, you can skip configuring a dialect, and your connector will use the parent’s dialect.
- If your database follows the SQL standards of another database that Tableau already supports (listed below), then you can choose that dialect as a starting point.

These are valid values for <span style="font-family: courier new">base</span>:

- BigQuerySQLDialect
- DB2Dialect
- DenodoDialect
- DrillDialect
- EXASolution5Dialect
- Firebird21Dialect
- GreenplumDialect
- Hive12Dialect
- Impala23Dialect
- JetDialect
- MySQL41UnicodeDriverDialect
- Oracle102Dialect
- PostgreSQL90Dialect
- PrestoDialect
- ProgressOpenEdgeDialect
- RedShiftDialect
- SQLServer10Dialect_Datetime2
- SnowflakeDialect
- SybaseASEDialect
- SybaseIQ151Dialect
- Teradata1410Dialect
- VerticaDialect

### Should I create a diralect definition file?

If you want to customize the generated SQL, or if your connector inherits from ODBC or JDBC, then you need to create a custom dialect file. Without a file, the dialect from the superclass is used. For more information, see [Create a Tableau Dialect Definition (TDD) File]({{ site.baseurl }}/docs/dialect).

## Set connection capabilities

Tableau capabilities are Boolean settings you can use to tune many aspects of your connector behavior, including:
- The types of queries that Tableau generates
- How metadata is read
- How Tableau binds to the drivers result set

For information on common capabilities and how they are used, see [Capabilities]({{ site.baseurl }}/docs/capabilities).

## Consider database capability 

Consider these two questions:

__Does your database support temporary tables?__  
__Important:__ Your database should support temporary tables and subqueries for the best user experience, but at least one of those is required to support complete integration with Tableau.   
  
If your database supports temp tables, we recommend that you enable them through the appropriate [Capabilities]({{ site.baseurl }}/docs/capabilities). If the temp table capabilities are set, the connector will perform a simple check at connection time to confirm that the user can create a temp table in the current database environment. If the user does not have permission or the capabilities are disabled, then Tableau will attempt to generate an alternative query to retrieve the necessary results. Often these queries need subqueries and the performance can be poor, particularly with large data sets. If the connector does not support temporary tables or subqueries, then Tableau will report an error and will be unable to proceed.    
   
A common example is filtering the top three regions by sum of sales. You can try this using our Staples sample table by dragging [Market Segment] to __Rows__, then drag it again to __Filters__. Click the Top tab and select [Sales Total] aggregated by sum.

__Does your database support null column metadata?__  
Tableau relies on accurate column metadata from the ODBC or JDBC result set in order to make certain query optimizations. If information about whether a column contains null values is inaccurate, Tableau may generate inefficient or incorrect queries. If your database does not support null column information, then it is safer to indicate that all columns contain null values. This ensures that Tableau does not generate an optimized query that actually returns incorrect results.
Tableau uses "SQLColAttribute" with "SQL_DESC_NULLABLE" on the result set metadata for ODBC connections and the "isNullable" method on the "ResultSetMetaData" object for JDBC.
