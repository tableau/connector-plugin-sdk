---
title: Metadata Enumeration
---

Connection metadata refers to the set of APIs Tableau uses to model Database/Schema/Table hierarchy, as well as table column details like name, type and constraints. When connecting to a data source Tableau needs to start by enumerating the hierarchy and related entities. When selecting a table, or connecting to an existing saved connection,  the column level info needs to be queried as well. 

## ODBC Metadata Enumeration
ODBC capabilities determine the method Tableau uses to read ODBC metadata.  Note that the scenarios below are in order and the scenario that returns results first is used, all others are skipped. The detailed logs of reading ODBC metadata are logged with `SQLODBCProtocol::ReadMetadataImpl` keyword.  You should be able to find those log lines in tabprotosrv log file with `Debug` level logging.

1. Full "select *" using SQLPrepare only, which ensures the query is parsed but not executed.
Conditions: CAP_ODBC_METADATA_SUPPRESS_PREPARED_QUERY = false AND CAP_ODBC_METADATA_SUPRESS_SELECT_STAR = false
Example query: `SELECT * FROM default.testv1_batters`

2. Row-limiting "select *" with WHERE 1=0.
Conditions: CAP_QUERY_WHERE_FALSE_METADATA = true AND (CAP_ODBC_METADATA_SUPPRESS_PREPARED_QUERY = false OR CAP_ODBC_METADATA_SUPPRESS_EXECUTED_QUERY = false)
Example query: `SELECT * FROM default.testv1_batters WHERE 1=0`

3. Row-limiting "select *" with TOP 0 / LIMIT 0.
Conditions: CAP_QUERY_TOP_0_METADATA = true AND (CAP_ODBC_METADATA_SUPPRESS_PREPARED_QUERY = false OR CAP_ODBC_METADATA_SUPPRESS_EXECUTED_QUERY = false)
Example query: `SELECT * FROM default.testv1_batters LIMIT 0`

4. Querying table metadata directly from [SQLColumns](https://docs.microsoft.com/en-us/sql/odbc/reference/syntax/sqlcolumns-function), which is fast, but can be less reliable.
Conditions: CAP_ODBC_METADATA_SUPPRESS_SQLCOLUMNS_API = false

5. Full "select *" query
Conditions: CAP_ODBC_METADATA_SUPPRESS_PREPARED_QUERY = false OR CAP_ODBC_METADATA_SUPPRESS_EXECUTED_QUERY = false
Example query: `SELECT * FROM default.testv1_batters`

## JDBC Metadata Enumeration
There are six JDBC capabilities controlling JDBC metadata enumeration, They are all prefixed with `CAP_JDBC_METADATA_`. When metadata is enumerated by a SQL query, it will be logged with keyword `grpc-protocol-read-query-metadata`. When reading the metadata of columns from a table, the event will be logged with keyword `grpc-protocol-read-table-metadata`.

Without any of below capabilities being set, our default behavior is to use JDBC APIs like getCatalogs, getSchemas, getTables, and getColumns from [DatabaseMetaData](https://docs.oracle.com/javase/7/docs/api/java/sql/DatabaseMetaData.html).

1. Set `CAP_JDBC_METADATA_SUPPRESS_PREPARED_QUERY` to true to disable SQLPrepare query, query will include a `WHERE 1=0` clause in order to read metadata.

2. Set `CAP_JDBC_METADATA_USE_RESULTSET_FOR_TABLE` to true to read metadata using an empty result set, example query as `select * from <tableName> where 1=0`. Turn this capability off to read the metadata of ResultSet for a particular table.

3. Set `CAP_JDBC_METADATA_READ_FOREIGNKEYS` to false to disable reading foreign key metadata.

4. Set `CAP_JDBC_METADATA_READ_PRIMARYKEYS` to false to disable reading primary key metadata.

5. Set `CAP_JDBC_METADATA_GET_INDEX_INFO` to false to disable reading index info.

For all Tableau connector capabilities, please refer to capabilities [documentation](https://tableau.github.io/connector-plugin-sdk/docs/capabilities).