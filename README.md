TDVT - Tableau Datasource Verification Tool
---------------

TDVT is an automated testing tool for testing Tableau connectivity with a database.  Tests span from simple expressions to complex SQL.  When evaluating the connection to your database, please use a named connector if one exists.  Named connectors are optimized connections and provide a faster, cleaner experience for customers.  If a named connector does not exist, you can connect through the Other Databases (ODBC) options.  For more information on ODBC, check out this guide.  

We recommend running TDVT for:
*       New Driver Releases
*       Database Patches
*       Database Releases

What’s in this guide?
---------------
This guide will walk through setting up the TDVT and using it.  The guide will show you have to set up and configure the TDVT, how to add configurations for your own Data source, and how to run tests.    This guide uses Postgres as an example, but you can use your own data source to follow along with this guide. 

Test Scope
1.	Ability to connect to your database
2.	Support for all Tableau calculations (see below)
3.	Support for simple queries
4.	Support for complex queries

![Alt text](/readme_img/expression_dialog.jpg?raw=true "Tableau Expression Dialog")

### Requirements ###
1. PC or VM running Windows. In the future Tableau will provide Mac and Linux versions.
2. Python 3.3. Pip is required as well but should come by default with the Python installation.  Ensure that you check "install environmental variables".
3. An ODBC driver for your database.
4. The 'Calcs' and 'Staples' table loaded in your database.
    

How it works
---------------
The TDVT consists of Python scripts that create a test framework around TabQueryCLI.exe. The inputs are an expression test file or a logical query and a TDS. The outputs are rows of data returned from the database after executing the query.

Expression tests are text files that contain Tableau calculation language expressions (ie anything you could type into an edit calculation dialog). These expressions are parsed and compiled as individual queries.

Logical query tests are intermediate, abstract query representations. These are parsed and run like the expression tests.

For each input file the tdvt script calls TabQueryCLI.exe to run the query and then compares the results to an expected file. Multiple expected files are supported.


Installation
---------------

1. Install TDVT Python module
    * Install from an archive file: `pip install tdvt-1.1.59.zip` or `py -3 -m pip install tdvt-1.1.59.zip`.
    * Verify it is installed by running `pip list` or `py -3 -m pip list`.
2. Run this from your working directory to create the necessary setup directories.
    `py -3 -m tdvt.tdvt --setup`
3. Extract and then load the TestV1 minimal dataset into your database.
4. Move tabquerycli.exe and tabqueryclihelper.dll to your Tableau x.y bin directory (i.e. C:\Program Files\Tableau\Tableau 10.5\bin).
3. Edit config/tdvt/tdvt_override.ini and set the path to tabquerycli.exe.
    * For example: `TAB_CLI_EXE_X64 = C:\Program Files\Tableau\Tableau 10.5\bin\tabquerycli.exe` 

Notes on loading TestV1
---------------
See the section below about troubleshooting boolean values if your database does not have a native boolean type.

There is a 'StaplesData' test and a 'calcs_data' test that retrive every value from the table and compare it to an expected value. This can help ensure the data is loaded correctly with the right data types.

Notes on invoking TDVT
---------------
When TDVT is installed as a Python module it can be invoked as follows:
`python -m tdvt.tdvt`. If you have Python 2 and Python 3 installed run it like `py -3 -m tdvt.tdvt`. This will ensure Python 3 is used. In th examples below `tdvt` is used, but one of the above would be used in actual practice.


TDVT will look for the necessary config and setup files relative to the current working directory. Always run TDVT commands from the top level directory of your generated folder structure.
Use double quotes to wrap arguments that contain spaces.

`tdvt --generate` is used to update some config files. You need to run it if you add a new datasource or change your mydb.ini file.

Adding a new datasource
---------------
First decide on a name for your new datasource. This TDVT config name will be used to name configuration files and will be the argument you use to invoke TDVT. This documentation will use 'mydb' as an example.
Secondly you will need two Tableau Data Source files (.tds). These represent saved connection information to a particular table in your database. TDVT uses the 'Calcs' and 'Staples' tables.

