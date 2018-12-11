DROP TABLE IF EXISTS "Calcs";

CREATE TABLE "Calcs"
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
    bool0 BOOLEAN,
    bool1 BOOLEAN,
    bool2 BOOLEAN,
    bool3 BOOLEAN,
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

COPY "Calcs" (key, num0, num1, num2, num3, num4, str0, str1, str2, str3, int0, int1, int2, int3, bool0, bool1, bool2, bool3, date0, date1, date2, date3, time0, time1, datetime0, datetime1, zzz) 
FROM '<root_directory>/connector-plugin-sdk/tests/datasets/TestV1/Calcs.csv' 
DELIMITER ',' CSV ENCODING 'UTF8' QUOTE '"'; 
