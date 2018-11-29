---
title: Capabilities
---

When a value (yes, no, ?) in the Recommended column is bold, verify that the value you use is correct for your database.

## Metadata

Capability | Description | Default | Recommended
-|-|-|-
CAP_FAST_METADATA | Set to 'yes' if you have small to moderate size schemas. This capability controls whether Tableau should enumerate all of the objects immediately when you connect. Set the value to “yes” to enable this capability for better performance when creating new connections. Disable this capability to allow search for specific schemas or tables instead of retrieving all objects. You can search for all objects by using an empty string. This capability is available in 9.0 and later. | yes | yes
CAP_QUERY_TOP_0_METADATA | Set to 'yes' if the datasource can handle a "TOP 0" request for retrieving metadata | no | **?**
CAP_QUERY_WHERE_no_METADATA | Set to 'yes' if the datasource can handle a "WHERE \<no\>" predicate for retrieving metadata | &ndash; | **?**

## Temporary Tables

Capability | Description | Default | Recommended
-|-|-|-
CAP_CREATE_TEMP_TABLES | Set to 'yes' if Tableau can create temporary tables needed for certain complex or optimized queries. See also: CAP_SELECT_INTO. | &ndash; | **?**
CAP_CREATE_TEMP_TABLES_DROP_NULLABILITY | Set to 'yes' if Tableau needs to drop nullability when creating temp tables through SELECT INTO | &ndash; | &ndash;
CAP_INDEX_TEMP_TABLES | Set to 'yes' if datasource supports creation of indexes on temp tables database | &ndash; | &ndash;
CAP_QUERY_USE_TEMP_TABLE_NAMES_AS_SUBQUERY_ALIASES | Set to 'yes' if Tableau must use generated temporary table names for aliases of subqueries because they might end up implemented as temporary tables | no | no
CAP_SELECT_INTO | Set to 'yes' if Tableau can create a table on the fly from the resultset of another query. See also: CAP_CREATE_TEMP_TABLES. | &ndash; | **?**
CAP_SELECT_TOP_INTO | Set to 'yes' if Tableau can use a TOP or LIMIT row-limiting clause when creating a table from a query resultset. | &ndash; | **?**
CAP_ODBC_METADATA_FORCE_UTF8_TEMP_TABLE_COLUMN_SIZE | Set to 'yes' if when creating temp tables specify the size of varchar columns in bytes. | &ndash; | &ndash;
CAP_TEMP_TABLES_NOT_SESSION_SCOPED | Set to 'yes' if this datasource uses regular tables to simulate temp tables. Temporary table creation is still controlled by CAP_CREATE_TEMP_TABLE or CAP_SELECT_INTO | &ndash; | &ndash;

## String Splits

Capability | Description | Default | Recommended
-|-|-|-
CAP_SUPPORTS_SPLIT_FROM_LEFT | *supports splitting a string from the left* | &ndash; | **yes**
CAP_SUPPORTS_SPLIT_FROM_RIGHT | *supports splitting a string from the right* | &ndash; | **?**

## Query

