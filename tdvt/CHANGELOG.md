# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
- Change Staples smoke test to be logical

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
