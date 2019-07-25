DROP TABLE IF EXISTS "Batters";

CREATE TABLE "Batters"
(
    Player VARCHAR(101),
    Team VARCHAR(50),
    League VARCHAR(2),
    Year SMALLINT,
    Games DOUBLE PRECISION,
    AB DOUBLE PRECISION,
    R DOUBLE PRECISION,
    H DOUBLE PRECISION,
    Doubles DOUBLE PRECISION,
    Triples DOUBLE PRECISION,
    HR DOUBLE PRECISION,
    RBI DOUBLE PRECISION,
    SB DOUBLE PRECISION,
    CS DOUBLE PRECISION,
    BB DOUBLE PRECISION,
    SO DOUBLE PRECISION,
    IBB DOUBLE PRECISION,
    HBP DOUBLE PRECISION,
    SH DOUBLE PRECISION,
    SF DOUBLE PRECISION, 
    GIDP DOUBLE PRECISION
);
\p\g


copy batters(
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
