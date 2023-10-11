--
title: Testing Novel Tables With TDVT
--


## Testing Novel Tables
As of version 2.8.0, TDVT supports running a subset of tests against _any_ table, not just `Calcs` and `Staples`.

If you want to use TDVT to test your connector against a custom table, you are provided with two options:
1. **Connection Tests** - TDVT will generate a set of tests to `tdvt/exprtests/custom_tests` that enumerate each of the columns in your table.
2. **Expression Tests** - TDVT can attempt to generate and run suites of expression tests against your table. In order to do this, you will need to provide a `.json` file (described below) with data about your table's columns and choose which test suites you would like to run against your table. TDVT will then map the columns to columns in the [Calcs table](https://github.com/tableau/connector-plugin-sdk/blob/master/tests/datasets/TestV1/Calcs_headers.csv) to determine which expression tests can be run against it. TDVT uses strict matching to the `Calcs` columns; you can edit generated test cases to run against columns of your choosing if the strict matching disallows too many tests.

### Custom Table JSON File
To create custom tests, you need to create a json file that describes your table's columns. The json file should contain objects that each describes a column in your table. Note that the order of the keys describing the data in each column matters; they should be in alphabetic orer as below. The following is an example of a json file that describes a table with two columns:
```
    {
    "k": {
        "empties": false,
        "negatives": false,
        "nulls": false,
        "type": "VARCHAR"
        },
    "n0": {
        "empties": false,
        "negatives": true,
        "nulls": true,
        "type": "FLOAT"
        },
    "cool_column": {
        "empties": true,
        "negatives": true,
        "nulls": false,
        "type": "TIMESTAMP"
        },
    }
```


**Column Name**: Name of the column as in your `.tds` file.

**`type`**: Data type per Standard SQL data types. Types that can be matched with the `Calcs` table are:
- BOOLEAN
- DATE
- FLOAT
- INTEGER
- TIME
- TIMESTAMP
- VARCHAR

**`nulls` and `empties`**: Enter `true` or `false` for each of the following:

Data Shape | Description | Calcs Reference Column
-|-|-

`nulls` | Fields in the column may contain a null value. | [int1](https://github.com/tableau/connector-plugin-sdk/blob/master/tests/datasets/TestV1/Calcs_headers.csv)
`empties` | Fields in the column may contain no data (e.g. an empty string). | [datetime1](https://github.com/tableau/connector-plugin-sdk/blob/master/tests/datasets/TestV1/Calcs_headers.csv)

**`negatives`**: Does the column contain positive and negative values. (True/False)

For reference, a full mapping of Calcs columns to data shapes can be found in the TEST_ARGUMENT_DATA_TYPES constant in [tdvt/tdvt/constants.py](https://github.com/tableau/connector-plugin-sdk/blob/master/tdvt/tdvt/constants.py)

#### Custom Table Test Suites

Depending on the contents of your table, you can choose any number of the following optional test suites to run against your table. Below are the test groups and links to the test suites that can be run against your table. Some tests suites are excluded, often because they include tests hardcoded against data specific to the `Calcs` or `Staples` tables.

Test Group | Excluded Test Suites
-|-
[Agg](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.agg+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.agg.*.txt&type=code) | - None
[Cast](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.cast+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.cast.*.txt&type=code) | - None
[Date](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.date+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.date.*.txt&type=code) | - [date.dateadd](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.date.dateadd+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.date.dateadd.*.txt&type=code)<br /> - [date.datediff](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.date.datediff+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.date.datediff.*.txt&type=code)<br /> - [date.datename](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.date.datename+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.date.datename.*.txt&type=code)<br /> - [date.datepart](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.date.datepart+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.date.datepart.*.txt&type=code)<br /> - [date.datetrunc](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.date.datetrunc+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.date.datetrunc.*.txt&type=code)<br />
[Math](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.math+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.math.*.txt&type=code) | - None
[Operator](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.operator+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.operator.*.txt&type=code) | - [operator.str](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.operator.str+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.operator.str*.txt&type=code)<br />
[String](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.string+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.string.*.txt&type=code) | - [string.contains](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.string.contains+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.string.contains.*txt&type=code)<br /> - [string.endswith](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.string.endswith+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.string.endswith.*txt&type=code)<br /> - [string.find](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.string.find+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.string.find.*txt&type=code)<br /> - [string.space](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.string.space+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.string.space.*txt&type=code)<br /> - [string.startswith](https://github.com/search?q=repo%3Atableau%2Fconnector-plugin-sdk+setup.string.startswith+path%3Atdvt%2Ftdvt%2Fexprtests%2Fstandard%2Fsetup.string.startswith.*txt&type=code)<br />

TDVT carries out strict one-to-one matching of columns. This means that some tests may be excluded even though they could run. After tests are generated, **check the `setup.{test name}.txt` files in `tdvt/exprtests/custom_tests` to see if any excluded tests include function you believe can run against your  table**. You can point them to the desired column name, run tests, and then look at the expected file created to validate the results.
