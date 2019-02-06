---
title: Connector Design Considerations
---

The choices you make when creating a connector can include which superclass and dialect to use, and how you want to tune your connection using Tableau capabilities.

## Choosing a superclass

Connectors work using an inheritance pattern.
You can make a simple connector that reuses all of the PostgreSQL code by subclassing the ‘postgres’ class.
You can then customize some or all of the connector as needed, for example, by picking a different driver, renaming the connection, and changing the generated SQL.

The simplest connector  consists of just a manifest.xml file:

```
<connector-plugin class='example' superclass='postgres' plugin-version='0.0.0' name='Super PostgreSQL Connector' version='18.1'>
</connector-plugin>
```

This simple connector will inherit all behavior from the native Tableau PostgreSQL connector.

Tableau’s native connectors have special code and optimizations that may not be appropriate for your connection.
We recommend using the ‘odbc’ or ‘jdbc’ base classes for most connectors.
These handle connecting and retrieving data in a standard way and can be further customized as needed.
If your connection is very similar to an existing database such as PostgreSQL or MySQL, then choosing that as superclass might save considerable development time.

### Available superclass attributes

- odbc
- jdbc
- mysql_odbc

You might find other super class values in the workbook XML from an existing Tableau connection, but we don't recommend using them; they haven't been tested.

### Features based on superclass

Web Authoring (creating a new connection from the web) is not currently available for all connector superclasses. If your connector is based on 'odbc' or 'jdbc,' then you can publish your workbook or datasource from desktop to server, but you can't create a new connection directly on server. Connectors based on 'mysql_odbc' do support web authoring because this ability is inherited from the mysql code they are based on. 

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
- SybaseIQDialect
- Teradata1410Dialect
- TeradataDialect
- VerticaDialect

### Should I create a dialect definition file?
You don’t need a dialect definition file if your connector uses the same SQL dialect as the connector it’s based on, such as mysql_odbc. However, to make changes to an existing Tableau dialect or define a new dialect, you’ll need a new dialect definition file. For more information, see [Create a Tableau Dialect Definition (TDD) File]({{ site.baseurl }}/docs/dialect). 

## Setting connection capabilities

Tableau capabilities are Boolean settings you can use to tune many aspects of your connector behavior.
Capabilities can influence the types of queries that Tableau generates, how metadata is read, how Tableau binds to the drivers result set, and many other aspects.
Common capabilities and how they are used are described in [Capabilities]({{ site.baseurl }}/docs/capabilities).
