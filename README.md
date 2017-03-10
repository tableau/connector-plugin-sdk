TDVT - Tableau Datasource Verification Tool
---------------

### Requirements ###
1. Python 3.
2. An ODBC driver for your database.
3. The 'Calcs' and 'Staples' table loaded in your database.
4. Optional: The TPCH 1GB dataset loaded in your database.
    

How it works
---------------
The TDVT consists of Python scripts that create a test framework around TabQueryCLI.exe. The inputs are an expression test file or a logical query and a TDS. The outputs are rows of data returned from the database after executing the query.

Expression tests are text files that contain Tableau calculation language expressions (ie anything you could type into an edit calculation dialog). These expressions are parsed and compiled as individual queries.

Logical query tests are intermediate, abstract query representations. These are parsed and run like the expression tests.

For each input file the tdvt script calls TabQueryCLI.exe to run the query and then compares the results to an expected file. Multiple expected files are supported.


Installation
---------------

1. Install TDVT Python module
    * Install from an archive file: `pip install tdvt-1.1.13.tar.gz`
    * TODO pip install
2. Run this from your working directory to create the necessary setup directories.
    `tdvt.py --setup`
3. Edit config/tdvt/tdvt_override.ini and set the path to tabquerycli.exe.
    * For example: `TAB_CLI_EXE_X64 = C:\Program Files\Tableau\Tableau 10.1\bin\tabquerycli.exe` 

Notes on invoking TDVT
---------------
TDVT will look for the necessary config and setup files relative to the current working directory. Always run TDVT commands from the top level directory of your generated folder structure.
Use double quotes to wrap arguments that contain spaces.

`tdvt --generate` is used to update some config files. You need to run it if you add a new datasource or change your mydb.ini file.

Adding a new datasource
---------------
First decide on a name for your new datasource. This TDVT config name will be used to name configuration files and will be the argument you use to invoke TDVT. This documentation will use 'mydb' as an example.
Secondly you will need two Tableau Data Source files (.tds). These represent saved connection information to a particular table in your database. TDVT uses the 'Calcs' and 'Staples' tables.

1. Start Tableau desktop and connect to the 'Calcs' table using 'Other Database (ODBC)'. Once connected, right click on the datasource in the top left 'Data' tab and pick 'Add to Saved Datasources'. Save this in the tdvt/tds directory. Name this file 'cast_calcs.\*.tds' or 'Staples.\*.tds' where * represents your TDVT config name. For example 'cast_calcs.mydb.tds'.
2. Open the tds file in a text editor and embed the password in the <connection> tag of the tds file next to the existing 'username' value. Save the file.
3. Repeat this for the 'Staples' table.
4. Run `tdvt.py --add_ds mydb`. This wil create a mydb.ini file under /config and will modify your two tds files to rename the connection.
5. Update the generated ini file (ie mydb.ini) and choose a logical query config that matches what your database supports. See the section below titled 'Choosing a logical query config'.
6. Run: `-m tdvt.tdvt --generate`
7. Verify your new test suite by running: `-m tdvt.tdvt --list your_datasource_name`. It should show you a list of test suites associated with this datasource.

The `add_ds` command will rename the connection names to 'leaf'. See one of the checked in tds files for an example. `<named-connection name='leaf'> and <relation connection='leaf' >`. If this is not done the logical query tests may cause tabquerycli.exe crashes or application exceptions.
The mydb.ini file names the test suite and specifies which tests to run. The `Name` section of the ini file is used to find your TDS files. For example, if you set `Name = mydb` then your TDS files should be named `cast_calcs.mydb.tds` and `Staples.mydb.tds`.

Now you can run the tests using `-m tdvt.tdvt.py --run your_suite_name`

TDC files are also supported through the Tableau Repository.