1. Start Tableau desktop and connect to the 'Calcs' table using 'Other Database (ODBC)'. Once connected, right click on the datasource in the top left 'Data' tab and pick 'Add to Saved Datasources'. Save this in the 'tdvt/tds' directory. Name this file 'cast_calcs.\*.tds' or 'Staples.\*.tds' where * represents your TDVT config name. For example 'cast_calcs.mydb.tds'.
![Alt text](/readme_img/connection_1.jpg?raw=true "Connection to the Calcs table")
![Alt text](/readme_img/connection_2.jpg?raw=true "Saving the TDS file")
2. Open the tds file in a text editor and embed the password in the <connection> tag of the tds file next to the existing 'username' value. Save the file.
![Alt text](/readme_img/edit_tds.jpg?raw=true "Adding password to the TDS file")
3. Repeat this for the 'Staples' table.
4. Run `tdvt --add_ds mydb`. This wil create a mydb.ini file under /config and will modify your two tds files to rename the connection.
5. Update the generated ini file (ie mydb.ini) and choose a logical query config that matches what your database supports. See the section below titled 'Choosing a logical query config'.
6. Run: `tdvt --generate`
7. Verify your new test suite by running: `tdvt --list your_datasource_name`. It should show you a list of test suites associated with this datasource.

The `add_ds` command will rename the connection names to 'leaf'. See one of the tds files in '/tds' for an example. This occurs in two places, `<named-connection name='leaf'> and <relation connection='leaf' >`. If this is not done the logical query tests may cause tabquerycli.exe crashes or application exceptions.
The mydb.ini file names the test suite and specifies which tests to run. The `Name` section of the ini file is used to find your TDS files. For example, if you set `Name = mydb` then your TDS files should be named `cast_calcs.mydb.tds` and `Staples.mydb.tds`.

Now you can run the tests using `tdvt --run mydb`

TDC files are also supported through the Tableau Repository.

Choosing a logical query config
---------------
1. Open the Staples tds file in a text editor and look for the relation xml tag. For example: `<relation connection='leaf' name='Calcs' table='[dbo].[Calcs]'>`
2. Note the value for 'table', in this case '[dbo].[Calcs]'.
3. Run `tdvt --list_logical_configs`. This will print out all the logical query versions and some information about how they map things. Search the output of the command for something that matches '[dbo].[Calcs]'.
A selection of the output:
    Name = dbo
    Calcs = [dbo].[Calcs]
    Staples = [dbo].[Staples]
    Camel Case = [Camel Case]
    bool0 = [bool0]
    Date = [Date]

The Calcs value should match what you found in step 3. There are also mappings for some column names in case your database does not support the names as provided in the Calcs and Staples data files. For example, some databases may not support spaces in identifiers, in which case you can look for a logical configuration that replaces them with underscores and name the columns in your table accordingly.
4. In this case the logical configuration named 'dbo' matches.
5. Note the Name of the logical configuration and add this line to your ini file under the [Datasource] heading: LogicalQueryFormat = dbo
6. run: `tdvt --generate`

If none of the logical configurations work for your datasource then you can create your own in the ini file. See the next section below.

INI file structure
---------------

```ini
[Datasource]

Name = your_datasource_name  #i.e. mydb

LogicalQueryFormat = dbo

#You can add a new logical config here and use it above. These are example attributes, you wouldn't set them all since some are mutually exclusive.

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

CommandLineOverride = LogLevel=Debug #Space separated list of arguments that are passed through unchanged to tabquerycli.exe. Most Tableau arguments require a prepended '-D'.

MaxThread = 6   #You can add this to control Max Thread number when you use TDVT to run single datasource, it cannot apply with multi datasource

MaxSubThread = 4    #You can add this to control Max Sub Thread number for each test suite for this type of datasource

[StandardTests]

#You can put in comma separated string values that match part or all of a test name to exclude them. The asterix works as a wildcard.

LogicalExclusions_Calcs = string.right

LogicalExclusions_Staples = Filter.Trademark

ExpressionExclusions_Standard = string.ascii,string.char,logical

#If you remove this section the your test sute will not include the Level of Detail tests.

[LODTests]

#You don't need to specify anything to add this test suite, but you can exclude tests here too:

LogicalExclusions_Staples = 

ExpressionExclusions_Calcs = 

#This test will verify that your Staples table is loaded correctly. 

[StaplesDataTest]

#Recommended ini file for full test coverage:

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

TestPath = tests/mytests/ #This could point to a local directory relative to your tdvt working directory named 'tests'. Or for a logicaltest it would be 'tests/logical/setup/mytests/setup.\.xml


```