Capability | Description | Default | Recommended
-|-|-|-
CAP_QUERY_ALLOW_JOIN_REORDER | Query optimization to reduce database work with some inner and equality joins. | yes | yes
CAP_QUERY_ALLOW_PARTIAL_AGGREGATION | *Tableau can minimize data movement (and boost performance) in federated join scenarios by performing as much aggregation as possible in remote databases before shipping the data back. This can introduce additional groupbys on the fields used in the join condition. If the join is on a string field, not all datasources handle the additional groupbys on strings efficiently, leading to a rapid degradation in performance the more join key fields are used.* | yes | yes
CAP_QUERY_BOOL_IDENTIFIER_TO_LOGICAL | *Can the dialect handle WHEN [bit column] THEN or does it need something like WHEN [column] = 1 THEN.* | &ndash; | &ndash;
CAP_QUERY_BOOLEXPR_TO_INTEXPR | Set to 'yes' if Tableau must coerce any Boolean expressions to an integer value in order include in a result set. | &ndash; | **?**
CAP_QUERY_CASE_MATCHES_NULL | *Can CASE match a nullptr in a valued CASE expression?* | no | no
CAP_QUERY_CASE_PROMOTES_CHAR | *Can CASE promote character types?* | yes | yes
CAP_QUERY_FROM_REQUIRES_ALIAS | Set to 'yes' if the FROM clause must provide an alias for the given table. | &ndash; | &ndash;
CAP_QUERY_GROUP_ALLOW_DUPLICATES | Set to 'no' if SQL queries cannot contain duplicate expressions in the GROUP BY clause (this is uncommon). | yes | yes
CAP_QUERY_GROUP_BY_ALIAS | Set to 'yes' if SQL queries with aggregations can reference the grouping columns by their corresponding alias in the SELECT list, e.g. GROUP BY "none_ShipCountry_nk". | no | no
CAP_QUERY_GROUP_BY_BOOL | Can the database group by a raw boolean? If not, try casting to an INT. | &ndash; | **yes**
CAP_QUERY_GROUP_BY_DEGREE | Set to 'yes' if SQL queries with aggregations can reference the grouping columns by the ordinal position of each column, e.g. GROUP BY 2, 5. See also: CAP_QUERY_SORT_BY_DEGREE | no | **?**
CAP_QUERY_HAVING_REQUIRES_GROUP_BY | Set to 'yes' if Tableau must use an artificial grouping field for any query which has a HAVING clause but no grouping columns. | &ndash; | **?**
CAP_QUERY_HAVING_UNSUPPORTED | Set to 'yes' if the SQL syntax for HAVING is unsupported. Tableau may be able to work around this using subqueries. See also: CAP_QUERY_SUBQUERIES. | &ndash; | &ndash;
CAP_QUERY_INCLUDE_GROUP_BY_COLUMNS_IN_SELECT | Set to 'yes' to require all GROUP BY expressions to also appear in the SELECT expression list. | &ndash; | &ndash;
CAP_QUERY_INCLUDE_HAVING_COLUMNS_IN_SELECT | *Google Big Query needs the HAVING columns in the select clause all the time* | &ndash; | &ndash;
CAP_QUERY_INITIAL_SQL_SPLIT_STATEMENTS | *Does the data source require that multiple statements are issued as separate queries for Initial SQL?* | &ndash; | **?**
CAP_QUERY_INOUT_JOINS | *Can the connection handle the joins needed for IN/OUT set calculations?* | yes | yes
CAP_QUERY_JOIN_ACROSS_SCHEMAS | Set to 'yes' if SQL queries can express joins between tables located in different schemas. | no | **?**
CAP_QUERY_JOIN_ASSUME_CONSTRAINED | Set to ‘yes’ to cull inner joins even if the database tables does do not have FK-PK relationships. | &ndash; | &ndash;
CAP_QUERY_JOIN_MISMATCHED_VARCHAR_WIDTHS | *Can join predicates have different widths for VARCHAR columns?* | yes | **?**
CAP_QUERY_JOIN_PREDICATE_REQUIRES_SCOPE | *Join predicates must be enclosed in parens* | yes | yes
CAP_QUERY_JOIN_PUSH_DOWN_CONDITION_EXPRESSIONS | Set to 'yes' to rewrite joins to simplify the ON clause conditions to simple identifier comparisons. | &ndash; | &ndash;
CAP_QUERY_JOIN_REQUIRES_SCOPE | Set to 'yes' if SQL queries must scope each join clause within parentheses to ensure a proper order of evaluation. | &ndash; | &ndash;
CAP_QUERY_JOIN_REQUIRES_SUBQUERY | Set to ‘yes’ to force join expressions involving more than two tables to be composed with subqueries. | &ndash; | &ndash;
CAP_QUERY_NAKED_JOINS | *Do we need to wrap the base relation to join filters?* | yes | yes
CAP_QUERY_RECONNECT_ON_ERROR | *On datasource connection error, reconnect and run the abstract query once before erroring out. MDX only* | no | no
CAP_QUERY_SELECT_ALIASES_SORTED | Set to 'yes' if Tableau must impose a deterministic order on the SELECT expressions (sorted by alias) to ensure that query results can be properly matched with each field in the Tableau visualization. This is only required for data sources which do not preserve the aliases of the SELECT expressions when returning metadata with the query results. | no | no
CAP_QUERY_SORT_BY | Enables the 'Field' option in the Sort menu | no | **yes**
CAP_QUERY_SORT_BY_DEGREE | Set to 'yes' if SQL queries can reference the sorting columns by the ordinal position of each column, e.g. ORDER BY 2, 5. See also: CAP_QUERY_GROUP_BY_DEGREE. | yes | **?**
CAP_QUERY_SORT_BY_NON_NUMERIC | *Can we sort by non-numeric values?* | yes | yes
CAP_QUERY_SQL_GENERATION | Seems to be an internall setting that you shouldn't modify. *Do we generate SQL text?* | yes | yes
CAP_QUERY_SUBQUERIES | Set to 'yes' if the data source supports subqueries. | &ndash; | **yes**
CAP_QUERY_SUBQUERIES_WITH_TOP | Set to 'yes' if the data source supports a TOP or LIMIT row-limiting clause within a subquery. | yes | **?**
CAP_QUERY_SUBQUERY_QUERY_CONTEXT | Set to 'yes' to force Tableau to use a subquery for context filters instead of a temporary table or locally cached results. | yes | yes
CAP_QUERY_SUPPORT_EMPTY_GROUPBY | *supports empty group by* | &ndash; | &ndash;
CAP_QUERY_SUPPORTS_LODJOINS | *supports the types of joins we need for LOD calcs* | yes | yes
CAP_QUERY_TOP_0 | *Can the server handle a "TOP 0" request?* | yes | yes
CAP_QUERY_TOP_N | Set to 'yes' if the data source supports any form of row-limiting clause. The exact forms supported are described below. | no | **yes**
CAP_QUERY_TOP_PERCENT | *TOP supports percent* | no | **?**
CAP_QUERY_TOP_SAMPLE | *TOP supports sampling rows* | no | **?**
CAP_QUERY_TOP_SAMPLE_FAST | *TOP with sampling is faster than TOP* | no | no
CAP_QUERY_TOP_SAMPLE_PERCENT | *TOP supports sampling by percentages* | no | **?**
CAP_QUERY_USE_DOMAIN_RANGES_OPTIMIZATION | *Use domain ranges to optimize set functions.* | yes | yes
CAP_QUERY_USE_QUERY_FUSION | Set to ‘no’ to prevent Tableau from combining multiple individual queries into a single combined query. Turn off this capability for performance tuning or if the database is unable to process large queries. This capability is enabled by default and is available in Tableau 9.0 and later for all data sources except Tableau data extracts. Support for this capability in Tableau data extracts is available in Tableau 9.0.6. | yes | yes
CAP_QUERY_WRAP_SUBQUERY_WITH_TOP | *Can the server handle a subquery wrapped with only a TOP clause?* | no | no

