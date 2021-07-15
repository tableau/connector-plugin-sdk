---
title: Create a Tableau Dialect Definition File
---

A Tableau Dialect Definition file (.tdd) maps Tableau's query language to a database’s SQL. This is an XML file with a .tdd filename extension, and is one of the main components of a Tableau connector.

You should create a dialect definition file whenever you need to make changes to an existing Tableau dialect or define an entirely new dialect. If your connector uses the same SQL dialect as the connector it’s based on, such as PostgreSQL, then a new  TDD file isn't necessary.

## Create a TDD file

To get started quickly, you can copy the sample dialect.tdd file from the [postgres_odbc or postgres_jdbc folder](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins) and use the copy to make your modifications.

The XML schema for the plugin XML files is validated using XSD files. The dialect(.tdd) file is validated using [this XSD file](https://github.com/tableau/connector-plugin-sdk/blob/master/validation/tdd_latest.xsd).

Tableau searches for a TDD file in the location specified by the connector manifest XML file. The TDD format breaks down as follows:

### Dialect tag

The <span style="font-family: courier new">dialect</span> tag serves as the root for the document. For example:

```
<dialect
   name='CustomDialect'
   class='postgres'
   version='20.1'>
```

The <span style="font-family: courier new">dialect</span> tag has several required attributes and a couple of optional ones.

Attribute | Required | Description
-|-|-
name | Y | Dialect name. Used for dependency lookup.
class | Y | Should match the plug-in's class, as defined in the manifest.
base | N | Specifies a base dialect to build upon. If a certain property or function isn't defined in a dialect definition file, the connector will fall back to its base dialect's behavior (assuming a value for <span style="font-family: courier new">base</span> is defined), and SQL-92 default behavior (if a value for <span style="font-family: courier new">base</span> is not defined).  **Important:** This must be a valid, existing dialect. If the specified base does not exist, the connector will fail to load. For a list of bases, see [Dialect base classes]({{ site.baseurl }}/docs/design#dialect-base-classes).
dialect-version | N | Indicates the minimum database version applicable to the TDD file. For example, if you're adding a function definition that wasn't implemented until FooDB 3.0, then <span style="font-family: courier new">set dialect-version='3.0'</span>.
version | Y | Must match the current Tableau version in the format YY.Q; for example, "20.1".


### Supported-aggregations element

The <span style="font-family: courier new">supported-aggregations</span> element contains a list of aggregations and date truncation levels supported by the database, represented by one or more <span style="font-family: courier new">aggregation</span> elements.

- __aggregation element__
An <span style="font-family: courier new">aggregation</span> element has one required attribute, <span style="font-family: courier new">value</span>, which specifies a single aggregation or truncation. For a list, see [supported aggregations](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/components/dialects/Annotated.tdd#L1051).

### Function-map element

The <span style="font-family: courier new">function-map</span> element has no attributes and contains any number of <span style="font-family: courier new">function</span>, <span style="font-family: courier new">date-function</span>, and <span style="font-family: courier new">remove-function</span> elements.


- __function element__
Each <span style="font-family: courier new">function</span> element defines a single function. It has a few required attributes, contains a <span style="font-family: courier new">formula</span> element (and in some cases, an <span style="font-family: courier new">unagg-formula</span> element) and any number of <span style="font-family: courier new">argument</span> elements. For a list of supported functions, see the [FullFunctionMap.tdd](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/components/dialects/FullFunctionMap.tdd) file sample.



Attribute | Required | Description
-|-|-
name | Y | Indicates the name of the function being added or overridden.
group | Y | Contains one or more (comma-separated) groups that this function belongs to. Allowable types: aggregate, cast, date, logical, numeric, operator, passthru, special, string, system.
return-type | Y | Indicates the return type of the function. For a list of allowable types, see [argument-element](#Argument) below.

- __date-function element__
The <span style="font-family: courier new">date-function</span> element is a specialized variant of <span style="font-family: courier new">function</span>. In addition to the base formula, you can specify one or more datepart formulas, which are used instead of the generic formula when available.
The function <span style="font-family: courier new">name</span> must be one of these: DATEADD, DATEDIFF, DATENAME, DATEPARSE, DATEPART, DATETRUNC.
 Like <span style="font-family: courier new">function</span>, <span style="font-family: courier new">date-function</span> requires name and return-type, but unlike <span style="font-family: courier new">function</span>, group is not required.

  **Example: DATEPART without custom start of week**

    ```xml
        ...
        <date-function name='DATEPART' return-type='int'>
          <formula>CAST(TRUNC(EXTRACT(%1 FROM %2)) AS INTEGER)</formula>
          <formula part='weekday'>(1 + CAST(EXTRACT(DOW FROM %2) AS INTEGER))</formula>
          <formula part='week'>CAST(FLOOR((7 + EXTRACT(DOY FROM %2) - 1 + EXTRACT(DOW FROM DATE_TRUNC(&apos;YEAR&apos;, %2))) / 7) AS INTEGER)</formula>
          <argument type='localstr' />
          <argument type='datetime' />
        </date-function>
        ...
    ```

    Here the first argument (%1) is the value from the `<date-part-group>` in the dialect file.  A date-part-group can apply to one or more date functions, denoted by date-function child elements.
    If none are specified, the group acts as the default.
    The name attribute specifies a Tableau date part, while the value attribute contains the date part string literal to use in corresponding date functions.

    ```xml
        ...
          <date-part-group>
            <date-function name='DATEPART' />
            <part name='year' value='YEAR' />
            <part name='quarter' value='QUARTER' />
            <part name='month' value='MONTH' />
            <part name='week' value='WEEK' />
            <part name='weekday' value='DOW' />
            <part name='dayofyear' value='DOY' />
            <part name='day' value='DAY' />
            <part name='hour' value='HOUR' />
            <part name='minute' value='MINUTE' />
            <part name='second' value='SECOND' />
          </date-part-group>
        ...
    ```
    A single date function can have multiple overloaded functions with different parameters.
    <br/>
    To support Tableau's Custom Start of Week functionality each of the following: DATEDIFF, DATENAME, DATEPART, DATETRUNC need to also have an overloaded form with an additional `<argument type='localstr' />`.
    <br/>
    **Example: DATEPART for Custom Start of Week**
    ```xml
        ...
          <date-function name='DATEPART' return-type='int'>
          <formula part='week'>CAST(FLOOR((7 + EXTRACT(DOY FROM %2) - 1 + (CAST(7 + EXTRACT(DOW FROM DATE_TRUNC(&apos;YEAR&apos;, %2)) - %3 AS BIGINT) % 7)) / 7) AS INTEGER)</formula>
          <argument type='localstr' />
          <argument type='datetime' />
          <argument type='localstr' />
        </date-function>
        ...
    ```

  **DATEPARSE function**
  The <span style="font-family: courier new">DATEPARSE</span> function is used to define which parts of your field are which parts of a date. It uses the <span style="font-family: courier new">icu-date-token-map</span> instead of the <span style="font-family: courier new">date-part-group</span> formula used primarily by the other date function. As a modifier for the date string to be converted into a date, it uses the <span style="font-family: courier new">date-literal-escape</span>.
  As an example, for the [DATEPARSE function](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/components/dialects/Annotated.tdd#L945) with arguments <span style="font-family: courier new">%1</span> and <span style="font-family: courier new">%2</span>,
  the string values for <span style="font-family: courier new">%1</span> are defined by [icu-token-map](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/components/dialects/Annotated.tdd#L1369) and the string values for <span style="font-family: courier new">%2</span> are defined by [date-literal-escape](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/components/dialects/Annotated.tdd#L1130).

  **Datetime considerations**
  When writing datetime functions, use the default date 1900-01-01 where appropriate to standardize with other Tableau connectors.

- __remove-function element__
The <span style="font-family: courier new">remove-function</span> is used to remove existing functions in a function map without overriding them. It requires only a <span style="font-family: courier new">name</span> attribute and doesn't require you to specify any <span style="font-family: courier new">formula</span>.

Each of the <span style="font-family: courier new">function</span>, <span style="font-family: courier new">date-function</span>, and <span style="font-family: courier new">remove-function</span> elements can contain the following:

- __formula element__
The <span style="font-family: courier new">formula</span> element is a required child of <span style="font-family: courier new">function</span> and <span style="font-family: courier new">date-function</span> elements and specifies the function's formula using standard Tableau string substitution syntax for arguments (%1, %2, etc.). You can use the optional <span style="font-family: courier new">part</span> attribute to specify a formula for a specific date part.

- __unagg-formula element__
The <span style="font-family: courier new">unagg-formula</span> (unaggregated formula) element is an optional child of <span style="font-family: courier new">function</span> elements. It should be specified *only* if the function is part of the aggregate group. Unaggregated formulas should represent a reasonable way of expressing the aggregate of a single value. For example, for average, it should be the value itself. For variance, it should be 0.

- __argument element__
The <span style="font-family: courier new">argument</span> element is an optional child of all three types of <span style="font-family: courier new">function</span> elements. It contains a single attribute, <span style="font-family: courier new">type</span>, which specifies the abbreviated argument type. Arguments must be listed in the correct order.
Allowable types: none, bool, real, int, str, datetime, date, localstr, null, error, any, tuple, spatial, localreal, localint.
Allowable date parts: year, quarter, month, dayofyear, day, weekday, week, hour, minute, second.

### Join Support:

 **Supported Joins** <br/>
  Some database does not support all types of join.`<supported-joins>` enumerates list of supported join types.

  ```xml
    ...
        <supported-joins>
          <part name='Inner' />
          <part name='Left' />
          <part name='Right' />
          <part name='Full' />
          <part name='Cross' />
        </supported-joins>
      </sql-format>
      </dialect>
    ...
```
**Format is distinct** <br/>
 `<format-is-distinct>` Defines a strategy for determining whether two values are distinct.  <br/>
 The value for this property can be:

  - __Keyword__
      Uses `DISTINCT` keyword for comparision. Logic: `(lhs IS [NOT ]DISTINCT FROM rhs)`.
  - __Operator__
    Uses `<=>` for comparions. Logic:`([NOT] (lhs <=> rhs))`
  - __Formula__
        By default formula is used. In this case format is distinct checks that the value for LHS and RHS is not null. Logic :`((lhs [!]= rhs) OR[AND] (lhs IS [NOT] NULL AND[OR] rhs IS [NOT] NULL))`
  - __NoNullCheck__
      Does not check that the value of LHS and RHS is null. Logic: `(lhs [!]= rhs)` . Note: A known limitation is that using this value will cause Tableau to give the wrong answer in some scenarios if the column contains null. This is not recommended unless required by the underlying database.

  ```xml
  <format-is-distinct value='Operator' />
  ```

  **Join Capabilities**  <br/>
  Join usage is also defined by capabilities in the manifest file. See the Query section for join relation capabilities [here]({{ site.baseurl }}/docs/capabilities).

  **Disable Join Modification** <br/>
  Tableau can modify join types to make queries faster. *If you use OLAP cubes for your database and want the same query as the one that is present in the cube follow this step to get the unoptimized queries:* <br/>
  In the "Data Source" page, "Data" menu, use the option to "Convert to Custom SQL". This will prevent Tableau from modifying the join type.

  **Data Blending** <br/>
  When using data blending, Tableau creates a left join between the primary and secondary datasource. Data blending can only be a LEFT join, which means the primary table should contain all possible values.

### Boolean Support:
  Some databases need to customize boolean support functions.  A common case is when a database lacks native boolean support. <br/>
  `format-true` and `format-false` are used in predicate statements. <br/>
   **format-true** <br/>
  ```xml
   <format-true value='(1=1)' />
  ```
  **format-false** <br/>
  ```xml
  <format-false value='(1=0)' />
  ```

**Note: Changes in Tableau 2020.3**

  With the release of Tableau 2020.3, `format-true` and `format-false` will have two parameters, literal and predicate. <br/>
  Literals is used when a boolean is used as a value. The default values are 1 and 0. <br/>
  Example usage: `SELECT 1 AS literalBool` <br/>
  Predicates is used when a boolean is used as a predicate. The default values are `(1=1)` and `(1=0)`. <br/>
  Example usage: `SELECT something AS test WHERE (1=1)` <br/>
  `value` attribute is used as `predicate` for backwards compatability <br/>
  Example:
  ```xml
    <format-true literal='TRUE' predicate='TRUE' />
  ```
  ```xml
    <format-false literal='FALSE' predicate='FALSE' />
  ```

   **format-bool-as-value** <br/>
    Used in CASE statements. Determines whether the true or false case is used first. The function is only used when the `CAP_QUERY_BOOLEXPR_TO_INTEXPR` capiblity is set to yes.
    The value for this property can be:
  - __TrueFirst__
      This is the default case. Logic: `CASE WHEN %1 THEN 1 WHEN NOT %1 THEN 0 ELSE NULL END`
  - __FalseFirst__
      False case is used first. Logic: `CASE WHEN NOT %1 THEN 0 WHEN %1 THEN 1 ELSE NULL END`

  ```xml
    <format-bool-as-value value='TrueFirst' />
  ```

 **Boolean Capabilities**  <br/>

  Boolean usage is also defined by capabilities in the manifest file. <br\>
  See the Query section for boolean capabilities [here]({{ site.baseurl }}/docs/capabilities) for more details.

 **TDVT Coverage**  <br/>
The following TDVT tests check that the boolean functionality is working as expected for a connector.
logical.bool	`exprtests\standard\setup.logical.bool.txt` and logical	`exprtests\standard\setup.logical.txt`. See [this](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/tdvt/exprtests/standard) for more details.

### String Literal Support
You have some control over what characters are escaped in string literals by changing the value of `format-string-literal`. `Standard` escapes only single quotes and is the default, `Extended` also escapes `\'`, `\\`, `\x0A`, `\x0D`, `\t`, `\b`, and `\f`

Example:
  ```xml
    <format-string-literal value='Standard'/>
  ```

**Unicode Prefix** <br/>
Some databases require a prefix for unicode literals. Starting in 2020.3, you can define a prefix for string literals takes another parameter called `unicode-prefix` that defines such a prefix.

Example:
 ```xml
   <format-string-literal value='Standard' unicode-prefix='_utf16' />
 ```

### Date Literal Support
Date and Datetime formatting elements take a formula, typically used to cast the string literal to a date type, and a date string format.

The `formula` attribute uses the token '%1' to insert the formatted date string. The `format` attribute describes the database's accepted string format for date literals, using [ICU Date/Time format syntax](https://unicode-org.github.io/icu/userguide/format_parse/datetime/#datetime-format-syntax).

Example:
  ```xml
    <format-date-literal formula="(DATE '%1')"  format='yyyy-MM-dd' />
    <format-datetime-literal formula="(TIMESTAMP '%1')" format='yyyy-MM-dd HH:mm:ss.SSS' />
 ```

### Temporary Table Support:
   **format-create-table** <br/>
  This function uses  piece-by-piece formulas for creating a table.
  Predicates can be used with tokens that only corresponds to a certain type of table.
  Predicates: <br/>
  -  __GlobalTemp__
  -  __LocalTemp__
  -  __AnyTemp__
  -  __NoTemp__ <br/>
   You should also be able to use the following string substitution tokens along with the predicate:
      - __%n - table name__
     - __%f - formatted column list__
    This function is available when the `CAP_CREATE_TEMP_TABLES` capability is set to yes.

  ```xml
    <format-create-table>
        <formula>CREATE </formula>
        <formula predicate='GlobalTemp'>GLOBAL </formula>
        <formula predicate='LocalTemp'>LOCAL </formula>
        <formula predicate='AnyTemp'>TEMPORARY </formula>
        <formula>TABLE %n (</formula>
        <formula>%f</formula>
        <formula>)</formula>
        <formula predicate='AnyTemp'> ON COMMIT PRESERVE ROWS</formula>
      </format-create-table>
  ```

  **format-select** <br/>
  This function uses a piece-by-piece formula for defining a SELECT statement. Here, we can define the clause used in `SELECT` statement. <br/>
  the `Into` clauses in the `SELECT` statement creates a new table. `<format-select>` will help you define how your TEMP table is created when using an `INTO` clause.
  `INTO` clause  is only available when the `CAP_SELECT_INTO` capability is set to yes.

  ```xml
      <format-select>
        <part name='Into' value='CREATE GLOBAL TEMPORARY TABLE %1 ON COMMIT PRESERVE ROWS AS' />
        <part name='Top' value='SELECT * FROM (' />
        <part name='Select' value='SELECT %1' />
        <part name='From' value='FROM %1' />
        <part name='Where' value='WHERE %1' />
        ...
      </format-select> />
  ```

  **format-drop-table** <br/>
    This function defines the format for dropping a table. %1 is the table name. Each formula is executed as a separate statement. <br/>
    This function is only used when `CAP_TEMP_TABLES_NOT_SESSION_SCOPED` capability is set to yes.
  ```xml
    <format-drop-table>
      <formula>TRUNCATE TABLE %1</formula>
      <formula>DROP TABLE %1</formula>
    </format-drop-table>
  ```

 **Temporary Table Capabilities**  <br/>

  Temporary table usage is also defined by capabilities in the manifest file.
  See the temp table capabilities [here]({{ site.baseurl }}/docs/capabilities) for more details.
