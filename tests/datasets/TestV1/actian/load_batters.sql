DROP TABLE IF EXISTS "Batters";

\include ../DDL/Batters.sql

copy "Batters"(
        player= text(0)csv with null('NULL'),
        team= text(0)csv with null('NULL'),
        league= text(0)csv with null('NULL'),
        year= text(0)csv with null('NULL'),
        games= text(0)csv with null('NULL'),
        ab= text(0)csv with null('NULL'),
        r= text(0)csv with null('NULL'),
        h= text(0)csv with null('NULL'),
        doubles= text(0)csv with null('NULL'),
        triples= text(0)csv with null('NULL'),
        hr= text(0)csv with null('NULL'),
        rbi= text(0)csv with null('NULL'),
        sb= text(0)csv with null('NULL'),
        cs= text(0)csv with null('NULL'),
        bb= text(0)csv with null('NULL'),
        so= text(0)csv with null('NULL'),
        ibb= text(0)csv with null('NULL'),
        hbp= text(0)csv with null('NULL'),
        sh= text(0)csv with null('NULL'),
        sf= text(0)csv with null('NULL'),
        gidp= text(0)csv with null('NULL')
        )
FROM '../Batters.csv'; 
\p\g
