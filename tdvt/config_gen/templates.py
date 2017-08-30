"""
This defines a mapping to the table and columns in the datasource. It is used to generate a set of logical query tests that will work with the peculiarities of the data source.

You can run [tdvt --list_logical_configs] to see the resulting values.

The value on the left is the key that is used in your datasource ini file. THESE VALUES ARE CASE INSENSITIVE!
Keys you can set to control the generation are:

This should always be present. $dsName will be replaced with Calcs or Staples. You can put a string before the $dsName token to append something to your table name but if you want to set something on the end you need to use tablenamePostfix.
     'tablename' : '$dsName',

To change the table name: Say your table is called 'test_Calcs_view'. You can achieve this by setting:
     'tablename' : 'test_$dsName'
     'tablenamePostfix' : '_view',

This is prefixed to the table name.
     'tablePrefix' : '[TESTV1].',

Upper cases all table name.
     'tablenameUpper' : True,

Lower case table names.
     'tablenameLower' : True,

If the table has `Date_` instead of `Date` columns.
     'fieldnameDate_underscore' : True,

Field name is lower and contains underscores instead of spaces.
     'fieldnameLower_underscore' : True,

Do the `Bool0` fields look like `Bool0_`?
     'bool_underscore' : True

Instead of a space there is nothing. Ie ' ' vs ''.
     'fieldnameNoSpace' : True,

Instead of a space there is an underscore.
     'fieldnameUnderscoreNotSpace' : True,

Uppercase field names:
    'fieldnameUpper' : True

"""


