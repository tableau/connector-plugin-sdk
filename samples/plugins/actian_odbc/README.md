Actian ODBC Connector for Tableau
=================================

This is a Connector for Tableau created with the [connector-plugin-sdk](https://github.com/tableau/connector-plugin-sdk).

Recommended version of Tableau Desktop is 2019.2.2.

Latest version of the Connector can be obtained from
[GitHub](https://github.com/clach04/connector-plugin-sdk/tree/actian/samples/plugins/actian_odbc)

Table of contents
-----------------

  * [Usage](#usage)
    + [Install ODBC driver](#install-odbc-driver)
    + [Obtain Connector/install](#obtain-connector-install)
    + [Launch Tableau with new flags](#launch-tableau-with-new-flags)
    + [Notes](#notes)


Usage
-----

### Install ODBC driver

Install ODBC Driver from [ESD](https://esd.actian.com/product/Avalanche/Client_Runtime)

NOTE Tableau Desktop is a 64-bit product, it requires a 64-Bit ODBC Driver client installation.

### Obtain Connector/install

Obtain Connector, for example:

    git clone https://github.com/clach04/connector-plugin-sdk.git
    git checkout actian

Determine full path, for example, assuming Microsoft Windows.

    cd /d c:\
    git clone https://github.com/clach04/connector-plugin-sdk.git
    git checkout actian

Full path is:

    C:\connector-plugin-sdk\samples\plugins\

### Launch Tableau with new flags

Launch Tableau via command line (or create/update shortcut) to:

    "C:\Program Files\Tableau\Tableau 2019.2\bin\tableau.exe" -DConnectPluginsPath=C:\connector-plugin-sdk\samples\plugins\

Where `C:\Program Files\Tableau\Tableau 2019.2` is the location where Tableau was installed.

Notes
-----

### Object name case

For running the test suite, Tableau expects the non-default mixed case. This will not be needed for https://github.com/tableau/connector-plugin-sdk/issues/216 (CAP_ODBC_BIND_DETECT_ALIAS_CASE_FOLDING)

If your object name case is all lower case (which is the default for Actian Avalanche/Vector/ActianX/Ingres) mixed case option is **not** required.

I.e. only set mixed case if running Tableau Connector SDK tests suite.

Create database with mixed case object name support:

    iigetres ii.`iipmhost`.createdb.delim_id_case
    iisetres ii.`iipmhost`.createdb.delim_id_case mixed
    createdb mixedcase
    # optionally restore:
    iisetres ii.`iipmhost`.createdb.delim_id_case lower
