"""This module maintains the information about the set of attribute
definitions (aka "descriptions") that apply to each datasource type.
"""


# The leaf-strings in this data structure are really
# lightweight templates per the Templates class in
# Python's string module.  Bound names are:
# $dbPath -- Path to file-based local databases (e.g. csv files)
# $dsName -- Datasource name (e.g. 'Staples' or 'Calcs')
# $testDbName -- The current test database name, e.g. 'TestV1'
global attributes
attributes = {

    #TESTV1.Calcs
    'TESTV1' : { 
                 'tablename' : '$dsName',
                 #'tablenameUpper' : True,
                 #'fieldnameUpper' : True,
                 'tablePrefix' : '[TESTV1].',
                 },

    #TEST.Calcs
    'TEST' : { 
                 'tablename' : '$dsName',
                 #'tablenameUpper' : True,
                 #'fieldnameUpper' : True,
                 'tablePrefix' : '[TEST].',
                 },

    #test.Calcs
    'test_lower' : { 
                 'tablename' : '$dsName',
                 #'tablenameUpper' : True,
                 #'fieldnameUpper' : True,
                 'tablePrefix' : '[test].',
                 },

    #ADMIN.Calcs
    'ADMIN' : { 
                 'tablename' : '$dsName',
                 #'tablenameUpper' : True,
                 #'fieldnameUpper' : True,
                 'tablePrefix' : '[ADMIN].',
                 },

    #default.testv1_Calcs
    'default_testv1_' : { 
                 'tablename' : 'testv1_$dsName',
                 #'tablenameUpper' : True,
                 #'tablenameLower' : True,
                 #'fieldnameUpper' : True,
                 'tablePrefix' : '[default].',
                 },

    #testv1_Calcs
    'testv1_' : { 
                 'tablename' : 'testv1_$dsName',
                 #'tablenameUpper' : True,
                 #'tablenameLower' : True,
                 #'fieldnameUpper' : True,
                 #'tablePrefix' : '[default].',
                 'fieldnameDate_underscore' : True,
                 'fieldnameLower_underscore' : True,
                 },

    #testv1_Calcs
    'default_testv1_lower' : { 
                 'tablename' : 'testv1_$dsName',
                 #'tablenameUpper' : True,
                 'tablenameLower' : True,
                 #'fieldnameUpper' : True,
                 'fieldnameDate_underscore' : True,
                 'fieldnameLower_underscore' : True,
                 'tablePrefix' : '[default].',
                 },

    #PUBLIC.Calcs
    'PUBLIC' : { 
                 'tablename' : '$dsName',
                 'tablenameUpper' : True,
                 #'fieldnameUpper' : True,
                 'tablePrefix' : '[PUBLIC].'
                 },

    #Calcs with boolean underscore.
    'bool_' : { 
                 'dbname' : '$testDbName',
                 'tablename' : '$dsName',
                 'bool_underscore' : True
                 },

    #TestV1.Calcs with boolean underscore.
    'prefix_bool_' : { 
                     'tablename' : '$dsName',
                     'schema' : '$testDbName',
                     'tablePrefix' : '[$testDbName].',
                     'bool_underscore' : True
                      },
    #TestV1.Calcs
    'prefix' : { 
                     'tablename' : '$dsName',
                     'schema' : '$testDbName',
                     'tablePrefix' : '[$testDbName].'
                      },
    #Calcs
    'simple' : { 
                     'dbname' : '$testDbName',
                     'tablename' : '$dsName',
                     #'tablePrefix' : '[public].'
                     },

    #calcs
    'simple_lower' : { 
                     'dbname' : '$testDbName',
                     'tablename' : '$dsName',
                     'tablenameLower' : True,
                     #'tablePrefix' : '[public].'
                     },
     #calcs
    'simple_public' : {
                     'dbname' : '$testDbName',
                     'tablename' : '$dsName',
                     #'tablenameLower' : True,
                     'tablePrefix' : '[public].'
                     },
    
    #calcs
    'simple_lower_lower' : { 
                     'dbname' : '$testDbName',
                     'tablename' : '$dsName',
                     'tablenameLower' : True,
                     'fieldnameLower': True,
                     #'tablePrefix' : '[public].'
                     },

    #dbo.Calcs
    'dbo' : { 
                         'dbname' : 'TestV1',
                         'tablename' : '$dsName',
                         'tablePrefix' : '[dbo].'
                         },

    #[TestV1].Calcs 
    'testv1_underscore' : { 
                        'dbname' : 'TestV1',
                        'tablename' : '$dsName',
                        'tablePrefix' : '[TestV1].',
                        'bool_underscore' : True
                 },

    #tactile-pulsar-824:TestV1.Calcs
    'bigquery' : { 
                         'dbname' : 'TestV1',
                         'tablename' : '$dsName',
                         'fieldnameNoSpace' : True,
                         'tablePrefix' : '[tactile-pulsar-824:TestV1].'
                         },


    #tactile-pulsar-824.TestV1.Calcs
    'bigquery_sql' : { 
                         'dbname' : 'TestV1',
                         'tablename' : '$dsName',
                         'fieldnameNoSpace' : True,
                         'tablePrefix' : '[tactile-pulsar-824.TestV1].'
                         },
						 
    #[hive.default].
    'hive_default' : { 
                         'dbname' : 'TestV1',
                         'tablename' : 'testv1_$dsName',
                         'tablenameLower' : True,
                         'fieldnameDate_underscore' : True,
                         'fieldnameLower_underscore' : True,
                         'tablePrefix' : '[hive.testv1_raw].'
                         },
}
