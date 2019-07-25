# Hosting TestV1 in Actian Cloud Avalanche local Vector/ActianX/Ingres

NOTE does not use DDL folder SQL (uses the same SQL/defs though)

        cd CHECK_OUT\tests\datasets\TestV1\actian  # Windows
        cd CHECK_OUT/tests/datasets/TestV1/actian  # Linux/Unix

        sql < load_batters.sql mixedcase
        sql < load_calcs.sql mixedcase
        sql < load_staples.sql mixedcase
