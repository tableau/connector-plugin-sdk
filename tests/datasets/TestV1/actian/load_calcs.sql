DROP TABLE IF EXISTS "Calcs";

\include ../DDL/Calcs.sql

CREATE TABLE calcs_temp
(
    key VARCHAR(255),
    num0 DOUBLE PRECISION,
    num1 DOUBLE PRECISION,
    num2 DOUBLE PRECISION,
    num3 DOUBLE PRECISION,
    num4 DOUBLE PRECISION,
    str0 VARCHAR(255),
    str1 VARCHAR(255),
    str2 VARCHAR(255),
    str3 VARCHAR(255),
    int0 INTEGER,
    int1 INTEGER,
    int2 INTEGER,
    int3 INTEGER,
    bool0 i1,
    bool1 i1,
    bool2 i1,
    bool3 i1,
    date0 DATE,
    date1 DATE,
    date2 DATE,
    date3 DATE,
    time0 TIMESTAMP,
    time1 TIME,
    datetime0 TIMESTAMP,
    datetime1 VARCHAR(255),
    zzz VARCHAR(255)
);


copy calcs_temp(
        "key"= text(0)csv with null(''),
        num0= text(0)csv with null(''),
        num1= text(0)csv with null(''),
        num2= text(0)csv with null(''),
        num3= text(0)csv with null(''),
        num4= text(0)csv with null(''),
        str0= text(0)csv with null(''),
        str1= text(0)csv with null(''),
        str2= text(0)csv with null(''),
        str3= text(0)csv with null(''),
        int0= text(0)csv with null(''),
        int1= text(0)csv with null(''),
        int2= text(0)csv with null(''),
        int3= text(0)csv with null(''),
        bool0= c0csv with null(''),
        bool1= c0csv with null(''),
        bool2= c0csv with null(''),
        bool3= c0csv with null(''),
        date0= text(0)csv with null(''),
        date1= text(0)csv with null(''),
        date2= text(0)csv with null(''),
        date3= text(0)csv with null(''),
        time0= text(0)csv with null(''),
        time1= text(0)csv with null(''),
        datetime0= text(0)csv with null(''),
        datetime1= text(0)csv with null(''),
        zzz= text(0)csv with null('')
        )
from '../Calcs.csv';

INSERT INTO "Calcs" select * from calcs_temp;
drop table calcs_temp;
\p\g

