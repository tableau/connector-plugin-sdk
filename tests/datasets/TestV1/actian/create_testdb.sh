#!/bin/sh

DBNAME=testv1

#DBNAME=${1}

iigetres ii.`iipmhost`.createdb.delim_id_case
iisetres ii.`iipmhost`.createdb.delim_id_case mixed
createdb ${DBNAME}
# optionally restore:
iisetres ii.`iipmhost`.createdb.delim_id_case lower


sql < load_batters.sql ${DBNAME}
sql < load_calcs.sql ${DBNAME}
sql < load_staples.sql ${DBNAME}