Choosing a logical query config
---------------
1. Open the Staples tds file in a text editor and look for the relation xml tag. For example: `<relation connection='leaf' name='Calcs' table='[dbo].[Calcs]'>`
2. Note the value for 'table', in this case '[dbo].[Calcs]'.
3. Run `tdvt --list_logical_configs`. This will print out all the logical query versions and some information about how they map things. The Calcs value should match what you found in step 3. for example. There are also mappings for some column names in case your database does not support the names as provided in the Calcs and Staples data files. For example, some databases may not support spaces in identifiers, in which case you can look for a logical configuration that replaces them with underscors and name the columns in your table accordingly.
4. In this case the logical configuration named 'dbo' matches.
5. Note the Name of the logical configuration and add this line to your ini file under the [Datasource] heading: LogicalQueryFormat = dbo
6. run: `tdvt --generate`

If none of the logical configurations work for your datasource then you can create a new version in tdvt/logicaltests/generate/templates.py.

INI file structure
---------------
[Datasource]

Name = your_datasource_name

LogicalQueryFormat = dbo

CommandLineOverride = LogLevel=Debug #Space separated list of arguments that are passed through to tabquerycli.exe. Each is prepended with -D.

MaxThread = 6   #You can add this to control Max Thread number when you use TDVT to run single datasource, it cannot apply with multi datasource

MaxSubThread = 4    #you can add this to control Max Sub Thread number for each test suit for this type of datasource

[StandardTests]

*\#You can put in comma separated string values that match part or all of a test name to exclude them. The asterix works as a wildcard.*

LogicalExclusions_Calcs = string.right

LogicalExclusions_Staples = Filter.Trademark

ExpressionExclusions_Standard = string.ascii,string.char,logical

*#If you remove this section the your test sute will not include the Level of Detail tests.*

[LODTests]

*\#You don't need to specify anything to add this test suite, but you can exclude tests here too:*

*LogicalExclusions_Staples = *

*ExpressionExclusions_Calcs = *

*#This test will verify that your Staples table is loaded correctly.* 

[StaplesDataTest]

*\#You can add a new arbitrary test suite like this.*

[NewExpressionTest1]

*You could add a new logical test instead:*

*[NewLogicalTest1]*

Name = expression_test_dates.

TDS = cast_calcs.your_datasource.tds

Exclusions = string.ascii,string.char

TestPath = exprtests/standard/

Recommended ini file for full test coverage:

*[StandardTests]*

*[StaplesDataTest]*

*[LODTests]*

*[UnionTest]*

Running tests
---------------
Try `python -m tdvt.tdvt -h` for the latest usage information.

Run tdvt from your working directory since it will need the tds and ini files you created when adding your datasource.

To show the registered datasources and suites run: `python -m tdvt.tdvt --list`

Run a test:
`python -m tdvt.tdvt --run postgres_generic_example`
To run expression tests:
`python -m tdvt.tdvt --run postgres_generic_example -e`
To run logical query tests:
`python -m tdvt.tdvt --run postgres_generic_example -q`

Test results are available in a csv file called test_results_combined.csv. Try loading them in Tableau to visualize the results.


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

TDS Workaround
---------------
Sometimes you may need to rename a column in the tds. For example see cast_calcs.mysql.tds. The database defines columns like [[bool0_]] whereas the TDVT tests expect a column named [[bool0]]. You can re-map these in the tds by adding a column definition like this:

<column datatype='boolean' name='[bool0]' role='dimension' type='nominal'>

    <calculation class='tableau' formula='[bool0_]!=0' />

</column>

Architecture and troubleshooting
---------------

Each datasource has an associated collection of test suites defined in the mydb.ini file. You can see these by running `tdvt --list mydb`. When you invoke `tdvt --run mydb` each test suite runs on it's own thread. Each test suite can consist of one or more tests, and each test can consist of one of more test cases. The test suite spawns a number of worker threads to run these tests in parallel. Each worker thread invokes 'tabquerycli.exe' to run the test. The tabquery process compiles the test into SQL, runs it against your database and saves a result file. TDVT then compares these result files to the expected result file.
Once all test suites have finished TDVT will compile the results into a csv file. The csv file contains information such as the test name, a 'passed' indicator, the generated SQL and the data (tuples) that came back from the database. It also indicates which expected file most closely matched the actual results from the query.