## JDBC

Capability | Description | Default | Recommended
-|-|-|-
CAP_JDBC_EXPORT_DATA_BATCH | Set to 'no' to disable the use of JDBC batch operations for data insert. | yes | yes
CAP_JDBC_EXPORT_TRANSLATE_DATA_PARALLEL | Set to 'no' to disable use of parallel loops to translate Tableau DataValues to wire buffers on exports | yes | yes
CAP_JDBC_JNI_FETCH_SIZE_SMALL | *Fetch 10 rows per JNI call* | &ndash; | &ndash;
CAP_JDBC_JNI_FETCH_SIZE_MEDIUM | *Fetch 100 rows per JNI call* | yes | yes
CAP_JDBC_JNI_FETCH_SIZE_LARGE | *Fetch 1000 rows per JNI call* | &ndash; | &ndash;
CAP_JDBC_JNI_FETCH_SIZE_MASSIVE | *Fetch 10000 rows per JNI call* | &ndash; | &ndash;
CAP_JDBC_METADATA_GET_INDEX_INFO | Set to 'no' to disable reading index info | yes | yes
CAP_JDBC_METADATA_READ_FOREIGNKEYS | Set to 'no' to disable reading foreign key metadata | yes | yes
CAP_JDBC_METADATA_READ_PRIMARYKEYS | Set to 'no' to disable reading primary key metadata | yes | yes
CAP_JDBC_QUERY_ASYNC | Set to 'yes' to run queries on another thread | &ndash; | **yes**
CAP_JDBC_QUERY_CANCEL | Set to 'yes' if driver can cancel queries | &ndash; | **yes**
CAP_JDBC_SUPPRESS_ENUMERATE_DATABASES | Set to 'yes' to disable database enumeration. | &ndash; | &ndash;
CAP_JDBC_SUPPRESS_ENUMERATE_SCHEMAS | Set to 'yes' to disable schema enumeration. | &ndash; | &ndash;
CAP_JDBC_SUPPRESS_ENUMERATE_TABLES | Set to 'yes' to disable table enumeration. | &ndash; | &ndash;

## ODBC