global template_attributes
template_attributes = {

    #TESTV1.Calcs
    'TESTV1' : { 
                 'tablename' : '$dsName',
                 'tablePrefix' : '[TESTV1].',
                 },
	#[Extract].[Extract]
    'Extract' : { 
                 'tablename' : 'Extract',
                 'tablePrefix' : '[Extract].',
                 },

    'TESTV1_TESTV1' : { 
                 'tablename' : '$dsName',
                 'tablenamePrefix' : 'TESTV1_',
                 'tablePrefix' : '[TESTV1].',
                 'tablenameUpper' : True,
                 'fieldnameDate_underscore' : True,
                 'fieldnameUnderscoreNotSpace' : True,
                 'fieldnameUpper' : True,
                 },

    #TEST.Calcs
    'TEST' : { 
                 'tablename' : '$dsName',
                 'tablePrefix' : '[TEST].',
                 },

    #test.Calcs
    'test_lower' : { 
                 'tablename' : '$dsName',
                 'tablePrefix' : '[test].',
                 },

    #ADMIN.Calcs
    'ADMIN' : { 
                 'tablename' : '$dsName',
                 'tablePrefix' : '[ADMIN].',
                 },

    #admin.calcs
    'admin_lower' : {
                'tablename' : '$dsName',
                'calcsnameLower' : True,
                'tablePrefix' : '[admin].'
                },

    #default.testv1_Calcs
    'default_testv1_' : { 
                 'tablename' : '$dsName',
                 'tablenamePrefix' : 'testv1_',
                 'tablePrefix' : '[default].',
                 },

    #testv1_Calcs
    'testv1_' : { 
                 'tablename' : '$dsName',
                 'tablenamePrefix' : 'testv1_',
                 'fieldnameDate_underscore' : True,
                 'fieldnameLower_underscore' : True,
                 },

    #testv1_Calcs
    'default_testv1_lower' : { 
                 'tablename' : '$dsName',
                 'tablenamePrefix' : 'testv1_',
                 'tablenameLower' : True,
                 'fieldnameDate_underscore' : True,
                 'fieldnameLower_underscore' : True,
                 'tablePrefix' : '[default].',
                 },

    #PUBLIC.Calcs
    'PUBLIC' : { 
                 'tablename' : '$dsName',
                 'tablenameUpper' : True,
                 'tablePrefix' : '[PUBLIC].'
                 },

    #Calcs with boolean underscore.
    'bool_' : { 
                 'tablename' : '$dsName',
                 'bool_underscore' : True
                 },

    'bool_lower' : { 
                     'tablename' : '$dsName',
                     'tablenameLower' : True,
                     'bool_underscore' : True
                 },

    #TestV1.Calcs with boolean underscore.
    'prefix_bool_' : { 
                     'tablename' : '$dsName',
                     'tablePrefix' : '[TestV1].',
                     'bool_underscore' : True
                      },
    #TestV1.Calcs
    'prefix' : { 
                     'tablename' : '$dsName',
                     'tablePrefix' : '[TestV1].'
                      },
    #testv1.Calcs
    'prefix_bool_lower' : { 
                     'tablename' : '$dsName',
                     'tablePrefix' : '[testv1].',
                     'bool_underscore' : True
                      },
    #Calcs
    'simple' : { 
                     'tablename' : '$dsName',
                     },

    #calcs
    'simple_lower' : { 
                     'tablename' : '$dsName',
                     'tablenameLower' : True,
                     },
     #calcs
    'simple_public' : {
                     'tablename' : '$dsName',
                     'tablePrefix' : '[public].'
                     },
    
    #calcs
    'simple_lower_lower' : { 
                     'tablename' : '$dsName',
                     'tablenameLower' : True,
                     'fieldnameLower': True,
                     },

    'dbadmin_underscore' : { 
                     'tablename' : '$dsName',
                     'tablePrefix' : '[dbadmin].',
                     'tablenameLower' : True,
                     'fieldnameLower': True,
                     'bool_underscore' : True
                     },

    #dbo.Calcs
    'dbo' : { 
                         'tablename' : '$dsName',
                         'tablePrefix' : '[dbo].'
                         },

    #[TestV1].Calcs 
    'testv1_underscore' : { 
                        'tablename' : '$dsName',
                        'tablePrefix' : '[TestV1].',
                        'bool_underscore' : True
                 },

    #tactile-pulsar-824:TestV1.Calcs
    'bigquery' : { 
                         'tablename' : '$dsName',
                         'fieldnameNoSpace' : True,
                         'tablePrefix' : '[tactile-pulsar-824:TestV1].'
                         },


    #tactile-pulsar-824.TestV1.Calcs
    'bigquery_sql' : { 
                         'tablename' : '$dsName',
                         'fieldnameNoSpace' : True,
                         'tablePrefix' : '[tactile-pulsar-824.TestV1].'
                         },

    'bigquery_sql_datetime' : { 
                         'tablename' : '$dsName',
                         'fieldnameNoSpace' : True,
                         'tablePrefix' : '[tactile-pulsar-824.TestV1].',
                         'tablenamePostfix' : 'DateTime',
                         },
						 
    #[hive.default].
    'hive_default' : { 
                         'tablename' : '$dsName',
                         'tablenamePrefix' : 'testv1_',
                         'tablenameLower' : True,
                         'fieldnameDate_underscore' : True,
                         'fieldnameLower_underscore' : True,
                         'tablePrefix' : '[hive.testv1_raw].'
                         },

    'default_lower' : { 
                         'tablename' : '$dsName',
                         'tablenameLower' : True,
                         'tablePrefix' : '[DEFAULT].'
                         },

    'testv1_testv1_lower' : { 
                 'tablename' : '$dsName',
                 'tablenamePrefix' : 'testv1_',
                 'tablenameLower' : True,
                 'fieldnameDate_underscore' : True,
                 'fieldnameLower_underscore' : True,
                 'tablePrefix' : '[testv1].',
                 },

    'view_lower' : { 
                 'tablename' : '$dsName',
                 'tablenamePostfix' : '_view',
                 'tablenameLower' : True,
                 'tablePrefix' : '[testv1].',
                 'fieldnameLower_underscore' : True,
                 'bool_underscore' : True
                 },

    'redshift_spectrum_partitioned' : {
                'tablename' : '$dsName',
                'tablenamePostfix' : '_partition',
                'tablenameLower' : True,
                'tablePrefix' : '[testv1spectrum].',
                'fieldnameDate_underscore' : True,
                'fieldnameLower_underscore' : True
                },

    'redshift_spectrum_unpartitioned' : {
                'tablename' : '$dsName',
                'tablenamePrefix' : 'testv1_',
                'tablenameLower' : True,
                'tablePrefix' : '[testv1spectrum].',
                'fieldnameDate_underscore' : True,
                'fieldnameLower_underscore' : True
                },
}
