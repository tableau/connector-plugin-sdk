---
title: Connector Design Considerations
---

The choices you make when creating a connector can include which superclass and dialect to use, and how you want to tune your connection using Tableau capabilities.

## Choosing a connection class

The class attribute is a unique key for your connector. When Tableau loads the connectors at startup, if the class has already been registered the connector will not be loaded. The class is also stamped in Tableau Workbook (.twb or .twbx) files and Tableau Datasource (.tds) files to identify what connector that particular connection was using.

## Choosing a superclass

Connectors work using an inheritance pattern. The superclass refers to the Tableau native connector your connector inherits the behavior of.

Because Tableau’s native connectors have special code and optimizations that may not be appropriate for your connection, we recommend using ‘odbc’ or ‘jdbc’ for your superclass. These handle connecting and retrieving data in a standard way and can be further customized as needed.

### Available superclass attributes

- odbc
- jdbc
- mysql_odbc

You might find other super class values in the workbook XML from an existing Tableau connection, but we don't recommend using them; they haven't been tested.

## Choosing a dialect

The dialect determines what SQL is generated for various Tableau actions. Choosing the right dialect is a critical part of writing a connector.

- If you choose 'mysql_odbc' as the parent, you can skip configuring a dialect, and your connector will use the parent’s dialect.
- If your database follows the SQL standards of another database that Tableau already supports (listed below), then you can choose that dialect as a starting point.

### Dialect base classes

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

### Should I create a dialect definition file?
If you want to customize the generated SQL, or your connector inherits from 'odbc' or 'jdbc', then you need a dialect file. Without a file, the dialect from the superclass is used. For more information, see [Create a Tableau Dialect Definition (TDD) File]({{ site.baseurl }}/docs/dialect).

## Setting connection capabilities

Tableau capabilities are Boolean settings you can use to tune many aspects of your connector behavior.
Capabilities can influence the types of queries that Tableau generates, how metadata is read, how Tableau binds to the drivers result set, and many other aspects.
Common capabilities and how they are used are described in [Capabilities]({{ site.baseurl }}/docs/capabilities).

## Database Capability Considerations
### Subqueries and Temp Tables

**Your database should support temporary tables and subqueries for the best user experience, but at least one of those is required to support complete integration with Tableau.**

If your database supports temp tables it is recommended that you enable them through the appropriate [Capabilities]({{ site.baseurl }}/docs/capabilities). The connector will perform a simple check at connection time if the temp table capabilities are set in order to confirm that the user has the ability to create a temp table in the current database environment. If the user does not have permission or the capabilities are disabled then Tableau will attempt to generate an alternative query to retrieve the necessary results. Often these queries will need subqueries and the performance can be poor, particularly with large data sets. If the connector does not support temporary tables or subqueries then Tableau will throw an error and will be unable to proceed.

A common example is filtering the top 3 regions by sum of sales. You can try this using our Staples sample table by dragging [Market Segment] to Rows, then drag it again to Filters. Click the ‘top’ tab and pick [Sales Total] aggregated by sum.

### NULL column metadata

Tableau relies on accurate column metadata from the ODBC or JDBC result set in order to make certain query optimizations. Tableau may generate inefficient or incorrect queries if information about whether a column contains Null values is inaccurate. If your database does not support Null column information then it is safer to indicate that all columns contain Null values. This will ensure that Tableau does not generate an optimized query that actually returns incorrect results.
Tableau uses 'SQLColAttribute' with 'SQL_DESC_NULLABLE' on the result set metadata for ODBC connections and the 'isNullable' method on the 'ResultSetMetaData' object for JDBC.
