Actian JDBC Connector for Tableau
=================================

This is a Connector for Tableau created with the [connector-plugin-sdk](https://github.com/tableau/connector-plugin-sdk).

Recommended version of Tableau Desktop is 2019.2.2.

Latest version of the Connector can be obtained from [GitHub](https://github.com/clach04/connector-plugin-sdk/tree/actian/samples/plugins/actian_jdbc)

Usage
-----

### Install JDBC driver jar file

Install JDBC jar file, Tableau instructions for this are located at [Tableau Drivers](https://onlinehelp.tableau.com/current/pro/desktop/en-us/examples_otherdatabases_jdbc.htm).

Obtain iijdbc.jar and copy into `C:\Program Files\Tableau\Drivers`

iijdbc.jar can either be downloaded from [ESD](https://esd.actian.com/product/Avalanche/JDBC/java/Actian_Avalanche_JDBC_Drivers)
or obtained from a client installation from:

  * `%II_SYSTEM%\ingres\lib\iijdbc.jar` - Windows
  * `$II_SYSTEM/ingres/lib/iijdbc.jar` - Linux/Unix


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


