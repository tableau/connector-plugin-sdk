Actian ODBC Connector for Tableau
=================================

This is a Connector for Tableau created with the [connector-plugin-sdk](https://github.com/tableau/connector-plugin-sdk).

Recommended version of Tableau Desktop is 2019.2.2.

Latest version of the Connector can be obtained from [GitHub](https://github.com/clach04/connector-plugin-sdk/tree/actian/samples/plugins/actian_odbc)

Table of contents
-----------------

  * [Usage](#usage)
    + [Install ODBC driver](#install-odbc-driver)
    + [Obtain Connector/install](#obtain-connector-install)
    + [Launch Tableau with new flags](#launch-tableau-with-new-flags)


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


