---
title: Create a Tableau Dialect Definition File 
---

A Tableau Dialect Definition file (.tdd) maps Tableau's query language to a database’s SQL. This is an XML file with a .tdd filename extension, and is one of the main components of a Tableau connector. 

YOu should create a dialect definition file whenever you need to make changes to an existing Tableau dialect or define an entirely new dialect. If your connector uses the same SQL dialect as the connector it’s based on, such as PostgreSQL, then a new  TDD file isn't necessary. 

Create a TDD file 

To get started quickly, you can copy the sample dialect.tdd file from the [postgres_odbc or postgres_jdbc folder](https://github.com/tableau/connector-plugin-sdk/tree/master/samples/plugins) and use the copy to make your modifications. 

For an example of the XML schema for the TDD file format, see the [sample XSD file](https://github.com/tableau/connector-plugin-sdk/blob/master/validation/tdd_latest.xsd).

Tableau searches for a TDD file in the location specified by the connector manifest XML file. The TDD format breaks down as follows: 

### Dialect tag

The <span file-format="Courier">dialect</span> tag serves as the root for the document. It has several required attributes and a couple of optional ones. 

Attribute | Required | Description 
-|-|- 
name | Y | Dialect name. Used for dependency lookup. 
class | Y | Indicates the datasource class whose dialect you'd like to modify, for example "sqlserver", "postgres", or "genericodbc". 
base | N | Specifies a base dialect to build upon. If a certain property or function isn't defined in a dialect definition file, the connector will fall back to its base dialect's behavior if a base is defined, and SQL-92 default behavior if there is no base. **Important:** This must be a valid, existing dialect. If the specified base does not exist, the connector will fail to load. For a list of bases, see [Dialect base classes]({{ site.baseurl }}/docs/design#dialect-base-classes). 
dialect-version | N | Indicates the minimum database version the TDD file applies to. For example, if you're adding a function definition that wasn't implemented until FooDB 3.0, then set dialect-version='3.0'. 
version | Y | Must match the current Tableau version in the format YY.Q, for example, "19.2". 


### Supported Aggregations 

The *supported-aggregations* element contains a list of aggregations and date truncation levels supported by the database, represented by one or more *aggregation* elements. 

### Aggregation 

An *aggregation* element has one required attribute, *value*, which specifies a single aggregation or truncation. For a list, see [supported aggregations](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/components/dialects/Annotated.tdd#L1051). 

### Function Map 

The *function-map* element has no attributes and contains any number of *function*, *date-function*, and *remove-function* elements. 

### Function 

*function* elements represent a function definition. They have a few required attributes, contain a *formula* element (and in some cases, an unagg-formula element) and any number of argument elements. For a list of supported functions, see the [full_dialect.tdd](https://github.com/tableau/connector-plugin-sdk/blob/master/samples/components/dialects/full_dialect.tdd) file sample. 

 

Attribute | Required | Description 
-|-|-
name | Y | Indicates the name of the function being added or overridden. Remember, just because a function is present in a dialect doesn't mean that our calculated field expression parser will recognize it. 
group | Y | Contains one or more (comma-separated) groups this function belongs to. Allowable types: aggregate, cast, date, logical, numeric, operator, passthru, special, string, system 
return-type | Y | Indicates the return type of the function. Allowable types: see [Argument](#Argument) 

### Date Function 

*date-function* elements are a specialized variant of function. In addition to the base formula, you can specify one or more datepart formulas, which are used instead of the generic formula when available. 
The function *name* must be one of DATEADD, DATEDIFF, DATEFORMAT, DATENAME, DATEPARSE, DATEPART, DATETRUNC.

Like *function*, *date-function* requires name and return-type, but unlike *function*, group is not required. 

### Remove Function 

*remove-function* is used to remove existing functions in a function map without overriding them. It only requires a *name* attribute and doesn't require you to specify any *formula*. 

### Formula 

The *formula* element is a required child of *function* and *date-function* elements and specifies the function's formula using standard Tableau string substitution syntax for arguments (%1, %2, etc.). You can use the optional *part* attribute to specify a formula for a specific date part. 

### Unagg Formula 

The *unagg-formula* (unaggregated formula) element is an optional child of *function* elements. It should be specified if and only if the function is part of the aggregate group. Unaggregated formulas should represent a reasonable way of expressing the aggregate of a single value. For example, for average, it should be the value itself. For variance, it should be 0. 

### Argument 

The *argument* element is an optional child of all three types of function elements. It contains a single attribute, *type*, which specifies the abbreviated argument type. Arguments must be listed in the correct order. 

Allowable types: none, bool, real, int, str, datetime, date, localstr, null, error, any, tuple, spatial, localreal, localint 

Allowable date parts: year, quarter, month, dayofyear, day, weekday, week, hour, minute, second 