### Expected Files ###
The expected files are located in the TDVT Python package location. You can find this by running `python -m pip show tdvt`. Expresion tests have a name like 'setup.agg.avg.txt' and a corresponding expected file like 'expected.setup.agg.avg.txt'. There may be optional alternative expecteds like 'expected.setup.agg.avg.1.txt' and so on. The expected files are located in 'exprtests/' in the TDVT package directory.
Logical tests have names like 'setup.Filter.slicing_Q_date_month_instance_filter.prefix_bool\_.xml'. The last section of the name 'prefix_bool\_' corresponds to the name of the logical query config from your mydb.ini file. These various permutations do not affect the test results so the expected file has a base name like  'expected.setup.Filter.slicing_Q_date_month_instance_filter.xml'. The expected files are located in 'logicaltests/expected' in the TDVT package directory.

### Troubleshooting test failures ###

First ensure that the data is loaded correctly. Incorrect data can cause many test failures. The standard test suite include a test named 'calcs_data' that contains several test cases, one for each column in the table. This test and all test cases must pass first before further troubleshooting.
There is a similar test for the Staples table but you must add it manually to your mydb.ini fiel by adding '[StaplesDataTest]'. This test works like the 'calcs_data' test but since Staples contains several UTF-8 characters it is difficult to get it passing completely. Some of the logical tests filter one these UTF-8 characters but you can get 100% pass rate even if the StaplesDataTest does not pass. Still it can be useful for tracking down data issues.

It can be insightful to load the Calcs and Staples tables on a PostGre or MySQL server and run the tests in order to compare working SQL against what TDVT is generating for your database. Just add a new datasource to TDVT that uses the native connector for that database. Do not use Other ODBC in this case. These tests should pass completely for these datasources.

#### Check your setup ####
Make sure the tds files include the 'password' element and that you have renamed the relations to 'leaf' as indicated in the setup instructions.

#### Log Files ####
tdvt_log\*.txt contains '--verbose' level logging. It can help to either run a single test or to run things in serial with '-t 1 -tt 1' otherwise the log file will be interleaved by different sub threads.
tabquerycli.exe writes log files to your 'My Tableau Repository'. These can be useful if it isn't clear what is causing a test to fail.

#### Actual does not match expected ####
This means that your database returned results that do not match any expected files for that test. One common problem is precision errors for floating point values, although the test framework imposes some rounding to standardize results. If the error is not significant then you can either skip the test or add a new expected file. Another problem invloves various date functions that might be off by a day. These can be caused by start of week errors (Sunday should be 1 and Saturday is 7). Other causes might include discrepancies around some start of week calculations or quarter boundaries.

#### Invalid expression ####
This kind of error indicates that Tableau was unable to generate SQL for the test case. Usually it means that Tableau queried the driver to see what ODBC functions are supported but a necessary function or cast/convert was not found. Tuning the TDC file can sometimes fix these although it is a difficult process. A future version of TDVT will support an easy method of adding these functions.

#### An ODBC error from your database ####
If Tableau generates SQL that does not work against your database the easiest fix is to note what will work. These custom functions can be added during development work for a new connector. In the future there will be a way to add or change how the SQL is generated. TDC files can sometimes help as well.

#### No generated SQL ####
This can mean that Tableau was unable to find the functions necessary (see above). Sometimes Tableau was able to run some SQL but it wasn't reported to the TDVT. In that case you can inspect the Tableau log files for that test. It is helpful to clear the log files and then run just the single failing test. See the 'tdvt --help' for more details.

#### Logical Query Tests ####
If all the logical queries fail it can mean that you do not have the right logical query config associated in your mydb.ini file.
