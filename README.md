TDVT - Tableau Datasource Verification Tool

Requirements
    Python 3.

How it works
---------------
The TDVT consists of Python scripts that create a test framework around TabQueryCLI.exe. The inputs are an expression test file or a logical query and a TDS. The outputs are rows of data returned from the database after executing the query.

Expression tests are text files that contain Tableau calculation language expressions (ie anything you could type into an edit calculation dialog). These expressions are parsed and compiled as individual queries.

Logical query tests are intermediate, abstract query representations. These are parsed and run like the expression tests.

For each input file the tdvt script calls TabQueryCLI.exe to run the query and then compares the results to an expected file. Multiple expected files are supported.


Installation
---------------

1. Install TDVT Python module
    TODO pip install
    TODO install from module zip
2. Run this from your working directory to create the necessary setup directories.
    tdvt.py --setup
3. Edit config/tdvt/tdvt_override.ini and set the path to tabquerycli.exe.

Adding a new datasource
---------------
Adding a new datasource is easy. To run the expression tests first create a tds file that connectis to the Calcs table on your database.
1. The easiest way to create this is to connect to the table in Tableau desktop and then right click on the datasource and pick 'Add to Saved Datasources'. Save this in the tdvt/tds directory.
2. Open the tds file in a text editor and embed the password in the <connection> tag of the tds file.
3. Rename the connection names to 'leaf'. See one of the checked in tds files for an example. `<named-connection name='leaf'> and <relation connection='leaf' >`
4. Create an ini file in tdvt/config. The ini file names the test suite and specifies which tests to run.
5. Run: `-m tdvt.tdvt --generate`

Now you can run the tests using `-m tdvt.tdvt.py --run your_suite_name`

TDC files are also supported through the Tableau Repository.

Logical query files take a little more work since they need to be customized to the datasource. 
1. Create a tds file that connects to the Staples table on your database.
2. Open the tds in a text editor and look for the relation xml tag. For example: `<relation connection='leaf' name='Calcs' table='[dbo].[Calcs]'>`
3. Note the value for 'table', in this case '[dbo].[Calcs]'.
4. Open tdvt/logicaltests/generate/templates.py and search for a value that matches your table value. In this case 'dbo' matches.
5. Add this line to your ini file under the [Datasource] heading: LogicalQueryFormat = dbo
6. run: `tdvt --generate`

Verify your new test suite by running: tdvt_runner --list your_datasource_name
It should show you a list of test suites associated with this datasource.

INI file structure
---------------
[Datasource]
Name = your_datasource_name
LogicalQueryFormat = dbo

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

TDC Files and Logging
---------------
TDC files are supported either in the My Tableau Repository, or embedded in the TDS file.
Tableau desktop style logs will be found in your My Tableau Repository. TDVT logs will be found in the main TDVT directory.

Output
---------------
tdvt_actuals.zip - Zipped actual files from a test run.
tdvt_log.txt - Verbose logging from tdvt.
tdvt_output.json - JSON output of test results. Suitable for re-running failed tests. See tdvt --help.
tdvt_results.csv - Tableau friendly result file. Load with a double quote text qualifier.

The above files have versions named *_combined.*, such as tdvt_log_combined.txt. This indicates the file contains combined results from tdvt_runner.

TDS Workaround
---------------
Sometimes you may need to rename a column in the tds. For example see cast_calcs.mysql.tds. The database defines columns like [[bool0_]] whereas the TDVT tests expect a column named [[bool0]]. You can re-map these in the tds by adding a column definition like this:

<column datatype='boolean' name='[bool0]' role='dimension' type='nominal'>

    <calculation class='tableau' formula='[bool0_]!=0' />

</column>



