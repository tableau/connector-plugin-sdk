# Hosting TestV1 in Actian Cloud Avalanche local Vector/ActianX/Ingres

Test data is provided in utf8 encoding, the DBMS character set should match this setting.
An alternative WIN1252 encoded data set is available, to use this edit `load_staples.sql` and see the commented out code section.

SDK test suite expects mixedcase object names, although Tableau Desktop does not.

    cd CHECK_OUT\tests\datasets\TestV1\actian  # Windows
    cd CHECK_OUT/tests/datasets/TestV1/actian  # Linux/Unix

Create database and load data.
Use provided batch file for windows and shell script for Linux/MacOS/Unix:

  * `create_testdb.bat`
  * `sh create_testdb.sh`

NOTE does not use DDL folder SQL (uses the same SQL/defs though)
