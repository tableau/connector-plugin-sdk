---
title: Capabilities
---

Use Tableau capabilities to customize and tune your connector behavior. 

- [Metadata](#metadata)
- [Temporary Tables](#temporary-tables)
- [String Splits](#string-splits)
- [Initial SQL](#initial-sql)
- [Query](#query)
- [JDBC](#jdbc)
- [ODBC](#odbc)
- [Stored Procedures](#stored-procedures)
- [Isolation Level](#isolation-level)
- [Uncommon](#uncommon)

**Read the table**

Entry | Description 
-|- 
&ndash; | There is no default or recommended value for this capability. If you use this capability, you need to verify that the value you use is correct for your database.
? | You need to verify that the value you use is correct for your database.
**<span style="color:red">Red</span>** | The recommended value is different than the default value.

## Metadata

Capability | Description | Default | Recommended 
-|-|-|-
CAP_FAST_METADATA | Set to 'yes' if you have small to moderate size schemas. This capability controls whether Tableau should enumerate all of the objects immediately when you connect. Set the value to “yes” to enable this capability for better performance when creating connections. Disable this capability to allow search for specific schemas or tables instead of retrieving all objects. You can search for all objects by using an empty string. | yes | yes 
CAP_QUERY_TOP_0_METADATA | Set to 'yes' if the data source can handle a "TOP 0" request for retrieving metadata | no | **<span style="color:red">?</span>**    
CAP_QUERY_WHERE_FALSE_METADATA | Set to 'yes' if the data source can handle a "WHERE \<false\>" predicate for retrieving metadata | &ndash; | **<span style="color:red">?</span>** 

## Temporary Tables

Capability | Description | Default | Recommended
-|-|-|-
CAP_CREATE_TEMP_TABLES | Set to 'yes' if Tableau can create temporary tables needed for certain complex or optimized queries. Set to 'no' if creating temporary tables is not supported. See also: CAP_SELECT_INTO. | &ndash; | **<span style="color:red">?</span>**  
CAP_INDEX_TEMP_TABLES | Set to 'yes' if data source supports creation of indexes on temp tables database | &ndash; | &ndash; 
CAP_QUERY_USE_TEMP_TABLE_NAMES_AS_SUBQUERY_ALIASES | Set to 'yes' if Tableau must use generated temporary table names for aliases of subqueries because they might end up implemented as temporary tables | no | no
CAP_SELECT_INTO | Set to 'yes' if Tableau can create a table on the fly from the resultset of another query. See also: CAP_CREATE_TEMP_TABLES. | &ndash; | **<span style="color:red">?</span>**   
CAP_SELECT_TOP_INTO | Set to 'yes' if Tableau can use a TOP or LIMIT row-limiting clause when creating a table from a query resultset. | &ndash; | **<span style="color:red">?</span>**   
CAP_ODBC_METADATA_FORCE_UTF8_TEMP_TABLE_COLUMN_SIZE | Set to 'yes' if when creating temp tables specify the size of varchar columns in bytes. | &ndash; | &ndash;
CAP_TEMP_TABLES_NOT_SESSION_SCOPED | Set to 'yes' if this data source uses regular tables to simulate temp tables. Temporary table creation is still controlled by CAP_CREATE_TEMP_TABLE or CAP_SELECT_INTO | &ndash; | &ndash; 
CAP_SUPPRESS_TEMP_TABLE_CHECKS | Set to 'yes' to skip the connection time check that determines if the user has permission to create temp tables. | no | no 

## String Splits 

Capability | Description | Default | Recommended 
-|-|-|-
CAP_SUPPORTS_SPLIT_FROM_LEFT | Set to 'yes' if data source supports splitting a string from the left | &ndash; | **<span style="color:red">yes</span>**  
CAP_SUPPORTS_SPLIT_FROM_RIGHT | Set to 'yes' if data source supports splitting a string from the right | &ndash; | **<span style="color:red">?</span>**  

## Initial SQL 

Capability | Description | Default | Recommended 
-|-|-|-
CAP_SUPPORTS_INITIAL_SQL | Set to 'yes' to enable Initial SQL on the connection dialog. Available in Tableau 2020.3 and newer. | &ndash; | **<span style="color:red">yes</span>**

## Query

Capability | Description | Default | Recommended
-|-|-|-
CAP_QUERY_AGG_NO_BOOLEXPR | Set to 'yes' to transform boolean expressions to integers for arguments to aggregates. Available in Tableau 2020.2 and newer. | &ndash; | &ndash;
CAP_QUERY_ALLOW_JOIN_REORDER | Set to 'yes' to use query optimization to reduce database work with some inner and equality joins. | yes | yes 
CAP_QUERY_ALLOW_PARTIAL_AGGREGATION | Tableau can minimize data movement (and boost performance) in federated join scenarios by performing as much aggregation as possible in remote databases before shipping the data back. This can introduce additional groupbys on the fields used in the join condition. If the join is on a string field, not all data sources handle the additional groupbys on strings efficiently, leading to a rapid degradation in performance the more join key fields are used. | yes | yes 
CAP_QUERY_BOOL_IDENTIFIER_TO_LOGICAL | Set to 'yes' if the dialect can handle WHEN [bit column] THEN or does it need something like WHEN [column] = 1 THEN. | &ndash; | &ndash; 
CAP_QUERY_BOOLEXPR_TO_INTEXPR | Set to 'yes' if data source does not support booleans natively in a result set. Set to 'no' if booleans are supported natively. | &ndash; | **<span style="color:red">?</span>**   
CAP_QUERY_CASE_MATCHES_NULL | Set to 'yes' if CASE can match a null in a valued CASE expression | no | no 
CAP_QUERY_CASE_OUT_NO_BOOL_OPS | Set to 'yes' if CASE outputs cannot contain boolean operators like AND/OR/NOT. Available in Tableau 2020.2 and newer. | &ndash; | &ndash;
CAP_QUERY_CASE_PROMOTES_CHAR | Set to 'no' if CASE cannot promote character types? | yes | yes 
CAP_QUERY_CAST_MONEY_AS_NUMERIC | Set to 'yes' to cast money as numeric. Available in Tableau 2021.1 and newer. | &ndash; | &ndash;
CAP_QUERY_FROM_REQUIRES_ALIAS | Set to 'yes' if the FROM clause must provide an alias for the given table. | &ndash; | &ndash;
CAP_QUERY_GROUP_ALLOW_DUPLICATES | Set to 'no' if SQL queries cannot contain duplicate expressions in the GROUP BY clause (this is uncommon). | yes | yes
CAP_QUERY_GROUP_BY_ALIAS | Set to 'yes' if SQL queries with aggregations can reference the grouping columns by their corresponding alias in the SELECT list, for example, GROUP BY "none_ShipCountry_nk". | no | no 
CAP_QUERY_GROUP_BY_BOOL | Set to 'yes' if the database can group by a raw boolean. Set to 'no' if booleans should be cast to an INT. Can also influence booleans in the SELECT clause. | no | **<span style="color:red">yes</span>** 
CAP_QUERY_GROUP_BY_DEGREE | Set to 'yes' if SQL queries with aggregations can reference the grouping columns by the ordinal position of each column, for example, GROUP BY 2, 5. See also: CAP_QUERY_SORT_BY_DEGREE | no | **<span style="color:red">yes</span>**  
CAP_QUERY_HAVING_REQUIRES_GROUP_BY | Set to 'yes' if Tableau must use an artificial grouping field for any query that has a HAVING clause but no grouping columns. | &ndash; | **<span style="color:red">?</span>** 
CAP_QUERY_HAVING_UNSUPPORTED | Set to 'yes' if the SQL syntax for HAVING is unsupported. Sometimes Tableau can work around this using subqueries. See also: CAP_QUERY_SUBQUERIES. | &ndash; | &ndash; 
CAP_QUERY_INCLUDE_GROUP_BY_COLUMNS_IN_SELECT | Set to 'yes' to require all GROUP BY expressions to also appear in the SELECT expression list. | &ndash; | &ndash; 
CAP_QUERY_INCLUDE_HAVING_COLUMNS_IN_SELECT | Set to 'yes' if the HAVING columns are always needed in the SELECT clause | &ndash; | &ndash; 
CAP_QUERY_INITIAL_SQL_SPLIT_STATEMENTS | Set to 'yes' if the data source requires multiple statements issued as separate queries for Initial SQL | &ndash; | **<span style="color:red">?</span>**  
CAP_QUERY_INOUT_JOINS | Set to 'no' if the connection cannot handle the joins needed for IN/OUT set calculations | yes | yes 
CAP_QUERY_JOIN_ACROSS_SCHEMAS | Set to 'yes' if SQL queries can express joins between tables located in different schemas. | no | **<span style="color:red">?</span>** 
CAP_QUERY_JOIN_MISMATCHED_VARCHAR_WIDTHS | Set to 'yes' if join predicates have different widths for VARCHAR columns | yes | **<span style="color:red">?</span>**
CAP_QUERY_JOIN_PREDICATE_REQUIRES_SCOPE | Set to 'yes' if join predicates must be enclosed in parens | yes | yes
CAP_QUERY_JOIN_PUSH_DOWN_CONDITION_EXPRESSIONS | Set to 'yes' if the data source cannot handle complex expressions in join conditions (anything more complex than an identifier): JOIN ON [id]=[id] vs JOIN ON UPPER([State])=[State] | &ndash; | &ndash;
CAP_QUERY_JOIN_REQUIRES_SCOPE | Set to 'yes' if SQL queries must scope each join clause within parentheses to ensure a proper order of evaluation. | &ndash; | &ndash; 
CAP_QUERY_JOIN_REQUIRES_SUBQUERY | Set to ‘yes’ to force join expressions involving more than two tables to be composed with subqueries. | &ndash; | &ndash; 
CAP_QUERY_NAKED_JOINS | Set to 'yes' if Tableau needs to wrap the base relation to join filters | yes | yes
CAP_QUERY_OUTER_JOIN_CONDITION_NO_TRIVIAL | Set to 'yes' to rewrite empty outer join conditions to non-trivial conditions. Available in Tableau 2020.1 and newer. | &ndash; | &ndash;
CAP_QUERY_SCALAR_SELECTS_ALL_IN_GROUP_BYS | Set to 'yes' if all scalar selects must be in an aggregated query's GROUP BY clause | &ndash; | &ndash;
CAP_QUERY_SCALAR_SELECTS_SOME_IN_GROUP_BYS | Set to 'yes' if some scalar selects must be in an aggregated query's GROUP BY clause. Available in Tableau 2020.2 and newer. | &ndash; | &ndash;
CAP_QUERY_SELECT_ALIASES_SORTED | Set to 'yes' if Tableau must impose a deterministic order on the SELECT expressions (sorted by alias) to ensure that query results can be properly matched with each field in the Tableau visualization. This is only required for data sources that do not preserve the aliases of the SELECT expressions when returning metadata with the query results. | no | no  
CAP_QUERY_SORT_BY | Set to 'yes' to enable the 'Field' option in the Sort menu | no | **<span style="color:red">yes</span>**  
CAP_QUERY_SORT_BY_DEGREE | Set to 'yes' if SQL queries can reference the sorting columns by the ordinal position of each column, for example, ORDER BY 2, 5. See also: CAP_QUERY_GROUP_BY_DEGREE. | yes | **<span style="color:red">?</span>** 
CAP_QUERY_SORT_BY_NON_NUMERIC | Set to 'no' if data source cannot sort by non-numeric values | yes | yes 
CAP_QUERY_SUBQUERIES | Set to 'yes' if the data source supports subqueries. | &ndash; | **<span style="color:red">yes</span>** 
CAP_QUERY_SUBQUERIES_WITH_TOP | Set to 'yes' if the data source supports a TOP or LIMIT row-limiting clause within a subquery. | yes | **<span style="color:red">?</span>**  
CAP_QUERY_SUBQUERY_QUERY_CONTEXT | Set to 'yes' to force Tableau to use a subquery for context filters instead of a temporary table or locally cached results. | yes | yes 
CAP_QUERY_SUPPORT_EMPTY_GROUPBY | Set to 'yes' if data source supports empty group by clause | &ndash; | &ndash; 
CAP_QUERY_SUPPORTS_UNIQUE_IDENTIFIER | Set to 'yes' if data source supports uniqueidentifier data type. Available in Tableau 2020.1 and newer. | &ndash; | &ndash;
CAP_QUERY_TIME_REQUIRES_CAST | Set to 'yes' if the time columns must be cast to timestamp/datetime. This capability applies to ODBC connectors. | &ndash; | &ndash; 
CAP_QUERY_TOP_0 | Set to 'no' if the server cannot handle a "TOP 0" request | yes | yes
CAP_QUERY_TOP_N | Set to 'yes' if the data source supports any form of row-limiting clause. The exact forms supported are described below. | no | **<span style="color:red">yes</span>** 
CAP_QUERY_TOP_PERCENT | Set to 'yes' if TOP supports percent | no | **<span style="color:red">?</span>** 
CAP_QUERY_TOP_SAMPLE | Set to 'yes' if TOP supports sampling rows | no | **<span style="color:red">?</span>**  
CAP_QUERY_TOP_SAMPLE_FAST | Set to 'yes' if TOP with sampling is faster than TOP | no | no 
CAP_QUERY_TOP_SAMPLE_PERCENT | Set to 'yes' if TOP supports sampling by percentages | no | **<span style="color:red">?</span>**  
CAP_QUERY_USE_DOMAIN_RANGES_OPTIMIZATION | Set to 'no' if domain ranges cannot be used to optimize set functions. | yes | yes
CAP_QUERY_USE_QUERY_FUSION | Set to ‘no’ to prevent Tableau from combining multiple individual queries into a single combined query. Turn off this capability for performance tuning or if the database is unable to process large queries.  | yes | yes 
CAP_QUERY_WRAP_SUBQUERY_WITH_TOP | Set to 'yes' if the server can handle a subquery wrapped with only a TOP clause | no | no 


## JDBC 

Capability | Description | Default | Recommended 
-|-|-|-
CAP_JDBC_BIND_BIGDECIMAL_STRING | Set to 'yes' to bind bigdecimal as string for JDBC. Available in Tableau 2020.1 and newer. | &ndash; | &ndash; 
CAP_JDBC_BIND_DETECT_ALIAS_CASE_FOLDING | Set to 'yes' to allow Tableau to detect and recover from a JDBC data source that reports the field names in a result set using only upper-case or lower-case characters, instead of the expected field names.  | &ndash;  | &ndash; 
CAP_JDBC_BIND_SPATIAL_AS_WKB | Set to 'yes' to use WKB for spatial types serialization. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;
CAP_JDBC_CONVERT_WKB_HEX_STRING | Set to 'yes' to convert a hex string to regular WKB. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;
CAP_JDBC_EXPORT_BIND_BOOL_AS_INTEGER  | Set to 'yes' to bind Tableau booleans to integer for data insertion. Available in Tableau 2020.2 and newer. | &ndash; | &ndash; 
CAP_JDBC_EXPORT_DATA_BATCH | Set to 'no' to disable the use of JDBC batch operations for data insert. | yes | yes 
CAP_JDBC_INSERT_COERCE_INT_TO_BOOL | Set to 'yes' to convert integer type to boolean only when the column type and source type are different. Available in Tableau 2021.2 and newer. | &ndash; | &ndash;
CAP_JDBC_MAX_STRING_LENGTH_MEDIUM | Set to 'yes' to use 512 character string length limit. Default is 16K. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;
CAP_JDBC_METADATA_GET_INDEX_INFO | Set to 'no' to disable reading index info | yes | yes  
CAP_JDBC_METADATA_IGNORE_NULLABILITY | Set to 'yes' to ignore column nullability retrieved from query metadata and always set it to true for all columns in the query result. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;
CAP_JDBC_METADATA_NUMERIC_DEFAULT_PREC_SCALE_DOUBLE | Set to 'yes' to use precision=17 and no scale for numeric with undefined precision/scale. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;
CAP_JDBC_METADATA_READ_FOREIGNKEYS | Set to 'no' to disable reading foreign key metadata | yes | yes   
CAP_JDBC_METADATA_READ_PRIMARYKEYS | Set to 'no' to disable reading primary key metadata | yes | yes 
CAP_JDBC_METADATA_USE_RESULTSET_FOR_TABLE | Set to 'yes' to get column metadata from the result set of a select * query. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;
CAP_JDBC_METADATA_SUPPRESS_PREPARED_QUERY | If CAP_JDBC_METADATA_USE_RESULTSET_FOR_TABLE is enabled, set this capability to 'yes' to disable preparing the query used for reading the table metadata. We will execute the query wrapped with a where-false clause. | &ndash; | &ndash;
CAP_JDBC_PARAMETER_METADATA_REQUIRES_EXECUTE | Set to 'yes' if retrieving parameter metadata for inserts requires execution of an empty batch. Available in Tableau 2020.2 and newer. | &ndash; | &ndash; 
CAP_JDBC_QUERY_ASYNC | Set to 'yes' to run queries on another thread. | &ndash; | **<span style="color:red">yes</span>**
CAP_JDBC_QUERY_CANCEL | Set to 'yes' if driver can cancel queries. Requires CAP_JDBC_QUERY_ASYNC to be set. | yes | yes
CAP_JDBC_QUERY_DISABLE_AUTO_COMMIT | Set to 'yes' to disable the default auto-commit mode when running query. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;
CAP_JDBC_QUERY_FORCE_PREPARE | Set to 'yes' to always prepare the query before execution. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;
CAP_JDBC_SUPPRESS_EMPTY_CATALOG_NAME | Set to 'yes' to ignore missing catalog. | &ndash; | &ndash;
CAP_JDBC_SUPPRESS_ENUMERATE_DATABASES | Set to 'yes' to disable database enumeration. | &ndash; | &ndash; 
CAP_JDBC_SUPPRESS_ENUMERATE_SCHEMAS | Set to 'yes' to disable schema enumeration. | &ndash; | &ndash; 
CAP_JDBC_SUPPRESS_ENUMERATE_TABLES | Set to 'yes' to disable table enumeration. | &ndash; | &ndash; 
CAP_JDBC_SET_CLIENT_INFO | Enable the JDBC setClientInfo API to pass trace information to the database. Available in Tableau 2021.2 and newer for on-premises Tableau Server. Needs additional configuration see documentation. | &ndash; | &ndash;
CAP_JDBC_TRIM_STRING_PADDING | Set to 'yes' to trim trailing whitespace from string columns that have been added by the driver. Available in Tableau 2020.1 and newer. | &ndash; | &ndash; 
CAP_JDBC_USE_ADAPTIVE_FETCH_SIZE | Set to 'yes' to use ResultSet metadata to determine optimal fetch size. May require CAP_JDBC_QUERY_FORCE_PREPARE to be enabled to work properly. Available in Tableau 2020.4 and newer. | yes | &ndash;
CAP_JDBC_USE_SINGLE_ROW_FETCH | Set to 'yes' to use single row fetch. May require CAP_JDBC_QUERY_FORCE_PREPARE. Available in Tableau 2020.4 and newer. | &ndash; | &ndash;

## ODBC 

Capability | Description | Default | Recommended 
-|-|-|-
CAP_ODBC_BIND_BOOL_AS_WCHAR_01LITERAL | Set to 'yes' to bind a Boolean data type as a WCHAR containing values '0' or '1'. | &ndash; | &ndash; 
CAP_ODBC_BIND_BOOL_AS_WCHAR_TFLITERAL | Set to 'yes' to bind a Boolean data type as WCHAR containing values 't' or 'f'. | &ndash; | &ndash; 
CAP_ODBC_BIND_DETECT_ALIAS_CASE_FOLDING | Set to 'yes' to allow Tableau to detect and recover from an ODBC data source that reports the field names in a result set using only upper-case or lower-case characters, instead of the expected field names. | &ndash; | &ndash; 
CAP_ODBC_BIND_FORCE_DATE_AS_CHAR | Set to 'yes' to force the Tableau native ODBC protocol to bind date values as CHAR. | &ndash; | &ndash; 
CAP_ODBC_BIND_FORCE_DATETIME_AS_CHAR | Set to 'yes' to force the Tableau native ODBC protocol to bind datetime values as CHAR. | &ndash; | &ndash; 
CAP_ODBC_BIND_FORCE_MAX_STRING_BUFFERS | Set to 'yes' to force the Tableau native ODBC protocol to use maximum-sized buffers (1 MB) for strings instead of the size described by metadata. | &ndash; | &ndash; 
CAP_ODBC_BIND_FORCE_MEDIUM_STRING_BUFFERS | Set to 'yes' to force the Tableau native ODBC protocol to use medium-sized buffers (1 K) for strings instead of the size described by metadata. | &ndash; | &ndash; 
CAP_ODBC_BIND_FORCE_SIGNED | Set to 'yes' to force binding integers as signed. | &ndash; | &ndash; 
CAP_ODBC_BIND_FORCE_SMALL_STRING_BUFFERS | Set to 'yes' to force the Tableau native ODBC protocol to use small buffers for strings instead of the size described by metadata. | &ndash; | &ndash; 
CAP_ODBC_BIND_PRESERVE_BOM | Set to 'yes' to preserve BOM when present in strings. Hive will return BOM and treat strings containing it as distinct entities. | &ndash; | &ndash; 
CAP_ODBC_BIND_SKIP_LOCAL_DATATYPE_UNKNOWN | Set to 'yes' to prevent the native ODBC Protocol from binding to columns having local data type DataType::Unknown in the expected metadata | &ndash; | &ndash;
CAP_ODBC_BIND_SPATIAL_AS_WKT | Set to 'yes' to force binding Spatial data as WKT (Well Known Text) | &ndash; | &ndash; 
CAP_ODBC_BIND_SUPPRESS_COERCE_TO_STRING | Set to 'yes' to prevent the Tableau native ODBC protocol from binding non-string data as strings (that is, requesting driver conversion). | &ndash; | &ndash; 
CAP_ODBC_BIND_SUPPRESS_INT64 | Set to 'yes' to prevent the Tableau native ODBC protocol from using 64-bit integers for large numeric data. | &ndash; | &ndash; 
CAP_ODBC_BIND_SUPPRESS_PREFERRED_CHAR | Set to 'yes' to prevent the Tableau native ODBC protocol from preferring a character type that differs from the driver default. | &ndash; | &ndash; 
CAP_ODBC_BIND_SUPPRESS_PREFERRED_TYPES | Set to 'yes' to prevent the Tableau native ODBC protocol from binding any data according to its preferred wire types. With this capability set, Tableau will only bind according to the data types described by the ODBC driver via metadata. | &ndash; | &ndash; 
CAP_ODBC_BIND_SUPPRESS_WIDE_CHAR | Set to 'yes' to prevent the Tableau native ODBC protocol from binding strings a WCHAR. Instead they will be bound as single-byte CHAR arrays, and processed locally for any UTF-8 characters contained within. | &ndash; | &ndash; 
CAP_ODBC_CONNECTION_STATE_VERIFY_FAST | Set to ‘yes’ to check if a connection is broken with a fast ODBC API call. | yes | yes 
CAP_ODBC_CONNECTION_STATE_VERIFY_PROBE | Set to ‘yes’ to check if a connection is broken with a forced probe. | no | no 
CAP_ODBC_CONNECTION_STATE_VERIFY_PROBE_IF_STALE | Set to ‘yes’ to check if a connection is broken with a forced probe only if it is "stale" (that is, unused for about 30 minutes). | yes | yes 
CAP_ODBC_CONNECTION_STATE_VERIFY_PROBE_PREPARED_QUERY | Set to ‘yes’ to check if a connection is broken using a prepared query. | yes | yes 
CAP_ODBC_CURSOR_DYNAMIC | Set to 'yes' to force the Tableau native ODBC protocol to set the cursor type for all statements to Dynamic (scrollable, detects added/removed/modified rows). | &ndash; | &ndash; 
CAP_ODBC_CURSOR_FORWARD_ONLY | Set to 'yes' to force the Tableau native ODBC protocol to set the cursor type for all statements to Forward-only (non-scrollable). | &ndash; | **<span style="color:red">?</span>** 
CAP_ODBC_CURSOR_KEYSET_DRIVEN | Set to 'yes' to force the Tableau native ODBC protocol to set the cursor type for all statements to Keyset-driven (scrollable, detects changes to values within a row). | &ndash; | &ndash; 
CAP_ODBC_CURSOR_STATIC | Set to 'yes' to force Tableau to set the cursor type for all statements to Static (scrollable, does not detect changes). | &ndash; | &ndash; 
CAP_ODBC_ENABLE_AUTO_IPD | Set to 'yes' to enable automatic population of the IPD if supported by driver. Available in Tableau 2020.3 and newer. | &ndash; | &ndash;
CAP_ODBC_ERROR_IGNORE_FALSE_ALARM | Set to 'yes' to allow the Tableau native ODBC protocol to ignore SQL_ERROR conditions where SQLSTATE is '00000' (meaning "no error"). | &ndash; | &ndash; 
CAP_ODBC_ERROR_IGNORE_SQLNODATA_FOR_COMMAND_QUERIES | Set to 'yes' to ignore when SQLExecDirect returns SQL_NO_DATA even when data is not expected back | &ndash; | &ndash; 
CAP_ODBC_EXPORT_ALLOW_CHAR_UTF8 | Set to 'yes' to allow the use of single-byte char data type for binding Unicode strings as UTF-8. | no | no 
CAP_ODBC_EXPORT_BIND_FORCE_TARGET_METADATA | Set to 'yes' to force binding for export based on all of the metadata from the target table instead of the ODBC metadata for the parameterized insert statement. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_BIND_PREFER_TARGET_METADATA | Set to 'yes' to prefer binding for export based on specific types of metadata from the target table instead of the ODBC metadata for the parameterized insert statement. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_BUFFERS_RESIZABLE | Set to 'yes' to allow export buffers to be reallocated after the first batch to improve performance. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_BUFFERS_SIZE_FIXED | Set to 'yes' to ignore the width of a single row when computing the total rows to insert at a time. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_BUFFERS_SIZE_LIMIT_512KB | Set to 'yes' to limit export buffers to 512 KB. This is an uncommon setting. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_BUFFERS_SIZE_MASSIVE | Set to 'yes' to force the use of large buffers for insert. If CAP_ODBC_EXPORT_BUFFERS_RESIZABLE is not set or disabled, a fixed row count is used. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_BUFFERS_SIZE_MEDIUM | Set to 'yes' to force the use of medium-sized buffers for insert. If CAP_ODBC_EXPORT_BUFFERS_RESIZABLE is not set or disabled, a fixed row count is used. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_BUFFERS_SIZE_SMALL | Set to 'yes' to force the use of small buffers for insert. If CAP_ODBC_EXPORT_BUFFERS_RESIZABLE is not set or disabled, a fixed row count is used. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_CONTINUE_ON_ERROR | Set to 'yes' to continue data insert despite errors. Some data sources report warnings as errors. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_DATA_BULK | Set to 'yes' to allow the use of ODBC bulk operations for data insert. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_DATA_BULK_VIA_INSERT | Set to 'yes' to allow the use of ODBC bulk operations based on 'INSERT INTO' parameterized queries. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_DATA_BULK_VIA_ROWSET | Set to 'yes' to allow the use of ODBC bulk operations based on a rowset cursor. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_FORCE_INDICATE_NTS | Set to 'yes' to force the use of indicator buffers for identifying null-terminated strings (NTS). | &ndash; | &ndash; 
CAP_ODBC_EXPORT_FORCE_SINGLE_ROW_BINDING | Set to 'yes' to force the use of a single row for binding export buffers to insert data. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_FORCE_SINGLE_ROW_BINDING_WITH_TIMESTAMPS | Set to 'yes' to force the use of a single row for binding export buffers when dealing with timestamp data. This is required for some versions of Teradata. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_FORCE_STRING_WIDTH_FROM_SOURCE | Set to 'yes' to force the use of the source string width (from Tableau metadata), overriding the destination string width (from insert parameter metadata). | &ndash; | &ndash; 
CAP_ODBC_EXPORT_FORCE_STRING_WIDTH_USING_OCTET_LENGTH | Set to 'yes' to force the use of the source string width from the octet length. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_SUPPRESS_STRING_WIDTH_VALIDATION | Set to 'yes' to suppress validating that the target string width can accommodate the widest source strings. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_BATCH_MASSIVE | Set to ‘yes’ to commit in massive batches of INSERT statements (~100,000). This may be useful with single-row export binding. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_BATCH_MEDIUM | Set to 'yes' to commit in medium-sized batches of INSERT statements (~50). A single statement may be bound to multiple records. | yes | yes 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_BATCH_SMALL | Set to 'yes' to commit in small batches of INSERT statements (~5). A single statement may be bound to multiple records. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_BYTES_MASSIVE | Set to 'yes' to commit in massive batches of data (~100 MB). | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_BYTES_MEDIUM | Set to 'yes' to commit in medium batches of data (~10 MB). | yes | yes 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_BYTES_SMALL | Set to 'yes' to commit in small batches of data (~1 MB). | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_EACH_STATEMENT | Set to 'yes' to commit after executing each INSERT statement. A single statement may be bound to multiple records. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_INTERVAL_LONG | Set to 'yes' to commit in long intervals of elapsed time (~100 seconds). | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_INTERVAL_MEDIUM | Set to 'yes' to commit in medium intervals of elapsed time (~10 seconds). | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_INTERVAL_SHORT | Set to 'yes' to commit in short intervals of elapsed time (~1 seconds). | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSACTIONS_COMMIT_ONCE_WHEN_COMPLETE | Set to 'yes' to commit only once at the end after the export is complete. | &ndash; | &ndash; 
CAP_ODBC_EXPORT_TRANSLATE_DATA_PARALLEL | Set to 'yes' to use parallel loops to translate Tableau DataValues to wire buffers on export. | yes | yes 
CAP_ODBC_FETCH_ABORT_FORCE_CANCEL_STATEMENT | Set to 'yes' to cancel the statement handle upon interrupting SQLFetch with a cancel exception. | &ndash; | &ndash; 
CAP_ODBC_FETCH_BUFFERS_RESIZABLE | Set to 'yes' to allow buffers to be reallocated after fetch to improve performance or handle data truncation. | &ndash; | &ndash; 
CAP_ODBC_FETCH_BUFFERS_SIZE_FIXED | Set to 'yes' to ignore the width of a single row when computing the total rows to fetch. | &ndash; | &ndash; 
CAP_ODBC_FETCH_BUFFERS_SIZE_MASSIVE | Set to 'yes' to force the use of large buffers. If CAP_ODBC_FETCH_BUFFERS_SIZE_FIXED is enabled, a fixed row count is used. | &ndash; | &ndash; 
CAP_ODBC_FETCH_BUFFERS_SIZE_MEDIUM | Set to 'yes' to force the use of medium-sized buffers. If CAP_ODBC_FETCH_BUFFERS_SIZE_FIXED is enabled, a fixed row count is used. | &ndash; | &ndash; 
CAP_ODBC_FETCH_BUFFERS_SIZE_SMALL | Set to 'yes' to force the use of small buffers. If CAP_ODBC_FETCH_BUFFERS_SIZE_FIXED is enabled, a fixed row count is used. | &ndash; | &ndash; 
CAP_ODBC_FETCH_CONTINUE_ON_ERROR | Set to 'yes' to allow the Tableau native ODBC protocol to continue resultset fetch despite errors (some data sources report warnings as errors). | &ndash; | &ndash; 
CAP_ODBC_FETCH_IGNORE_FRACTIONAL_SECONDS | Set to 'yes' to allow the Tableau native ODBC protocol to ignore the fractional seconds component of a time value when fetching query result set data. This is useful when working with data sources that do not follow the ODBC specification for fractional seconds, which must be represented as billionths of a second. | &ndash; | &ndash; 
CAP_ODBC_FETCH_RESIZE_BUFFERS | Set to 'yes' to allow the Tableau native ODBC protocol to automatically resize buffers and fetch again if data truncation occurred. | &ndash; | &ndash; 
CAP_ODBC_FORCE_SINGLE_ROW_BINDING | Set to 'yes' to force the Tableau native ODBC protocol to use a single row for result set transfers instead of the more efficient bulk-fetch. | &ndash; | &ndash; 
CAP_ODBC_IMPORT_ERASE_BUFFERS | Set to 'yes' to reset the contents of data buffers before fetching each block. | &ndash; | &ndash; 
CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL | Set to 'no' to disable decoding data locally in parallel. | yes | yes 
CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL_SMALL | Set to 'yes' to use a small degree of parallelism when using CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL. Available in Tableau 2020.4 and newer. | &ndash; | &ndash; 
CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL_MEDIUM | Set to 'yes' to use a medium degree of parallelism when using CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL. Available in Tableau 2020.4 and newer. | &ndash; | &ndash; 
CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL_LARGE | Set to 'yes' to use a large degree of parallelism when using CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL. Available in Tableau 2020.4 and newer. | &ndash; | &ndash; 
CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL_XL | Set to 'yes' to use an extra-large degree of parallelism when using CAP_ODBC_IMPORT_TRANSLATE_DATA_PARALLEL. Available in Tableau 2020.4 and newer. | &ndash; | &ndash; 
CAP_ODBC_METADATA_FORCE_LENGTH_AS_PRECISION | Set to 'yes' to force the Tableau native ODBC protocol to use the column "length" as the numeric precision. This is an uncommon setting. | &ndash; | &ndash; 
CAP_ODBC_METADATA_FORCE_NUM_PREC_RADIX_10 | Set to 'yes' to force the Tableau native ODBC protocol to assume the numeric precision is reported in base-10 digits. This is an uncommon setting. | &ndash; | &ndash; 
CAP_ODBC_METADATA_FORCE_UNKNOWN_AS_STRING | Set to 'yes' to force the Native ODBC Protocol to treat unknown data types as string instead of ignoring the associated column. | &ndash; | &ndash; 
CAP_ODBC_METADATA_FORCE_UTF8_IDENTIFIERS | Set to 'yes' to force the protocol to treat identifiers as UTF-8 when communicating with the driver. | &ndash; | &ndash; 
CAP_ODBC_METADATA_SKIP_DESC_TYPE_NAME | Set to 'yes' to remove the check for the SQL_DESC_TYPE_NAME attribute with the SQLColAttribute API. | &ndash; | &ndash; 
CAP_ODBC_METADATA_STRING_LENGTH_UNKNOWN | Set to 'yes' to prevent Tableau from allocating memory based on the driver-reported string length, which may not be known or reported properly. Instead, Tableau will use a fixed-sized string length, and will reallocate as needed to handle string data that is too large for the fixed-size buffer. | &ndash; | &ndash; 
CAP_ODBC_METADATA_STRING_TRUST_OCTET_LENGTH | Set to 'yes' to use the octet length reported by the driver for strings instead of computing it from the number of characters. | &ndash; | &ndash; 
CAP_ODBC_METADATA_SUPPRESS_EXECUTED_QUERY | Set to 'yes' to prevent Tableau from executing a query as a means of reading metadata. While Tableau typically includes a row-limiting clause in such metadata queries (for example, 'LIMIT', or 'WHERE 1=0'), this may not help when used with a Custom SQL connection for database systems with poor query optimizers. Note that this capability may prevent Tableau from determining the connection metadata properly. | &ndash; | &ndash; 
CAP_ODBC_METADATA_SUPPRESS_PREPARED_QUERY | Set to 'yes' to prevent Tableau from using a prepared query as a means of reading metadata. A prepared query is often the fastest way to accurately read metadata. However, not all database systems are capable of reporting metadata for a prepared query without actually executing the query. Note that certain metadata -- for example from connections using Custom SQL -- cannot be retrieved if this capability and CAP_ODBC_METADATA_SUPPRESS_EXECUTED_QUERY are both set. | &ndash; | &ndash; 
CAP_ODBC_METADATA_SUPPRESS_READ_IDENTITY_COLUMNS | Set to 'no' to prevent reading identity column metadata | yes | yes 
CAP_ODBC_METADATA_SUPPRESS_SELECT_STAR | Set to 'yes' to prevent reading metadata using a 'select *' query. | &ndash; | &ndash; 
CAP_ODBC_METADATA_SUPPRESS_SQLCOLUMNS_API | Set to 'yes' to prevent Tableau from using older, less accurate API for reading metadata from ODBC data sources. Setting this capability allows Tableau to read metadata by issuing a full 'select *' query, which is expensive but may enable connectivity for extremely limited or unstable data sources. | &ndash; | &ndash; 
CAP_ODBC_METADATA_SUPPRESS_SQLFOREIGNKEYS_API | Set to 'yes' to prevent Tableau from attempting to read metadata describing foreign key constraints. Despite the simple nature of this ODBC API, some drivers may have unstable behavior or produce inaccurate results. Setting this capability may force Tableau to generate less efficient queries involving multi-table joins. | &ndash; | &ndash; 
CAP_ODBC_METADATA_SUPPRESS_SQLPRIMARYKEYS_API | Set to 'yes' to prevent Tableau from reading primary key metadata using the SQLPrimaryKeys API or an equivalent query. | &ndash; | &ndash; 
CAP_ODBC_METADATA_SUPPRESS_SQLSTATISTICS_API | Set to 'yes' to prevent reading unique constraints and table cardinality estimates using the SQLStatistics API or an equivalent query. | yes | yes 
CAP_ODBC_REBIND_SKIP_UNBIND | Set to 'yes' to force the Tableau native ODBC protocol to rebind a column directly and skip unbinding, which reduces ODBC API calls when resizing buffers to refetch truncated data. | &ndash; | &ndash; 
CAP_ODBC_SUPPORTS_LONG_DATA_BULK | Set to 'yes' if driver can fetch multiple long-data rows at a time. | no | no |
CAP_ODBC_SUPPORTS_LONG_DATA_ORDERED | Set to 'yes' if driver requires long-data columns to come after non-long-data ones | no | no | 
CAP_ODBC_SUPPRESS_CATALOG_NAME | Set 'yes' to suppress passing catalog name for SQLTables, SQLPrimaryKeys, SQLForeignKeys, SQLStatistics calls | &ndash; | &ndash;
CAP_ODBC_SUPPRESS_ENUMERATE_SCHEMA_WITHOUT_CATALOG | Set 'yes' to suppress enumerating schemas without a valid catalog. | &ndash; | &ndash;
CAP_ODBC_SUPPRESS_INFO_SCHEMA_TABLES | Set to 'yes' to prevent tables from "information_schema" schema from being returned by EnumerateTables | &ndash; | &ndash; 
CAP_ODBC_SUPPRESS_PG_TEMP_SCHEMA_TABLES | Set to 'yes' to prevent tables from "pg_temp" schema from being returned by EnumerateTables | &ndash; | &ndash;  
CAP_ODBC_SUPPRESS_PREPARED_QUERY_FOR_ALL_COMMAND_QUERIES | Set to 'yes' to execute all commands directly (that is, no prepared statement). | &ndash; | &ndash; 
CAP_ODBC_SUPPRESS_PREPARED_QUERY_FOR_DDL_COMMAND_QUERIES | Set to 'yes' to execute DDL commands (for example, CREATE TABLE) directly (that is, no prepared statement). | &ndash; | &ndash; 
CAP_ODBC_SUPPRESS_PREPARED_QUERY_FOR_DML_COMMAND_QUERIES | Set to 'yes' to execute DML commands (for example, INSERT INTO) directly (i.e, no prepared statement). | &ndash; | &ndash; 
CAP_ODBC_SUPPRESS_PREPARED_QUERY_FOR_NON_COMMAND_QUERIES | Set to 'yes' to execute all non-command queries directly (no prepared statement). | &ndash; | &ndash;
CAP_ODBC_TRANSACTIONS_COMMIT_INVALIDATES_PREPARED_QUERY | Set to ‘yes’ to indicate that a transaction will invalidate all prepared statements and close any open cursors. | &ndash; | &ndash; 
CAP_ODBC_TRANSACTIONS_SUPPRESS_EXPLICIT_COMMIT | Set to 'yes' to prevent the Native ODBC Protocol from explicitly managing transactions. | &ndash; | &ndash; 
CAP_ODBC_TRIM_CHAR_LEAVE_PADDING | Set to 'yes' to leave whitespace padding at the end of a character or text data type. Most data sources will trim this whitespace automatically, but the behavior depends on the driver. | &ndash; | &ndash; 
CAP_ODBC_TRIM_VARCHAR_PADDING | Set to 'yes' to force the Tableau native ODBC protocol to trim trailing whitespace from VARCHAR columns which the driver has erroneously padded. | &ndash; | &ndash; 
CAP_ODBC_UNBIND_AUTO | Set to 'yes' to force the Tableau native ODBC protocol to unbind and deallocate columns automatically, which can reduce ODBC API calls. | &ndash; | &ndash; 
CAP_ODBC_UNBIND_BATCH | Set to 'yes' to force the Tableau native ODBC protocol to unbind and deallocate columns in a single batch operation, which can reduce ODBC API calls. | &ndash; | &ndash; 
CAP_ODBC_UNBIND_EACH | Set to 'yes' to force the Tableau native ODBC protocol to unbind and deallocate columns individually, which may improve stability. | yes | yes 
CAP_ODBC_UNBIND_PARAMETERS_BATCH | Set to ‘yes’ to unbind all parameters in a single batch operation. | yes | yes 

## Stored Procedures

Capability | Description | Default | Recommended 
-|-|-|-
CAP_CONNECT_STORED_PROCEDURE | Set to 'yes' to allow support for connecting to a stored procedure. | &ndash; | &ndash;
CAP_INSERT_TEMP_EXEC_STORED_PROCEDURE | Set to 'yes' to populate the temporary table from running query in the database | no | no  
CAP_JDBC_SUPPRESS_INFO_SCHEMA_STORED_PROCS | Set to 'yes' to prevent the INFORMATION.SCHEMA schema from being queried when enumerating stored procedures. | &ndash; | &ndash;
CAP_ODBC_SUPPRESS_INFO_SCHEMA_STORED_PROCS | Set to 'yes' to prevent the INFORMATION.SCHEMA schema from being queried when enumerating stored procedures. | &ndash; | &ndash; 
CAP_ODBC_SUPPRESS_SYS_SCHEMA_STORED_PROCS | Set to 'yes' to explicitly add the "SYS" schema to the schema exclusions when enumerating stored procedures. | &ndash; | &ndash; 
CAP_STORED_PROCEDURE_PREFER_TEMP_TABLE | Set to 'yes' to use a temporary table to support remote queries over the stored procedure result set. | &ndash; | &ndash;
CAP_STORED_PROCEDURE_REPAIR_TEMP_TABLE_STRINGS | Set to 'yes' to attempt to compute actual string widths if metadata indicates no width or non-positive width. | &ndash; | &ndash;
CAP_STORED_PROCEDURE_TEMP_TABLE_FROM_BUFFER | Set to 'yes' to populate the temporary table from a result set buffered in entirety. | &ndash; | &ndash;
CAP_STORED_PROCEDURE_TEMP_TABLE_FROM_NEW_PROTOCOL | Set to ‘yes’ to populate the temporary table from a separate protocol created for just this operation. | &ndash; | &ndash;

## Isolation Level

Capability | Description | Default | Recommended
-|-|-|-
CAP_ISOLATION_LEVEL_READ_COMMITTED | Set to 'yes' to force the transaction isolation level to Read Committed if the data source supports it. Only one of the four transaction isolation levels should be set to 'yes'. See also: CAP_SET_ISOLATION_LEVEL_VIA_SQL, CAP_SET_ISOLATION_LEVEL_VIA_ODBC_API. | &ndash; | &ndash; 
CAP_ISOLATION_LEVEL_READ_UNCOMMITTED | Set to 'yes' to force the transaction isolation level to Read Uncommitted if the data source supports it. Only one of the four transaction isolation levels should be set to 'yes'. This capability can improve speed by reducing lock contention, but may result in partial or inconsistent data in query results. See also: CAP_SET_ISOLATION_LEVEL_VIA_SQL, CAP_SET_ISOLATION_LEVEL_VIA_ODBC_API. | &ndash; | &ndash; 
CAP_ISOLATION_LEVEL_REPEATABLE_READS | Set to 'yes' to force the transaction isolation level to Repeatable Reads if the data source supports it. Only one of the four transaction isolation levels should be set to 'yes'. See also: CAP_SET_ISOLATION_LEVEL_VIA_SQL, CAP_SET_ISOLATION_LEVEL_VIA_ODBC_API. | &ndash; | &ndash; 
CAP_ISOLATION_LEVEL_SERIALIZABLE | Set to 'yes' to force the transaction isolation level to Serializable if the data source supports it. Only one of the four transaction isolation levels should be set to 'yes'. This is a very conservative setting that may improve stability at the expense of performance. See also: CAP_SET_ISOLATION_LEVEL_VIA_SQL, CAP_SET_ISOLATION_LEVEL_VIA_ODBC_API. | &ndash; | &ndash; 
CAP_SET_ISOLATION_LEVEL_VIA_ODBC_API | Set to 'yes' to force Tableau to set the transaction isolation level for the data source using the ODBC API. CAP_SET_ISOLATION_LEVEL_VIA_ODBC_API must be set to 'yes' when any one of the four CAP_ISOLATION_LEVEL capabilities has been set to 'yes'. | &ndash; | &ndash; 
CAP_SET_ISOLATION_LEVEL_VIA_SQL | Set to 'yes' to force Tableau to set the transaction isolation level for the data source using a SQL query. CAP_SET_ISOLATION_LEVEL_VIA_SQL must be set to 'yes' when any one of the four CAP_ISOLATION_LEVEL capabilities has been set to 'yes'. | &ndash; | &ndash; 

## Uncommon

Capability | Description | Default | Recommended
-|-|-|-
CAP_EXTRACT_ONLY | Set to 'yes' to perform queries on extracted data only. | &ndash; | &ndash;  
CAP_FORCE_COUNT_FOR_NUMBEROFRECORDS | Set to 'yes' to force these alternatives for calculating number of records: <br>1. COUNT(1) rather than SUM(1) <br>2. COUNT(const) * const rather than SUM(const) <br>Available in Tableau 2020.2 and newer. | &ndash; | &ndash;  
CAP_SUPPRESS_GET_SERVER_TIME | Some data sources, such as Hive, are very slow at retrieving the server time.  | &ndash; | &ndash; 
CAP_SUPPORTS_UNION | Set to 'no' if data source doesn't support UNION functionality. | yes | yes 
