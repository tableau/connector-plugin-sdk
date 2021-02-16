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

For all Tableau connector capabilities, please refer to capabilities [documentation](https://tableau.github.io/connector-plugin-sdk/docs/capabilities).
