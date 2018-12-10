# Hosting TestV1 in local PostgreSQL server

## Install PostgreSQL Server
- Download the latest 10.0 version: https://www.postgresql.org/download/
- Run the installer and accept the defaults.
- Create a password for the database superuser (postgres).

## Configure Database and Users with pgAdmin
- Run pgAdmin4: "C:\Program Files\PostgreSQL\10\pgAdmin 4\bin\pgAdmin4.exe"
- Create a new user, 'test'
    - Under Servers > PostgreSQL10, right-click Login/Group Roles and select Create > Login/Group Role...
    - On the General tab, in the Name field, type test.
    - On the Definition tab, in the Password field, enter a password.
    - On the Privileges tab, for Can login? and Superuser, toggle the switch to Yes.
    - Select Save.

- Create a new database, 'TestV1'.
    - Under Servers > PostgreSQL10, right-click Databases and select Create > Database...
    - On the General tab, in the Database field, type TestV1.
    - In the Owner drop-down list, select test.
    - Select Save.

## Prepare TestV1 scripts
- Update load_batters.sql, load_calcs.sql and load_staples.sql scripts by replacing ```<root_directory>``` with the correct absolute path.
    - Example: update ```<root_directory>``` to ```D:\```

## Load TestV1 dataset
- Verify the csv files have comma separated values.
- Run each script from an elevated command line. 

```
C:\Program Files\PostgreSQL\10\bin>

psql.exe -d TestV1 -f D:\connector-plugin-sdk\tests\datasets\TestV1\postgres\load_batters.sql test
psql.exe -d TestV1 -f D:\connector-plugin-sdk\tests\datasets\TestV1\postgres\load_calcs.sql test
psql.exe -d TestV1 -f D:\connector-plugin-sdk\tests\datasets\TestV1\postgres\load_staples.sql test
```
