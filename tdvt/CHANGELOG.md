# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.13.4] - 2023-12-20
- Some nits from making the release PR.

## [2.13.3] - 2023-12-04
- Change ARM tabquery path logic, falling back to regular Mac path if no arm-specific one is found.

## [2.13.2] - 2023-12-04
- Add expecteds with tolerance tags.

## [2.13.1] - 2023-12-01
- Fix bug in Mac ARM path logic.

## [2.13.0] - 2023-11-28
- Add support for Apple Silicon-specific tabquery path in tdvt.ini

## [2.12.0] - 2023-11-14
- Add support for tolerance, changing how test actuals and expecteds are compared to use `math.isclose()` if a tolerance value is included in expected file.

## [2.11.3] - 2023-10-15
- Escape column names in expression tests. Contributed by @wnob via [PR 1194](https://github.com/tableau/connector-plugin-sdk/pull/1194).

## [2.11.2] - 2023-10-09
- Fixed error produced by zip log deletion attempts.
- Added unit testing around BatchQueueWork do_work().

## [2.11.1] - 2023-09-29
- Changed verbiage and added newline to failed test run commands to test results.

## [2.11.0] - 2023-09-27
- Added failed test run commands to test results.

## [2.10.0] - 2023-09-19
- Update logging so `tdvt_log_combined.txt` is less verbose by default, but can have the current output using the `--verbose` flag.
- Update various logging calls to use the appropriate logging level throughout TDVT.
- Fix a bug that kept `tdvt_log_combined.txt` from being created but not being appended.

## [2.9.8] - 2023-09-13
- Add more REGEXP test cases

## [2.9.7] - 2023-08-28
- Added formatting for generated expected files.

## [2.9.6] - 2023-08-28
- Address Spark SQL test issue

## [2.9.5] - 2023-08-28
- Add regex/tds mangling tests.

## [2.9.4] - 2023-08-09
- Add more `dateadd` tests.

## [2.9.3] - 2023-07-26
- PR 1151 from the monolith, add missing metadata argument.

## [2.7.6]. - 2023-10-11
- Use quoting for column references in the expression tests.

## [2.7.0]. - 2022-10-28
- Add a `--perf-run` flag that changes the output of `tdvt_log_combined.csv`.

## [2.6.2] - 2022-03-22
- Update file encoding of setup.string.regex.icu_fallback.txt to utf-8.

## [2.6.1] - 2022-02-04
- Bugfix for output-dir logic.

## [2.6.0] - 2021-11-30
- Added --output-dir option flag.

## [2.5.0] - 2021-12-01
- Convert smoke tests from Expression to Logical tests to support column renaming.

## [2.4.1] - 2021-12-01
- Hotfix for incorrect parsing of datasource inis that causes lots of incorrect console logs.

## [2.3.5] - 2021-04-30
- Hotfix for when cmd_output does not exist.

## [2.3.4] - 2021-04-12
- Clean up and simplify test metadata file
- Fix missing metadata file when running setup.py

## [2.3.3] - 2021-03-15
- Refactor calcs_data test
- Add logical query format option for fieldname postfix

## [2.3.2] - 2021-03-10
- Update expected file expected.setup.operator.date.6.txt for Presto TDVT test pass.

## [2.3.1] - 2020-12-23
- Revert Staples smoke test to be Expression; will fix in 2.3.2.

## [2.3.0] - 2020-12-09
- Change Staples smoke test to be logical.
- Added Connectors Tests.

## [2.2.1] - 2020-10-29
- Added: Moved some ISO8601 test cases from the Python 2.7 test framework to the TDVT suite
- Updated: Fixed some test cases with P3 defects initially checked in to use the correct functions (eg. DATENAME vs. DATETRUNC).

## [2.1.22] - 2020-10-05
- Added a expected file expected.setup.cast.str.13.txt to support Postgres 12 database server output. PR 626

## [2.1.21] - 2020-10-02
- Fixed a 'No tests found' error caused by a missing test metadata file.

## [2.1.20] - 2020-09-22
- test_results_combined.csv is now sorted by test complexity (number of distinct function tested)

## [2.1.19] - 2020-09-08
- test_results_combined.csv now include test priority, categories, and functions.

## [2.1.18] - 2020-08-25
- Initialsql tests use RAWSQLAGG_STR instead of RAWSQL_STR.

## [2.1.17] - 2020-08-21
- Updating expected values for Snowflake int % int test.

## [2.1.16] - 2020-07-29
- Add invalid driver tests for ODBC/JDBC plugins.

## [2.1.15] - 2020-06-15
- Add initialsql tests for vertica

## [2.1.14] - 2020-05-18
- Add more tests for initialsql

## [2.1.13] - 2020-05-8
- Fix the `force-run` flag logic to work with `run-file` command.

## [2.1.12] – 2020-04-30
- Add a `force-run` flag to run tests on all data source even if smoke tests fail.
- Update mocked unit tests to run correctly.

## [2.1.11] - 2020-04-23
- Added error comparison (comparing the `<error>` tag in query output); added `--compare-error` arg option.

## [2.1.10] - 2020-04-20
- Add test for initialsql

## [2.1.9] - 2020-04-13
- Change regex in setup_env.py to accomodate OM changes

## [2.1.7] - 2020-02-04
- Change return type in tdvt.py to resolve ValueError

## [2.1.6] - 2020-01-13
- Add string.contains.regex test to test escaping regex special characters in the Contains function

## [2.1.5] - 2020-01-08
- Update test names and setup file locations for CastCalcsTest, StaplesTest, and BadPasswordTest

## [2.1.4] - 2020-01-02
- Update smoke tests to count skipped & disabled tests as "pass". Also update the command line results from a TDVT run with more details.
- Refactor list command. list is used with suites and list-logical-configs is just for logical configs.
- Fixes test rerun bug.

## [2.1.3] - 2019-12-30
- Add tests specific to Snowflake.

## [2.1.2] - 2019-12-05
- Fix a bug that broke the `run-file` command.

## [2.1.1] - 2019-12-04
### Added
- Include all relevant log files in the zip archive.
- Compress the log file zip archive. This relies on the zlib module which seems to usually be installed by default.
- More logging about test exclusions.
- Update handling of args.run_file to use Path
- Update TDVT to add `expected_message` to JSON output of failed tests.