Running tests
---------------
Try `tdvt -h` for the latest usage information.

Run tdvt from your working directory since it will need the tds and ini files you created when adding your datasource.

To show the registered datasources and suites run: `tdvt --list`

Run a test:
`tdvt --run postgres_generic_example`
To run expression tests:
`tdvt --run postgres_generic_example -e`
To run logical query tests:
`tdvt --run postgres_generic_example -q`

Test results are available in a csv file called test_results_combined.csv. Try loading them in Tableau to visualize the results.

Review Results	
---------------
After the tests have run, you will see a “test_results_combined.csv” spreadsheet.  This contains the data about the test passes and failure from the previous run.  The TDVT includes a sample Tableau Workbook, available from your friendly Tableau contact, that will help you analyze the results of this file file. You can use these steps as a guide to develop your own workbook.
1.	Open the file called “Example Postgres Calc Test Result.twbx”, or start Tableau and connect to 'Text File'.
2.	Navigate to the “Data Source” tab.
3.	Click on the “test_results” connection on the left, and click “Edit Connection”.
![Alt text](/readme_img/edit_results.jpg?raw=true "Connecting to the csv results file")
4.      In the file navigator that comes up, choose the “test_results_combined” spreadsheet that is in your “tdvt” folder.
5.      Drag the new “test_results_combined.csv” file out to replace the old file in the data pre canvas.
6.      Right click on the new table, and click “Text File Properties…”.
![Alt text](/readme_img/edit_results2.jpg?raw=true "Connecting to the csv results file")
7.	Change the “text qualifier” to use a double quote.
8.	View the Viz by clicking on “Functional Test Pass” which should like the information below.  The Viz shows the test pass rate by Test Category.  Click on the bars to see the relevant failed tests in the “Test Details” section.
![Alt text](/readme_img/edit_results3.jpg?raw=true "Connecting to the csv results file")

File structure
---------------
Your working directory will look like this.
        tdvt/config - Ini files that configure test suites.
        tdvt/config/registry - You can create more elaborate groups of test suite here.
        tdvt/config/tdvt/tdvt_override.ini - You can specift the path to tabquerycli.exe here.
        tdvt/tds - Tds files.
        tdvt/ - TDVT log file, output csv and json files, a zip file containing any test results that did not match the expected results.

TDC Files and Logging
---------------
TDC files are supported either in the My Tableau Repository, or embedded in the TDS file.
Tableau desktop style logs will be found in your My Tableau Repository. TDVT logs will be found in the main TDVT directory.

Output
---------------
tdvt_actuals.zip - Zipped actual files from a test run. These are test results that did not match any expected files.
tdvt_log.txt - Verbose logging from tdvt.
tdvt_output.json - JSON output of test results. Suitable for re-running failed tests. See tdvt --help.
tdvt_results.csv - Tableau friendly result file. Load with a double quote text qualifier.

The above files have versions named *_combined.*, such as tdvt_log_combined.txt. This indicates the file contains combined results from several test suites.

Architecture
---------------

Each datasource has an associated collection of test suites defined in the mydb.ini file. You can see these by running `tdvt --list mydb`. When you invoke `tdvt --run mydb` each test suite runs on it's own thread. Each test suite can consist of one or more tests, and each test can consist of one of more test cases. The test suite spawns a number of worker threads to run these tests in parallel. Each worker thread invokes 'tabquerycli.exe' to run the test. The tabquery process compiles the test into SQL, runs it against your database and saves a result file. TDVT then compares these result files to the expected result file.
Once all test suites have finished TDVT will compile the results into a csv file. The csv file contains information such as the test name, a 'passed' indicator, the generated SQL and the data (tuples) that came back from the database. It also indicates which expected file most closely matched the actual results from the query.

### Expected Files ###
The expected files are located in the TDVT Python package location. You can find this by running `python -m pip show tdvt`. Expresion tests have a name like 'setup.agg.avg.txt' and a corresponding expected file like 'expected.setup.agg.avg.txt'. There may be optional alternative expecteds like 'expected.setup.agg.avg.1.txt' and so on. The expected files are located in 'exprtests/' in the TDVT package directory.
Logical tests have names like 'setup.Filter.slicing_Q_date_month_instance_filter.prefix_bool\_.xml'. The last section of the name 'prefix_bool\_' corresponds to the name of the logical query config from your mydb.ini file. These various permutations do not affect the test results so the expected file has a base name like  'expected.setup.Filter.slicing_Q_date_month_instance_filter.xml'. The expected files are located in 'logicaltests/expected' in the TDVT package directory.


