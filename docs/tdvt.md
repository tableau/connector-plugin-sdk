---
title: Test with TDVT Suite
---

Tableau provides an automated testing tool called the Tableau Data source Verification Tool, or TDVT, to test Tableau connectivity with a database. TDVT runs tests that range from simple expressions to complex SQL.

#### Check out our step-by-step guide to using TDVT:
{% include youtubePlayer.html id="rAgnnByJIJA" %}

When evaluating the connection to your database, use a named connector if one exists.
Named connectors are optimized connections and provide a faster, cleaner experience for customers.

If a named connector doesn't exist, you can connect through the Other Databases (ODBC) connector.
For information on the Other Databases (ODBC), see [Tableau Help](https://onlinehelp.tableau.com/current/pro/desktop/en-us/examples_otherdatabases.htm).

Or you can use TDVT to test a connector you created, as described in this *Tableau Connector SDK*.

We recommend running TDVT each time you do one of these things:

- Release a new driver
- Release a database
- Add or modify a connector


## Set up and configure TDVT

In this section, we'll use Postgres as an example tp describe the setup and configuration steps you can use your own data source.

The TDVT tests for these things:

- Ability to connect to your database
- Support for all Tableau calculations (see below)
- Support for simple queries
- Support for complex queries

![]({{ site.baseurl }}/assets/tdvt_expression_dialog.png)


## How TDVT works

TDVT consists of Python scripts that create a test framework around tabquerytool.exe, a command-line tool that leverages Tableau's data connectivity layer.

Inputs come from a TDS file, and either a logical query or an expression test file.
Expression tests are text files that contain Tableau calculation language expressions (that is, anything you can type into an __Edit Calculation__ dialog).
These expressions are parsed and compiled as individual queries.

Outputs for TDVT are rows of data returned from the database after executing the query.

Logical query tests are intermediate, abstract query representations.
These are parsed and run like the expression tests.

For each test suite, the TDVT script calls tabquerytool.exe to run the queries, and then compares the results to expected files.
Multiple expected files are supported.

## Set up

1. Be sure your system includes these prerequisites:
    - PC or VM running Windows or macOS.
    - Tableau Desktop installed
    - Python 3.7 (See: [Windows releases](https://www.python.org/downloads/windows/) / [Mac releases](https://www.python.org/downloads/mac-osx/))
    - Pip (by default comes by with the Python installation)
      Be sure to enable the "install environmental variables" option.
    - An ODBC or JDBC driver for your database.
    - The Calcs and Staples table loaded in your database.
1. Clone the [TDVT Python module](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt).
You can create an archive package and install that, or install from the live directory if you want to modify TDVT. Run the following commands from the top level "tdvt" directory.
    - Create an archive package in the dist folder:
`py -3 setup.py sdist --formats gztar`
    - Change directory to dist and install from the archived file:
`py -3 -m pip install tdvt-1.1.59.zip`
   __Note:__ Instead of A and B, you can install the live version:
    `py -3 -m pip install -e .`
    - Verify it is installed:
 `py -3 -m pip list`

1. Extract and then load the [TestV1 dataset](https://github.com/tableau/connector-plugin-sdk/tree/master/tests/datasets/TestV1) into your database.
__Notes:__
    - See [Postgres Example](https://github.com/tableau/connector-plugin-sdk/tree/master/tests/datasets/TestV1/postgres/README.md) for an example of loading data into a database
    - See the following section about troubleshooting Boolean values if your database doesn’t have a native Boolean type.
    - Make sure that empty values are treated as nulls. This may not be the default for your database.
    - You can run the tests named StaplesData and calcs_data to retrieve every value from the table and compare it to an expected value. This helps ensure the data is loaded correctly with the right data types.

1. If it's not already installed, install Tableau Desktop. Tableau Desktop includes the tabquerytool needed to run the tests.

2. Set up your TDVT workspace.
TDVT checks the current working directory for the test configuration files that set up test suites for your data source.
    - Run these steps to set up TDVT with a sample data source:
        1. Create a new directory, for example:
    `tdvt_workspace`
        1. Copy the contents of connector-plugin-sdk/tdvt/samples to tdvt_workspace.
        1. Copy the connector-plugin-sdk/samples/plugins folder to tdvt_workspace.
Note that tdvt_workspace should contain the following subdirectories: config, plugins, tds.
    - Or,  run this command to set up TDVT with an empty environment:
`py -3 -m tdvt.tdvt action --setup`

1. Edit config/tdvt/tdvt_override.ini and set the path to tabquerytool.
   For example:
   `TAB_CLI_EXE_X64 = C:\Program Files\Tableau\Tableau 1234.1\bin\tabquerytool.exe`



## About running TDVT

- When TDVT is installed as a Python module, invoke it as follows:
`python -m tdvt.tdvt`
- Make sure you're using the correctly using Python 3 if you have multiple versions of python installed.
- TDVT makes searches relative to the current working directory to find the config and setup files it needs.
- Always run TDVT commands from the top-level directory of your generated folder structure.
- Use double quotes to wrap arguments that contain spaces.

`tdvt run mydb --generate` is used to update some config files.
You need to run it if you add a new data source or change your mydb.ini file.

## Test a new data source

To test a new data source, you must first choose a name. This name is used as the TDVT config name, the data source name, and as an argument to invoke TDVT. In examples below, we use "mydb" as the data source name.

Next, you need two Tableau Data Source files (.tds).
These represent saved connection information to a particular table in your database.
TDVT uses the Calcs and Staples tables.

__To test a new data source__

1. Start Tableau Desktop and choose the connector you want to test.
1. Drag the Calcs table ato the work area.
1. Navigate to the worksheet, right-click the data source in the top left Data tab and select _Add to Saved Data Sources_.
    - Save this data source in the tdvt/tds directory.
    - Name this file "cast_calcs.\*.tds" or "Staples.\*.tds", replacing  "\*" with your TDVT config name.
   For example, "cast_calcs.mydb.tds".

   ![]({{ site.baseurl }}/assets/tdvt_connection_1.png)

   ![]({{ site.baseurl }}/assets/tdvt_connection_2.png)

1. Run `tdvt action --add_ds mydb`.
Choose to generate the password file and choose the logical query config. This creates a mydb.ini file under /config and will modify your two TDS files to rename the connection and link them to the tds/mydb.password password file.

1. Edit the generated tds/mydb.password file and enter the password for your connection. If your connection needs multiple fields for authentication such as OAuth tokens, pass them in a json string like this: {"ACCESSTOKEN" : "your_access_token", "REFRESHTOKEN" : "your_refresh_token"}. You can obtain "your_access_token" and "your_refresh_token" from any third-party tool to retrieve OAuth tokens such as Postman.
__Note:__ This can also be done manually. See [The Sample TDS Files](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/samples/tds).

1. Verify your new test suite by running:
`tdvt list --ds mydb`.
It should show you a list of test suites associated with this data source.

### About your test suite
- The `add_ds` command renames the connection names to "leaf".
See one of the TDS files in  "/tds' for an example.
- This occurs in two places, `<named-connection name='leaf'>` and `<relation connection='leaf' >`.
If this is not done, the logical query tests might cause tabquery crashes or application exceptions.
- The mydb.ini file names the test suite and specifies which tests to run.
The <span style="font-family: courier new">Name</span> section of the .ini file is used to find your TDS files.
For example, if you set <span style="font-family: courier new">Name = mydb</span> then your TDS files should be named <span style="font-family: courier new">cast_calcs.mydb.tds</span> and <span style="font-family: courier new">Staples.mydb.tds</span>.

- Now you can run the tests using this command:
`tdvt run mydb`

- TDC files are also supported through the Tableau Repository.

## Choose a logical query config

1. Open the Staples TDS file in a text editor and look for the relation XML tag. For example:
`<relation connection='leaf' name='Calcs' table='[dbo].[Calcs]'>`

1. Note the value for "table", in this case "[dbo].[Calcs]".

1. Run this command:
`tdvt list-logical-configs`
   This prints all the logical query versions and some information about how they map things.
   Search the output of the command for something that matches "[dbo].[Calcs]".
This is a selection of the output:
   ```
   Name = dbo
   Calcs = [dbo].[Calcs]
   Staples = [dbo].[Staples]
   Camel Case = [Camel Case]
   bool0 = [bool0]
   Date = [Date]
   ```
1. Note the Name of the logical configuration and add this line to your INI file under the [Datasource] heading: <span style="font-family: courier new">LogicalQueryFormat = dbo</span>

1. Run this command:
`tdvt run mydb --generate`

__Notes:__
   - The Calcs value should match what you found in step 3.
There are also mappings for some column names in case your database doesn't support the names as provided in the Calcs and Staples data files.
For example, some databases may not support spaces in identifiers, in which case you can look for a logical configuration that replaces them with underscores and name the columns in your table accordingly.
- In this case, the logical configuration named "dbo" matches.
- If none of the logical configurations work for your data source, then you can create your own in the .ini file. See the following section.

## INI file structure
Your mydb.ini file will define your new TDVT test suite, and has the following sections.

### [Datasource]
This section is required, and defines the basic information of the TDVT suite.

Option | Example Value | Default | Description | Required?
-|-|-|-|-
Name | mydb | N/A | Your data source name | Yes
CommandLineOverride | -DLogLevel=Debug | N/A | Space separated list of arguments that are passed through unchanged to tabquerytool | No
MaxThread | 6 | 6 | Controls maximum number of threads to a single data source. Does not apply when running TDVT with multiple data sources | No
TimeoutSeconds | 6000 | 3600 | Controls how long it takes for | No
LogicalQueryFormat | bool_lower | N/A | The logical query we use | Yes

### LogicalConfig
This section is optional, and allows you to define your own logical query config if the existing ones do not work for your database. Some options are mutually exclusive.

Option | Example Value | Default | Description | Required?
-|-|-|-|-
Name | my_logical_query | N/A | Name of your logical query | Yes
tablename | SomePrefix_$dsName | N/A | The name of the table. $dsName will be substituted with Calcs or Staples. | No
tablePrefix | [MySchema]. | N/A | Prefix that is appended to the table name | No
tablePostfix | [MySchema]. | N/A | Postfix that is appended to the table name | No
tablenameUpper | True | N/A | Set to true if the table name is all uppercase | No
tablenameLower | True | N/A | Set to true if the table name is all lowercase | No
bool_underscore | True | N/A | Set to true if the bool column name has underscores | No
fieldnameDate_underscore | True | N/A | Set to true if the date column name has underscores | No
fieldnameUpper | True | N/A | Set to true if the column names are all uppercase | No
fieldnameLower | True | N/A | Set to true if the column names are all lowercase  | No
fieldnameNoSpace | True | N/A | Set to true if the column names have no spaces | No
fieldnameLower_underscore | True | N/A | Set to true if the column names have underscores and are all lowercase | No
fieldnameUnderscoreNotSpace | True | N/A | Set to true if the column names replace spaces with underscores | No
fieldnamePostfix | SomePostfix | N/A | Postfix that is applied to every column name | No

### [StandardTests]
This is required to run the standard tests.

This section also allows you to skip tests by excluding them. You can put in comma-separated string values that match part or all of a test name to exclude them. The asterisk works as a wildcard.

Option | Example Value | Default | Description | Required?
-|-|-|-|-
LogicalExclusions_Calcs | string.right | N/A | Exclude logical tests that target the Calcs table | No
LogicalExclusions_Staples | Filter.Trademark | N/A | Exclude logical tests that target the Staples table | No
ExpressionExclusions_Standard | string.ascii,string.char | N/A | Exclude expression tests | No

### [LODTests]
Add this section to run LOD tests. This section is required.

Option | Example Value | Default | Description | Required?
-|-|-|-|-
LogicalExclusions_Staples | Filter.Trademark | N/A | Exclude logical tests that target the Staples table | No
ExpressionExclusions_Standard | string.ascii,string.char | N/A | Exclude expression tests| No

### [UnionTest]
Add this section to run Union tests. This section is required.

Option | Example Value | Default | Description | Required?
-|-|-|-|-
LogicalExclusions_Staples | Filter.Trademark | N/A | Exclude logical tests that target the Staples table | No
ExpressionExclusions_Standard | string.ascii,string.char | N/A | Exclude expression tests that| No

### [StaplesDataTest]
Add this section to test that your Staples data test is loaded correctly. This section is optional.

**Note:** Since Staples contains several UTF-8 characters, it may not pass even if the data is loaded correctly, which is why it is not part of the standard tests.

### [ConnectionTests]
An auto-generated section that is used to run tests to verify TDVT can connect to the Staples & cast_calcs tables.
The Connection Tests, and any other tests with the attribute `SmokeTest = True`, are run before the other tests.
They can be run by themselves using the --verify flag (for example, tdvt run postgres --verify).

Option | Example Value | Default | Description | Required?
-|-|-|-|-
CastCalcsTestEnabled | True | True | Runs connection smoke test against calcs table if true | No
StaplesTestEnabled | True | True | Runs connection smoke test against Staples table if true | No

## Example INI File
This is a basic ini file that runs tests against our postgres_jdbc sample connector. Here, we use an existing logical query format, skip some tests, and run connection smoke tests before the rest of the test groups.

```ini
[Datasource]
Name = postgres_jdbc
LogicalQueryFormat = simple_public
CommandLineOverride = -DLogLevel=Debug -DConnectPluginsPath=plugins

[StandardTests]
ExpressionExclusions_Standard = string.isdate, date.datediff.*
LogicalExclusions_Calcs = BUGS.B26728, Filter.Date_In
LogicalExclusions_Staples = lod.17_Nesting

[LODTests]

[UnionTest]

[ConnectionTests]
CastCalcsTestEnabled = True
StaplesTestEnabled = True
```

## Run TDVT tests

Run TDVT from your working directory since it will need the TDS and INI files you created when adding your data source.

To view the latest usage information, run:
`tdvt -h`

To show the registered data sources and suites, run:
`tdvt list --ds`

To run a data source's tests:
`tdvt run postgres_generic_example`

To run smoke tests, which verify TDVT can successfully connect to tables in your data source:
`tdvt run postgres_generic_example --verify`

To run expression tests:
`tdvt run postgres_generic_example -e`

To run logical query tests:
`tdvt run postgres_generic_example -q`

Test results are available in a CSV file called test_results_combined.
Try loading them in Tableau Desktop to visualize the results.

## Run Connectors tests

Run Connector tests from the TDVT working directory. Sample setup files required to run the connector tests are located in the [/tdvt/samples/connector-tests/](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/samples/connector-tests/) folder.

- Run ConnectionBuilderTest:

   tdvt run-connectors-test --conn-test connectionBuilder --conn-test-file [connBuilderSetupFilePath.xml](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/samples/connector-tests/connectionbuilder.xml)

- Run NormalizeConnectionAttributes Test:

   tdvt run-connectors-test --conn-test normalizeConnectionAttributes --conn-test-file [normalizaConnAttrSetupFilePath.xml](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/samples/connector-tests/matchesattributes.xml)

- Run MatchesConnectionAttributesTest:

   tdvt run-connectors-test --conn-test matchesConnectionAttributes --conn-test-file [matchesConnAttrSetupFilePath.xml](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/samples/connector-tests/normalizeattributes.xml)

- Run PropertiesBuilderTest:

   tdvt run-connectors-test --conn-test propertiesBuilder --conn-test-file [propBuilderSetupFilePath.xml](https://github.com/tableau/connector-plugin-sdk/tree/dev-2020.4/tdvt/samples/connector-tests/propertiesbuilder.xml)

- Run ServerVersionTest:

   tdvt run-connectors-test --conn-test serverVersion --conn-test-file [serVersionSetupFilePath.xml](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/samples/connector-tests/serverversion.xml) --conn-test-password-file [serVersionPassword.password](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/samples/connector-tests/serverversiontest.password)

## Test the sample connectors

Sample connectors are located in the samples/plugins folder.

1. Copy the samples/plugins folder to your working directory so that they exist under /plugins. Like this:
'/plugins/postgres_odbc/manifest.xml'

2. Check that everything is set up correctly and a list of tests displays:
`tdvt list --ds postgres_odbc`

## Review results

**Note:** This process is explained in our comprehensive TDVT Guide: [Tableau Connector SDK: Optimizing Tableau Connectors with TDVT](https://youtu.be/rAgnnByJIJA) [[28:26](https://youtu.be/rAgnnByJIJA?t=1706)].

After the tests have run, "test_results_combined.csv" is outputted to the working directory. It contains data around the passes and failures of each test case of the previous run, along with error messages, generated SQL, and more. The [/tdvt/ directory](https://github.com/tableau/connector-plugin-sdk/blob/master/tdvt/) contains a Tableau workbook to analyze the results and diagnose issues with the connector.

These steps show how to connect your test results to the workbook:

1. Locate the file "TDVT Results.twb" in [/tdvt/ directory](https://github.com/tableau/connector-plugin-sdk/blob/master/tdvt/) and copy it to your TDVT workspace.

1. Copy the "test_metadata.csv" file found in [/tdvt/tdvt/metadata/](https://github.com/tableau/connector-plugin-sdk/tree/master/tdvt/tdvt/metadata) into the TDVT workspace.

   ![]({{ site.baseurl }}/assets/sample-workspace.png)

1. Open the workbook and change to the "Data Source" tab.

1. Right-click the "test_results_combined" connection on the left, and click "Edit Connection".

   ![]({{ site.baseurl }}/assets/tdvt_edit_results.png)

1. In the File Navigator that opens, choose the "test_results_combined" spreadsheet in your tdvt folder.

1. Confirm the new connection is working by finding the proper TDS names in the data preview pane.

1. If the data is full of null values and seems corrupted, please change the text qualifier to use a double quote by right-clicking the "test_results_combined.csv" connection in the data pane, and selecting __Text File Properties__.

1. See [Fixing TDVT Test Failures](https://tableau.github.io/connector-plugin-sdk/docs/tdvt-test-case) for more on how to leverage the workbook and diagnose connector failures.

   ![]({{ site.baseurl }}/assets/tdvt_results_dashboard.png)

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

**tdvt_output.json** - JSON output of test results. Suitable for rerunning failed tests. See `tdvt --help`.

**tdvt_results.csv** - Tableau-friendly result file. Load with a double-quote text qualifier.

The preceding files have versions named "_\_combined._" (for example, tdvt_log_combined.txt). This indicates the file contains combined results from several test suites.

## Architecture

Each data source has an associated collection of test group defined in the mydb.ini file.
You can see these by running this command:
`tdvt list --ds mydb`.

When you invoke `tdvt run mydb`, each test group runs on its own thread.
Each test group can consist of one or more tests, and each test can consist of one or more test cases.

The test group spawns a number of worker threads to run these tests in parallel.
Each worker thread invokes tabquerytool to run the entire suite of tests.

The tabquery process compiles the test into SQL, runs it against your database, and saves a result file.
TDVT then compares these result files to the expected result file.

After all test suites are finished, TDVT compiles the results into a CSV file.
The CSV file contains information such as the test name, a "passed" indicator, the generated SQL, and the data (tuples) that came back from the database for each test case.
It also indicates which expected file most closely matched the actual results from the query.

### Expected files

The expected files are located in the TDVT Python package location.
You can find this by running:
`python -m pip show tdvt`.

Expression tests have a name like "setup.agg.avg.txt" and a corresponding expected file like "expected.setup.agg.avg.txt".
There may be optional alternative expected files like "expected.setup.agg.avg.1.txt", and so on.
The expected files are located in the "exprtests" directory within the TDVT package directory.

Logical tests have names like "setup.Filter.slicing_Q_date_month_instance_filter.prefix_bool\_.xml".
The last section of the name "prefix_bool\_" corresponds to the name of the logical query config from your mydb.ini file.
These various permutations do not affect the test results so the expected file has a base name like "expected.setup.Filter.slicing_Q_date_month_instance_filter.xml". The expected files are located in "logicaltests/expected" in the TDVT package directory.

## Frequently found issues and troubleshooting

__Smoke tests fail and the rest of the tests are skipped__

The first thing TDVT does is try to connect to your database using the .tds files you created. If these “smoke tests” can’t connect, all other tests will fail and so are skipped to save time.

1. Check the TDS file: Open the TDS file in Tableau.
   Check to see if Tableau shows any error messages, prompts for a username and password, or asks for any additional information fix that's in the TDS file.
   You should be able to open the TDS and create a viz without any prompts.

1. (If testing a packaged `.taco` file) Check that the taco is located in your `"My Tableau Repository\Connectors"` folder

1. (If testing an unpackaged connector) Check the INI file for the following line:
<span style="font-family: courier new">CommandLineOverride = -DLogLevel=Debug -DConnectPluginsPath=[PathToPluginsFolder]</span>
   Make sure that the DConnectPluginsPath attribute is present and correct.

1. Check Python version. If you are using both Python 2.x and Python 3, then run TDVT using the command:
`py -3 tdvt.py …`

1. Check tabquerytool.exe. This file should be placed in your Tableau bin directory and tdvt/config/tdvt_override.ini should be updated to point at that executable.

__Boolean data types are not recognized or your database doesn't support them__
You may need to rename a column in the TDS file.
For example, the database may integer columns instead of Booleans for the **bool0**, **bool1**, **bool2**, and **bool3** columns.
In this case, you would want to load the table into your database using integer columns named **bool0\_** (a trailing underscore), and so on.
You can remap these in the TDS file by adding a column definition like this:

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

__Check that test data is loaded correctly__
Incorrect data can cause many test failures. There are two tests that test if your data is loaded correctly:
- calcs_data
The standard test group include a test named calcs_data that contains several test cases, one for each column in the table.
Make sure this test and all test cases pass first before troubleshooting elsewhere.

- StaplesDataTest
There is a similar test for the Staples table, but you must add it manually to your mydb.ini file by adding "[StaplesDataTest]".
This test works like the calcs_data test, but since Staples contains several UTF-8 characters, it is difficult to get it to pass completely.
Some of the logical tests filter one these UTF-8 characters, but you can get 100% pass rate even if the StaplesDataTest does not pass.
Still it can be useful for tracking down data issues.

One common way test data can be loaded incorrectly is if, when loading in the TestV1 data from the provided CSV empty values are discarded instead of being treated as nulls. Some databases do this by default when loading csv data in to clean up the data, but for TDVT we need the nulls to test that their behavior is correct.

__Try a different connector__
It can be insightful to load the Calcs and Staples tables on a Postgres or MySQL server and run the tests in order to compare working SQL against what TDVT is generating for your database.
Just add a new data source to TDVT that uses the native connector for that database.
Do not use the Other Databases (ODBC) connector in this case.
These tests should pass completely for these data sources.

__Check your TDS is set up__
Make sure the TDS files include the <span style="font-family: courier new">password</span> element and that you have renamed the relations to <span style="font-family: courier new">leaf</span>, as indicated in the setup instructions.

__Check log files__
tdvt_log\*.txt contains <span style="font-family: courier new">--verbose</span> level logging.
It can help to either run a single test or to run things in serial with <span style="font-family: courier new">-t 1 -tt 1</span> otherwise the log file will be interleaved by different subthreads.
tabquerytool writes log files to the "My Tableau Repository" folder.
These can be useful if it isn't clear what is causing a test to fail.

__Troubleshoot when actual does not match expected__
When your database returned results that do not match any expected files for that test, consider the following:

- Precision errors.
A common problem is precision errors for floating point values, although the test framework imposes some rounding to standardize results.
If the error is not significant then you can either skip the test or add a new expected file.

- Misaligned date functions.
Another common problem involves various date functions that might be off by a day.
These can be caused by start of week errors (Sunday should be 1 and Saturday is 7).
Other causes might include discrepancies around some start of week calculations or quarter boundaries.

__No generated SQL__
This can mean that Tableau was unable to find the functions necessary (see above).
Sometimes Tableau was able to run some SQL but it wasn't reported to TDVT.
In that case you can inspect the Tableau log files for that test.
It's helpful to clear the log files and then run just the single failing test. See <span style="font-family: courier new">tdvt --help</span> for more details.

__All logical query tests fail__
If all the logical queries fail, it can mean that you don't have the right logical query config associated in your mydb.ini file. If no logical query config matches your database, you can create your own in your suite's ini file.

__Logic assert in DatepartFunction.cpp__
Check that any <span style="font-family: courier new">date-format</span> elements in your TDD file have a valid <span style="font-family: courier new">name</span>. See [Creating a TDD File](https://tableau.github.io/connector-plugin-sdk/docs/dialect)

__The agg.countd expression test and the join.null.int logical tests are failing__
Check that your database is correctly returning column nullability information in the metadata. See [Design Considerations]({{ site.baseurl }}/docs/design) for more information.
