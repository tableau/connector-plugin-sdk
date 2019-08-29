@echo off
setlocal

set DBNAME=testv1

if [%1] == []  goto :do_it
set DBNAME=%1%

:do_it

iigetres ii.%COMPUTERNAME%.createdb.delim_id_case
iisetres ii.%COMPUTERNAME%.createdb.delim_id_case mixed
createdb %DBNAME%
REM restore, assume lower
iisetres ii.%COMPUTERNAME%.createdb.delim_id_case lower

:data_load
sql < load_batters.sql %DBNAME%
sql < load_calcs.sql %DBNAME%
sql < load_staples.sql %DBNAME%

goto :EOF

endlocal