Capability | Description | Default | Recommended
-|-|-|-
CAP_ODBC_BIND_BOOL_AS_WCHAR_01LITERAL | Set to 'yes' to bind a Boolean data type as a WCHAR containing values '0' or '1'. | &ndash; | &ndash;
CAP_ODBC_BIND_BOOL_AS_WCHAR_TFLITERAL | Set to 'yes' to bind a Boolean data type as WCHAR containing values 't' or 'f'. | &ndash; | &ndash;
CAP_ODBC_BIND_DETECT_ALIAS_CASE_FOLDING | Set to 'yes' to allow Tableau to detect and recover from an ODBC data source that reports the field names in a result set using only upper-case or lower-case characters, instead of the expected field names. | &ndash; | &ndash;
CAP_ODBC_BIND_FORCE_DATE_AS_CHAR | Set to 'yes' to force the Tableau native ODBC protocol to bind date values as CHAR. | &ndash; | &ndash;
CAP_ODBC_BIND_FORCE_DATETIME_AS_CHAR | Set to 'yes' to force the Tableau native ODBC protocol to bind datetime values as CHAR. | &ndash; | &ndash;
CAP_ODBC_BIND_FORCE_MAX_STRING_BUFFERS | Set to 'yes' to force the Tableau native ODBC protocol to use maximum-sized buffers (1MB) for strings instead of the size described by metadata. | &ndash; | &ndash;
CAP_ODBC_BIND_FORCE_MEDIUM_STRING_BUFFERS | Set to 'yes' to force the Tableau native ODBC protocol to use medium-sized buffers (1K) for strings instead of the size described by metadata. | &ndash; | &ndash;
CAP_ODBC_BIND_FORCE_SIGNED | Set to 'yes' to force binding integers as signed. | &ndash; | &ndash;
CAP_ODBC_BIND_FORCE_SMALL_STRING_BUFFERS | Set to 'yes' to force the Tableau native ODBC protocol to use small buffers for strings instead of the size described by metadata. | &ndash; | &ndash;
CAP_ODBC_BIND_PRESERVE_BOM | Set to 'yes' to preserve BOM when present in strings. Hive will return BOM and treat strings containing it as distinct entities. | &ndash; | &ndash;
CAP_ODBC_BIND_SKIP_LOCAL_DATATYPE_UNKNOWN | Set to 'yes' to prevent the native ODBC Protocol from binding to columns having local data type DataType::Unknown in the expected metadata | &ndash; | &ndash;
CAP_ODBC_BIND_SPATIAL_AS_WKT | Set to 'yes' to force binding Spatial data as WKT (Well Known Text) | &ndash; | &ndash;
CAP_ODBC_BIND_SUPPRESS_COERCE_TO_STRING | Set to 'yes' to prevent the Tableau native ODBC protocol from binding non-string data as strings (i.e. requesting driver conversion). | &ndash; | &ndash;
CAP_ODBC_BIND_SUPPRESS_INT64 | Set to 'yes' to prevent the Tableau native ODBC protocol from using 64-bit integers for large numeric data. | &ndash; | &ndash;
CAP_ODBC_BIND_SUPPRESS_PREFERRED_CHAR | Set to 'yes' to prevent the Tableau native ODBC protocol from preferring a character type that differs from the driver default. | &ndash; | &ndash;
CAP_ODBC_BIND_SUPPRESS_PREFERRED_TYPES | Set to 'yes' to prevent the Tableau native ODBC protocol from binding any data according to its preferred wire types. With this capability set, Tableau will only bind according to the data types described by the ODBC driver via metadata. | &ndash; | &ndash;
CAP_ODBC_BIND_SUPPRESS_WIDE_CHAR | Set to 'yes' to prevent the Tableau native ODBC protocol from binding strings a WCHAR. Instead they will be bound as single-byte CHAR arrays, and processed locally for any UTF-8 characters contained within. | &ndash; | &ndash;
CAP_ODBC_CONNECTION_STATE_VERIFY_FAST | Set to ‘yes’ to check if a connection is broken with a fast ODBC API call. | yes | yes
CAP_ODBC_CONNECTION_STATE_VERIFY_PROBE | Set to ‘yes’ to check if a connection is broken with a forced probe. | no | no
CAP_ODBC_CONNECTION_STATE_VERIFY_PROBE_IF_STALE | Set to ‘yes’ to check if a connection is broken with a forced probe only if it is "stale" (i.e., unused for about 30 minutes). | yes | yes
CAP_ODBC_CONNECTION_STATE_VERIFY_PROBE_PREPARED_QUERY | Set to ‘yes’ to check if a connection is broken using a prepared query. | yes | yes
CAP_ODBC_CURSOR_DYNAMIC | Set to 'yes' to force the Tableau native ODBC protocol to set the cursor type for all statements to Dynamic (scrollable, detects added/removed/modified rows). | &ndash; | &ndash;
CAP_ODBC_CURSOR_FORWARD_ONLY | Set to 'yes' to force the Tableau native ODBC protocol to set the cursor type for all statements to Forward-only (non-scrollable). | &ndash; | **?**
CAP_ODBC_CURSOR_KEYSET_DRIVEN | Set to 'yes' to force the Tableau native ODBC protocol to set the cursor type for all statements to Keyset-driven (scrollable, detects changes to values within a row). | &ndash; | &ndash;
CAP_ODBC_CURSOR_STATIC | Set to 'yes' to force Tableau to set the cursor type for all statements to Static (scrollable, does not detect changes). | &ndash; | &ndash;
CAP_ODBC_ERROR_IGNORE_no_ALARM | Set to 'yes' to allow the Tableau native ODBC protocol to ignore SQL_ERROR conditions where SQLSTATE is '00000' (meaning "no error"). | &ndash; | &ndash;
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
CAP_ODBC_METADATA_FORCE_LENGTH_AS_PRECISION | Set to 'yes' to force the Tableau native ODBC protocol to use the column "length" as the numeric precision. This is an uncommon setting. | &ndash; | &ndash;
CAP_ODBC_METADATA_FORCE_NUM_PREC_RADIX_10 | Set to 'yes' to force the Tableau native ODBC protocol to assume the numeric precision is reported in base-10 digits. This is an uncommon setting. | &ndash; | &ndash;
CAP_ODBC_METADATA_FORCE_UNKNOWN_AS_STRING | Set to 'yes' to force the Native ODBC Protocol to treat unknown data types as string instead of ignoring the associated column. | &ndash; | &ndash;
CAP_ODBC_METADATA_FORCE_UTF8_IDENTIFIERS | Set to 'yes' to force the protocol to treat identifiers as UTF-8 when communicating with the driver. | &ndash; | &ndash;
CAP_ODBC_METADATA_SKIP_DESC_TYPE_NAME | Set to 'yes' to remove the check for the SQL_DESC_TYPE_NAME attribute with the SQLColAttribute API. | &ndash; | &ndash;
CAP_ODBC_METADATA_STRING_LENGTH_UNKNOWN | Set to 'yes' to prevent Tableau from allocating memory based on the driver-reported string length, which may not be known or reported properly. Instead, Tableau will use a fixed-sized string length, and will reallocate as needed to handle string data that is too large for the fixed-size buffer. | &ndash; | &ndash;
CAP_ODBC_METADATA_STRING_TRUST_OCTET_LENGTH | Set to 'yes' to use the octet length reported by the driver for strings instead of computing it from the number of characters. | &ndash; | &ndash;
CAP_ODBC_METADATA_SUPPRESS_EXECUTED_QUERY | Set to 'yes' to prevent Tableau from executing a query as a means of reading metadata. While Tableau typically includes a row-limiting clause in such metadata queries (e.g., 'LIMIT', or 'WHERE 1=0'), this may not help when used with a Custom SQL connection for database systems with poor query optimizers. Note that this capability may prevent Tableau from determining the connection metadata properly. | &ndash; | &ndash;
CAP_ODBC_METADATA_SUPPRESS_PREPARED_QUERY | Set to 'yes' to prevent Tableau from using a prepared query as a means of reading metadata. A prepared query is often the fastest way to accurately read metadata. However, not all database systems are capable of reporting metadata for a prepared query without actually executing the query. Note that certain metadata -- for example from connections using Custom SQL -- cannot be retrieved if this capability and CAP_ODBC_METADATA_SUPPRESS_EXECUTED_QUERY are both set. | &ndash; | &ndash;
CAP_ODBC_METADATA_SUPPRESS_READ_IDENTITY_COLUMNS | Set to 'no' to prevent reading identity column metadata | yes | yes
CAP_ODBC_METADATA_SUPPRESS_SELECT_STAR | Set to 'yes' to prevent reading metadata using a 'select *' query. | &ndash; | &ndash;
CAP_ODBC_METADATA_SUPPRESS_SQLCOLUMNS_API | Set to 'yes' to prevent Tableau from using older, less accurate API for reading metadata from ODBC data sources. Setting this capability allows Tableau to read metadata by issuing a full 'select *' query, which is expensive but may enable connectivity for extremely limited or unstable data sources. | &ndash; | &ndash;
CAP_ODBC_METADATA_SUPPRESS_SQLFOREIGNKEYS_API | Set to 'yes' to prevent Tableau from attempting to read metadata describing foreign key constraints. Despite the simple nature of this ODBC API, some drivers may have unstable behavior or produce inaccurate results. Setting this capability may force Tableau to generate less efficient queries involving multi-table joins. | &ndash; | &ndash;
CAP_ODBC_METADATA_SUPPRESS_SQLPRIMARYKEYS_API | Set to 'yes' to prevent Tableau from reading primary key metadata using the SQLPrimaryKeys API or an equivalent query. This capability is available in Tableau 9.1 and later. | &ndash; | &ndash;
CAP_ODBC_METADATA_SUPPRESS_SQLSTATISTICS_API | Set to 'yes' to prevent reading unique constraints and table cardinality estimates using the SQLStatistics API or an equivalent query. This capability is available in Tableau 9.0 and later. | yes | yes
CAP_ODBC_REBIND_SKIP_UNBIND | Set to 'yes' to force the Tableau native ODBC protocol to rebind a column directly and skip unbinding, which reduces ODBC API calls when resizing buffers to refetch truncated data. | &ndash; | &ndash;
CAP_ODBC_SUPPORTS_LONG_DATA_BULK | Set to 'yes' if driver can fetch multiple long-data rows at a time. | no | no |
CAP_ODBC_SUPPORTS_LONG_DATA_ORDERED | Set to 'yes' if driver requires long-data columns to come after non-long-data ones | no | no |
CAP_ODBC_SUPPRESS_INFO_SCHEMA_TABLES | Set to 'yes' to prevent tables from "information_schema" schema from being returned by EnumerateTables | &ndash; | &ndash;
CAP_ODBC_SUPPRESS_PG_TEMP_SCHEMA_TABLES | Set to 'yes' to prevent tables from "pg_temp" schema from being returned by EnumerateTables | &ndash; | &ndash;
CAP_ODBC_SUPPRESS_PREPARED_QUERY_FOR_ALL_COMMAND_QUERIES | Set to 'yes' to execute all commands directly (i.e., no prepared statement). | &ndash; | &ndash;
CAP_ODBC_SUPPRESS_PREPARED_QUERY_FOR_DDL_COMMAND_QUERIES | Set to 'yes' to execute DDL commands (e.g. CREATE TABLE) directly (i.e., no prepared statement). | &ndash; | &ndash;
CAP_ODBC_SUPPRESS_PREPARED_QUERY_FOR_DML_COMMAND_QUERIES | Set to 'yes' to execute DML commands (e.g. INSERT INTO) directly (i.e, no prepared statement). | &ndash; | &ndash;
CAP_ODBC_SUPPRESS_PREPARED_QUERY_FOR_NON_COMMAND_QUERIES | Set to 'yes' to execute all non-command queries directly (no prepared statement). | &ndash; | &ndash;
CAP_ODBC_TRANSACTIONS_COMMIT_INVALIDATES_PREPARED_QUERY | Set to ‘yes’ to indicate that a transaction will invalidate all prepared statements and close any open cursors. | &ndash; | &ndash;
CAP_ODBC_TRANSACTIONS_SUPPRESS_AUTO_COMMIT | Set to 'yes' to prevent the Native ODBC Protocol from using default auto-committing transaction behavior in ODBC. This capability cannot be used with CAP_ODBC_TRANSACTIONS_SUPPRESS_EXPLICIT_COMMIT. | &ndash; | &ndash;
CAP_ODBC_TRANSACTIONS_SUPPRESS_EXPLICIT_COMMIT | Set to 'yes' to prevent the Native ODBC Protocol from explicitly managing transactions. This capability cannot be used with CAP_ODBC_TRANSACTIONS_SUPPRESS_AUTO_COMMIT. | &ndash; | &ndash;
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
CAP_CONNECT_NO_CUSTOM_SQL | Set to 'yes' to disable the custom sql option. | &ndash; | &ndash;
CAP_EXTRACT_ONLY | Set to 'yes' to perform queries on extracted data only | &ndash; | &ndash;
CAP_SUPPRESS_GET_SERVER_TIME | Some datasources, such as Hive, are very slow at retrieving the server time  | &ndash; | &ndash;
CAP_SUPPORTS_UNION | Controls allowing UNIONs. It cannot be customized in a TDC for an existing connector but it does work for plugins. | yes | yes


