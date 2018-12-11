---
title: Test Your Connector Plugin
---

## Use Tableau Datasource Verification Tool (TDVT) to test

TDVT is an automated testing tool for testing Tableau connectivity with a database. 
Tests span from simple expressions to complex SQL.
When evaluating the connection to your database, use a named connector if one exists. 
Named connectors are optimized connections and provide a faster, cleaner experience for customers.

If a named connector doesn't exist, you can connect through the Other Databases (ODBC) connector. 
For information on the Other Databases (ODBC), check out the [online Help](https://onlinehelp.tableau.com/current/pro/desktop/en-us/examples_otherdatabases.htm). 

Or you can create a connector plugin, as described in this Developer Guide.

We recommend running TDVT for:

- New Driver Releases
- Database Patches
- Database Releases
- Connector Plugins

## What’s in this section?

This section shows you how to set up and configure TDVT, add configurations for your own data source, and run tests.
We use Postgres as an example in this section, but you can use your own data source to follow along.

Test Scope

- Ability to connect to your database
- Support for all Tableau calculations (see below)
- Support for simple queries
- Support for complex queries

![]({{ site.baseurl }}/assets/tdvt_expression_dialog.png)

### Requirements

- PC or VM running Windows or macOS.
- Python 3.3. Pip is required as well but should come by default with the Python installation. Ensure that you check "install environmental variables".
- An ODBC or JDBC driver for your database.
- The 'Calcs' and 'Staples' table loaded in your database.

## How it works

TDVT consists of Python scripts that create a test framework around tabquerytool.exe, a command line tool that leverages Tableau's data connectivity layer.
The inputs are an expression test file or a logical query and a TDS file.
The outputs are rows of data returned from the database after executing the query.

Expression tests are text files that contain Tableau calculation language expressions (in other words, anything you can type into an Edit Calculation dialog).
These expressions are parsed and compiled as individual queries.

Logical query tests are intermediate, abstract query representations.
These are parsed and run like the expression tests.

For each test suite the TDVT script calls tabquerytool.exe to run the queries and then compares the results to expected files.
Multiple expected files are supported.

## Installation

1. Clone the [TDVT Python module](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt). You can create an archive package and install that, or install from the live directory if you want to modify TDVT. Run the following commands from the top level 'tdvt' directory.
    - Create an archive package: `py -3 setup.py sdist --formats gztar`
    - Install from an archive file: `py -3 -m pip install tdvt-1.1.59.zip`.
    - Alternatively, install the live version: `py -3 -m pip install -e .`
    - Verify it is installed by running `py -3 -m pip list`.

1. Extract and then load the TestV1 minimal dataset into your database.

1. If it's not already installed, install Tableau Desktop which includes the tabquerytool needed to run the tests.

1. Setup your TDVT workspace. When you run TDVT it looks in the current working directory for the test configuration files which setup test suites for your datasource. Follow these steps to setup TDVT for the included sample datasources, or you can run `py -3 -m tdvt.tdvt --setup` to create an empty environment.
    - create a new directory, for example 'tdvt_workspace'.
    - copy the contents of connector-plugin-sdk/tdvt/samples to tdvt_workspace.
    - copy the connector-plugin-sdk/samples/plugins folder to tdvt_workspace.
    - tdvt_workspace should contain the following subdirectories: config, plugins, tds.

1. Edit config/tdvt/tdvt_override.ini and set the path to tabquerytool.
   - For example: `TAB_CLI_EXE_X64 = C:\Program Files\Tableau\Tableau 1234.1\bin\tabquerytool.exe`

## Notes on loading TestV1

See [Postgres Example](https://github.com/tableau/connector-plugin-sdk/tree/master/tests/datasets/TestV1/postgres/README.md) for instructions on loading TestV1 to a local Postgres database.
See the section below about troubleshooting Boolean values if your database does not have a native Boolean type.

There is a 'StaplesData' test and a 'calcs_data' test that retrieve every value from the table and compare it to an expected value.
This can help ensure the data is loaded correctly with the right data types.

## Notes on invoking TDVT

When TDVT is installed as a Python module it can be invoked as follows:
`python -m tdvt.tdvt`. 

If you have Python 2 and Python 3 installed, run `py -3 -m tdvt.tdvt`. This ensures Python 3 is used. In the examples below `tdvt` is used, but one of the above would be used in actual practice.

TDVT looks for the necessary config and setup files relative to the current working directory.
Always run TDVT commands from the top level directory of your generated folder structure.
Use double quotes to wrap arguments that contain spaces.

`tdvt --generate` is used to update some config files.
You need to run it if you add a new datasource or change your mydb.ini file.

## Add a new datasource

First, decide on a name for your new datasource.
This TDVT config name will be used to name configuration files and will be the argument you use to invoke TDVT.
We'll use 'mydb' as an example.

Next, you need two Tableau Data Source files (.tds).
These represent saved connection information to a particular table in your database.
TDVT uses the 'Calcs' and 'Staples' tables.

1. Start Tableau Desktop and connect to the 'Calcs' table using 'Other Database (ODBC)'.
   After you connect, right-click the datasource in the top left 'Data' tab and select 'Add to Saved Datasources'.
   Save this in the 'tdvt/tds' directory.
   Name this file 'cast_calcs.\*.tds' or 'Staples.\*.tds' where \* represents your TDVT config name.
   For example 'cast_calcs.mydb.tds'.

   ![]({{ site.baseurl }}/assets/tdvt_connection_1.png)

   ![]({{ site.baseurl }}/assets/tdvt_connection_2.png)

1. Open the TDS file in a text editor and embed the password in the <connection> tag of the TDS file next to the existing 'username' value.
   Save the file.

1. Repeat this for the 'Staples' table.

1. Run `tdvt --add_ds mydb`. This wil create a mydb.ini file under /config and will modify your two TDS files to rename the connection.

1. Update the generated ini file (mydb.ini) and choose a logical query config that matches what your database supports. 
   See the section below titled 'Choose a logical query config'.
   
1. Run: `tdvt --generate`

1. Verify your new test suite by running: `tdvt --list your_datasource_name`. It should show you a list of test suites associated with this datasource.

The `add_ds` command renames the connection names to 'leaf'.
See one of the TDS files in '/tds' for an example.
This occurs in two places, `<named-connection name='leaf'> and <relation connection='leaf' >`.
If this is not done, the logical query tests might cause tabquery crashes or application exceptions.

The mydb.ini file names the test suite and specifies which tests to run.
The `Name` section of the .ini file is used to find your TDS files.
For example, if you set `Name = mydb` then your TDS files should be named `cast_calcs.mydb.tds` and `Staples.mydb.tds`.

Now you can run the tests using `tdvt --run mydb`

TDC files are also supported through the Tableau Repository.

## Choose a logical query config

1. Open the Staples TDS file in a text editor and look for the relation XML tag. For example: `<relation connection='leaf' name='Calcs' table='[dbo].[Calcs]'>`

1. Note the value for 'table', in this case '[dbo].[Calcs]'.

1. Run: `tdvt --list_logical_configs`

   This prints all the logical query versions and some information about how they map things.
   Search the output of the command for something that matches '[dbo].[Calcs]'.

   A selection of the output:

   ```
   Name = dbo
   Calcs = [dbo].[Calcs]
   Staples = [dbo].[Staples]
   Camel Case = [Camel Case]
   bool0 = [bool0]
   Date = [Date]
   ```

The Calcs value should match what you found in step 3.
There are also mappings for some column names in case your database doesn't support the names as provided in the Calcs and Staples data files.
For example, some databases may not support spaces in identifiers, in which case you can look for a logical configuration that replaces them with underscores and name the columns in your table accordingly.

1. In this case the logical configuration named 'dbo' matches.

1. Note the Name of the logical configuration and add this line to your INI file under the [Datasource] heading: LogicalQueryFormat = dbo

1. Run: `tdvt --generate`

If none of the logical configurations work for your datasource, then you can create your own in the .ini file. See the following section.

## INI file structure

```ini
[Datasource]

Name = your_datasource_name  #i.e. mydb

CommandLineOverride = -DLogLevel=Debug #Space separated list of arguments that are passed through unchanged to tabquerytool. Most Tableau arguments require a prepended '-D'.
#If you are testing a connector plugin, be sure to add the command line argument -DConnectPluginsPath and have it pointed at the folder where your plugin is located

MaxThread = 6   #You can add this to control Max Thread number when you use TDVT to run single datasource, it cannot apply with multi datasource

LogicalQueryFormat = dbo

#You can add a new logical config here and use it above. These are example attributes; you wouldn't set them all since some are mutually exclusive.

[LogicalConfig]
Name = my_logical_query
tablename = SomePreix_$dsName #$dsName will be substituted with Calcs or Staples.
tablePrefix = [MySchema].
tablePostfix = [MySchema].
tablenameUpper = True
tablenameLower = True
boolUnderscore = True
fieldnameDate_underscore = True
fieldnameLower = True
fieldnameUpper = True
fieldnameNoSpace = True
fieldnameLower_underscore = True
fieldnameUnderscoreNotSpace = True


[StandardTests]

#You can put in comma-separated string values that match part or all of a test name to exclude them. The asterisk works as a wildcard.

LogicalExclusions_Calcs = string.right

LogicalExclusions_Staples = Filter.Trademark

ExpressionExclusions_Standard = string.ascii,string.char,logical

#If you remove this section then your test sute will not include the Level of Detail tests.

[LODTests]

#You don't need to specify anything to add this test suite, but you can exclude tests here, too:

LogicalExclusions_Staples =

ExpressionExclusions_Calcs =

#This test will verify that your Staples table is loaded correctly.

[StaplesDataTest]

#Recommended INI file for full test coverage:

[StandardTests]

[StaplesDataTest]

[LODTests]

[UnionTest]

#Advanced:
#You can add a new arbitrary test suite like this.

[SomeTests] #This is just a section header defining the test.

Type = expression #expression or logical.

Name = expression_test1. #This name should be unique among test suites.

TDS = cast_calcs.bigquery_sql_dates2.tds

Exclusions = string.ascii

TestPath = tests/mytests/ #This could point to a local directory relative to your TDVT working directory named 'tests'. Or for a logicaltest it would be 'tests/logical/setup/mytests/setup.\.xml

```

## Run tests

Try `tdvt -h` for the latest usage information.

Run TDVT from your working directory since it will need the TDS and INI files you created when adding your datasource.

To show the registered datasources and suites, run: `tdvt --list`

To run a test:
`tdvt --run postgres_generic_example`

To run expression tests:
`tdvt --run postgres_generic_example -e`

To run logical query tests:
`tdvt --run postgres_generic_example -q`

Test results are available in a CSV file called test_results_combined.
Try loading them in Tableau Desktop to visualize the results.

## Test the sample plugins

1. Copy the samples/plugins folder to your working directory so that they exist under /plugins. Like this: /plugins/postgres_odbc/manifest.xml 

2. Check that everything is set up correctly and a list of tests displays: `tdvt --list postgres_odbc`

## Review results

After the tests have run, you see a “test_results_combined.csv” spreadsheet.
This contains the data about the test passes and failure from the previous run.
TDVT includes a sample Tableau workbook that will help you analyze the results of this file.

You can use these steps as a guide to develop your own workbook.

1. Open the file called "Example Postgres Calc Test Result.twbx", or start Tableau and connect to 'Text File'.

1. Navigate to the "Data Source" tab.

1. Click the "test_results" connection on the left, and click "Edit Connection".

   ![]({{ site.baseurl }}/assets/tdvt_edit_results.png)
   
1. In the file navigator that opens, choose the "test_results_combined" spreadsheet that is in your "tdvt" folder.

1. Drag  the new "test_results_combined.csv" file to replace the old file in the data canvas.

1. Right-click the new table, and click "Text File Properties…".

   ![]({{ site.baseurl }}/assets/tdvt_edit_results2.png)
   
1. Change the "text qualifier" to use a double quote.

1. View the viz by clicking "Functional Test Pass," which should look like the information below. The viz shows the test pass rate by Test Category. Click the bars to see the relevant failed tests in the "Test Details" section.

   ![]({{ site.baseurl }}/assets/tdvt_edit_results3.png)

## File structure

Your working directory looks like this:

**/config** - INI files that configure test suites.

**/config/registry** - You can create more elaborate groups of test suite here.

**/config/tdvt/tdvt_override.ini** - You can specify the path to tabquerytool here.

**/tds** - TDS files.

**/** - TDVT log file, output CSV and JSON files, a zip file containing any test results that don't match the expected results.

## TDC files and logging

TDC files are supported either in the My Tableau Repository, or embedded in the TDS file.
Tableau Desktop style logs are found in your My Tableau Repository.
TDVT logs are found in the main TDVT directory.

## Output

**tdvt_actuals.zip** - Zipped actual files from a test run. These are test results that did not match any expected files.

**tdvt_log.txt** - Verbose logging from TDVT.

**tdvt_output.json** - JSON output of test results. Suitable for re-running failed tests. See tdvt --help.

**tdvt_results.csv** - Tableau-friendly result file. Load with a double quote text qualifier.

The above files have versions named _\_combined._, such as tdvt_log_combined.txt. This indicates the file contains combined results from several test suites.

## Architecture

Each datasource has an associated collection of test suites defined in the mydb.ini file.
You can see these by running `tdvt --list mydb`.

When you invoke `tdvt --run mydb` each test suite runs on it's own thread.
Each test suite can consist of one or more tests, and each test can consist of one of more test cases.

The test suite spawns a number of worker threads to run these tests in parallel.
Each worker thread invokes 'tabquerytool' to run the entire suite of tests.

The tabquery process compiles the test into SQL, runs it against your database, and saves a result file.
TDVT then compares these result files to the expected result file.

After all test suites have finished, TDVT compiles the results into a CSV file.
The CSV file contains information such as the test name, a 'passed' indicator, the generated SQL and the data (tuples) that came back from the database.
It also indicates which expected file most closely matched the actual results from the query.

### Expected files

The expected files are located in the TDVT Python package location.
You can find this by running `python -m pip show tdvt`.

Expression tests have a name like 'setup.agg.avg.txt' and a corresponding expected file like 'expected.setup.agg.avg.txt'.
There may be optional alternative expecteds like 'expected.setup.agg.avg.1.txt' and so on.
The expected files are located in 'exprtests/' in the TDVT package directory.

Logical tests have names like 'setup.Filter.slicing_Q_date_month_instance_filter.prefix_bool\_.xml'.
The last section of the name 'prefix_bool\_' corresponds to the name of the logical query config from your mydb.ini file.
These various permutations do not affect the test results so the expected file has a base name like 'expected.setup.Filter.slicing_Q_date_month_instance_filter.xml'. The expected files are located in 'logicaltests/expected' in the TDVT package directory.

## Frequently found issues and troubleshooting

### All my tests are failing!

1. Check the TDS file: Open the TDS file in Tableau.
   Check to see if Tableau shows any error messages, prompts for a username and password, or asks for any additional information fix that's in the TDS file.
   You should be able to open the TDS and create a viz without any prompts.
   
1. Check the INI file for the following line: CommandLineOverride = -DLogLevel=Debug -DConnectPluginsPath=[PathToPluginsFolder].
   Make sure that the DConnectPluginsPath attribute is present and correct.
   
1. Check Python Version: If you are using both Python 2.x and Python 3, then run TDVT using the command: py -3 tdvt.py …
   
1. Check tabquerytool.exe: This file should be placed in your Tableau bin directory and tdvt/config/tdvt_override.ini should be updated to point at that executable.

### Boolean data types are not recognized or your database doesn't support them

Sometimes you may need to rename a column in the TDS file.
For example the database may integer columns instead of Booleans for the **bool0**, **bool1**, **bool2**, and **bool3** columns.
In this case you would want to load the table into your database using integer columns named **bool0\_** (a trailing underscore) etc.
You can re-map these in the TDS file by adding a column definition like this:

```xml
  <column datatype='boolean' name='[bool0]' role='dimension' type='nominal'>
    <calculation class='tableau' formula='[bool0_]!=0' />
  </column>
  <column datatype='boolean' name='[bool1]' role='dimension' type='nominal'>
    <calculation class='tableau' formula='[bool1_]!=0' />
  </column>
  <column datatype='boolean' name='[bool2]' role='dimension' type='nominal'>
    <calculation class='tableau' formula='[bool2_]!=0' />
  </column>
  <column datatype='boolean' name='[bool3]' role='dimension' type='nominal'>
    <calculation class='tableau' formula='[bool3_]!=0' />
  </column>
```

![]({{ site.baseurl }}/assets/tdvt_edit_tds_columns.png)

### Troubleshoot test failures

First ensure that the data is loaded correctly.
Incorrect data can cause many test failures.

The standard test suite include a test named 'calcs_data' that contains several test cases, one for each column in the table.
This test and all test cases must pass first before further troubleshooting.

There is a similar test for the Staples table but you must add it manually to your mydb.ini file by adding '[StaplesDataTest]'.
This test works like the 'calcs_data' test but since Staples contains several UTF-8 characters it is difficult to get it to pass completely.
Some of the logical tests filter one these UTF-8 characters but you can get 100% pass rate even if the StaplesDataTest does not pass.
Still it can be useful for tracking down data issues.

It can be insightful to load the Calcs and Staples tables on a Postgres or MySQL server and run the tests in order to compare working SQL against what TDVT is generating for your database.
Just add a new datasource to TDVT that uses the native connector for that database.
Do not use the Other Databases (ODBC) connector in this case.
These tests should pass completely for these datasources.

### Check your setup

Make sure the TDS files include the 'password' element and that you have renamed the relations to 'leaf' as indicated in the setup instructions.

### Log Files

tdvt_log\*.txt contains '--verbose' level logging.
It can help to either run a single test or to run things in serial with '-t 1 -tt 1' otherwise the log file will be interleaved by different sub threads.
tabquerytool writes log files to your 'My Tableau Repository'.
These can be useful if it isn't clear what is causing a test to fail.

### Actual does not match expected

This means that your database returned results that do not match any expected files for that test.
One common problem is precision errors for floating point values, although the test framework imposes some rounding to standardize results.
If the error is not significant then you can either skip the test or add a new expected file.

Another problem invloves various date functions that might be off by a day.
These can be caused by start of week errors (Sunday should be 1 and Saturday is 7).
Other causes might include discrepancies around some start of week calculations or quarter boundaries.

### Invalid expression

This kind of error indicates that Tableau was unable to generate SQL for the test case.
Usually it means that Tableau queried the driver to see what ODBC functions are supported but a necessary function or cast/convert was not found.
Tuning the TDC file can sometimes fix these although it is a difficult process.

### An ODBC error from your database

If Tableau generates SQL that doesn't work against your database, the easiest fix is to note what will work.
These custom functions can be added during development work for a new connector.
TDC files can sometimes help, too.

### No generated SQL

This can mean that Tableau was unable to find the functions necessary (see above).
Sometimes Tableau was able to run some SQL but it wasn't reported to TDVT.
In that case you can inspect the Tableau log files for that test.
It's helpful to clear the log files and then run just the single failing test. See 'tdvt --help' for more details.

### Logical Query Tests

If all the logical queries fail it can mean that you don't have the right logical query config associated in your mydb.ini file.