Frequently Found Issues and Troubleshooting
---------------
### All my tests are failing?!@?#$!? ###
1.	Check the TDS File: Open the TDS file in Tableau.  If Tableau shows any error messages, prompts for a username/password, or asks for any additional information fix that in the TDS file.  You should be able to open the TDS and create a viz without any prompts.
2.	Check Python Version: If you are using both Python 2.x and Python 3, then run TDVT using the following command
     py -3 tdvt.py …
3.	Check tabquerycli.exe: This file should be placed in you Tableau bin directory and tdvt/config/tdvt_override.ini should be updated to point at that executable. It is very important that the version of tabquerycli.exe exactly matches the version of Tableau Desktop.

### Boolean Datatypes are not recognized or your database doesn't support them###
Sometimes you may need to rename a column in the tds. For example the database may integer columns instead of booleans for the **bool0**, **bool1**, **bool2**, and **bool3** columns. In this case you would want to load the table into your data base using integer columns named **bool0_** (a trailing underscore) etc. You can re-map these in the tds by adding a column definition like this:

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
  </column>```
 
![Alt text](/readme_img/edit_tds_columns.jpg?raw=true "Renaming boolean columns")


### Troubleshooting test failures ###

DATEPARSE, SPLIT, and POWER tests can be skipped in your ini file.  There is currently no way to add this functionality via a TDC, but if your connector supports that function, we can add it later in a named connector.

First ensure that the data is loaded correctly. Incorrect data can cause many test failures. The standard test suite include a test named 'calcs_data' that contains several test cases, one for each column in the table. This test and all test cases must pass first before further troubleshooting.
There is a similar test for the Staples table but you must add it manually to your mydb.ini fiel by adding '[StaplesDataTest]'. This test works like the 'calcs_data' test but since Staples contains several UTF-8 characters it is difficult to get it passing completely. Some of the logical tests filter one these UTF-8 characters but you can get 100% pass rate even if the StaplesDataTest does not pass. Still it can be useful for tracking down data issues.

It can be insightful to load the Calcs and Staples tables on a PostGre or MySQL server and run the tests in order to compare working SQL against what TDVT is generating for your database. Just add a new datasource to TDVT that uses the native connector for that database. Do not use Other ODBC in this case. These tests should pass completely for these datasources.

### Check your setup ###
Make sure the tds files include the 'password' element and that you have renamed the relations to 'leaf' as indicated in the setup instructions.

### Log Files ###
tdvt_log\*.txt contains '--verbose' level logging. It can help to either run a single test or to run things in serial with '-t 1 -tt 1' otherwise the log file will be interleaved by different sub threads.
tabquerycli.exe writes log files to your 'My Tableau Repository'. These can be useful if it isn't clear what is causing a test to fail.

### Actual does not match expected ###
This means that your database returned results that do not match any expected files for that test. One common problem is precision errors for floating point values, although the test framework imposes some rounding to standardize results. If the error is not significant then you can either skip the test or add a new expected file. Another problem invloves various date functions that might be off by a day. These can be caused by start of week errors (Sunday should be 1 and Saturday is 7). Other causes might include discrepancies around some start of week calculations or quarter boundaries.

### Invalid expression ###
This kind of error indicates that Tableau was unable to generate SQL for the test case. Usually it means that Tableau queried the driver to see what ODBC functions are supported but a necessary function or cast/convert was not found. Tuning the TDC file can sometimes fix these although it is a difficult process. A future version of TDVT will support an easy method of adding these functions.

### An ODBC error from your database ###
If Tableau generates SQL that does not work against your database the easiest fix is to note what will work. These custom functions can be added during development work for a new connector. In the future there will be a way to add or change how the SQL is generated. TDC files can sometimes help as well.

### No generated SQL ###
This can mean that Tableau was unable to find the functions necessary (see above). Sometimes Tableau was able to run some SQL but it wasn't reported to the TDVT. In that case you can inspect the Tableau log files for that test. It is helpful to clear the log files and then run just the single failing test. See the 'tdvt --help' for more details.

### Logical Query Tests ###
If all the logical queries fail it can mean that you do not have the right logical query config associated in your mydb.ini file.
