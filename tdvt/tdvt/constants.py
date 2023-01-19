# Constants for test generation
CALCS_FIELDS = [
    '[key]',
    '[num0]',
    '[num1]',
    '[num2]',
    '[num3]',
    '[num4]',
    '[str0]',
    '[str1]',
    '[str2]',
    '[str3]',
    '[int0]',
    '[int1]',
    '[int2]',
    '[int3]',
    '[bool0]',
    '[bool1]',
    '[bool2]',
    '[bool3]',
    '[bool0_]',
    '[bool1_]',
    '[bool2_]',
    '[bool3_]',
    '[date0]',
    '[date1]',
    '[date2]',
    '[date3]',
    '[time0]',
    '[time1]',
    '[datetime0]',
    '[datetime1]',
    '[zzz]'
]

STAPLES_FIELDS = [
    '[Item Count]',
    '[Ship Priority]',
    '[Order Priority]',
    '[Order Status]',
    '[Order Quantity]',
    '[Sales Total]',
    '[Discount]',
    '[Tax Rate]',
    '[Ship Mode]',
    '[Fill Time]',
    '[Gross Profit]',
    '[Price]',
    '[Ship Handle Cost]',
    '[Employee Name]',
    '[Employee Dept]',
    '[Manager Name]',
    '[Employee Yrs Exp]',
    '[Employee Salary]',
    '[Customer Name]',
    '[Customer State]',
    '[Call Center Region]',
    '[Customer Balance]',
    '[Customer Segment]',
    '[Prod Type1]',
    '[Prod Type2]',
    '[Prod Type3]',
    '[Prod Type4]',
    '[Product Name]',
    '[Product Container]',
    '[Ship Promo]',
    '[Supplier Name]',
    '[Supplier Balance]',
    '[Supplier Region]',
    '[Supplier State]',
    '[Order ID]',
    '[Order Year]',
    '[Order Month]',
    '[Order Day]',
    '[Order Date]',
    '[Order Quarter]',
    '[Product Base Margin]',
    '[Product ID]',
    '[Receive Time]',
    '[Received Date]',
    '[Ship Date]',
    '[Ship Charge]',
    '[Total Cycle Time]',
    '[Product In Stock]',
    '[PID]',
    '[Market Segment]'
]

DATA_TYPES = {
    'string': '&quot;',
    'datetime': '#',
    'date': '#',
    'time': '#'
}

DATA_SHAPES = {

}

TEST_ARGUMENT_DATA_TYPES = {
    'key': {
        'type': 'VARCHAR',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'num0': {
        'type': 'FLOAT',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'True',
    },
    'num1': {
        'type': 'FLOAT',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'num2': {
        'type': 'FLOAT',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'num3': {
        'type': 'FLOAT',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'True',
    },
    'num4': {
        'type': 'FLOAT',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'True',
    },
    'str0': {
        'type': 'VARCHAR',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'str1': {
        'type': 'VARCHAR',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'str2': {
        'type': 'VARCHAR',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'str3': {
        'type': 'VARCHAR',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'int0': {
        'type': 'INTEGER',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'int1': {
        'type': 'INTEGER',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'True',
    },
    'int2': {
        'type': 'INTEGER',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'True',
    },
    'int3': {
        'type': 'INTEGER',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'bool0': {
        'type': 'INTEGER',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'bool1': {
        'type': 'INTEGER',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'bool2': {
        'type': 'INTEGER',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'bool3': {
        'type': 'INTEGER',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'date0': {
        'type': 'DATE',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'date1': {
        'type': 'DATE',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'date2': {
        'type': 'DATE',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'date3': {
        'type': 'DATE',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'time0': {
        'type': 'TIMESTAMP',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'time1': {
        'type': 'TIME',
        'data_shape': 'no_empties_contains_nulls',
        'alts': 'False',
    },
    'datetime0': {
        'type': 'TIMESTAMP',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
    'datetime1': {
        'type': 'VARCHAR',
        'data_shape': 'contains_empties_contains_nulls',
        'alts': 'False',
    },
    'zzz': {
        'type': 'VARCHAR',
        'data_shape': 'no_empties_no_nulls',
        'alts': 'False',
    },
}

CUSTOM_TABLE_TEST_SET = {
    'agg': {
        'nice_name': 'Aggregation',
        'description of the suite': 'blah',
        'url_for_docs': 'https://blah.com',
            },
    'cast': {
        'nice_name': 'Cast',
        'description of the suite': 'blah',
        'url_for_docs': 'https://blah.com',
    },
    'date': {
        'nice_name': 'Date',
        'description of the suite': 'blah',
        'url_for_docs': 'https://blah.com',
    },
    'math': {
        'nice_name': 'Math',
        'description of the suite': 'blah',
        'url_for_docs': 'https://blah.com',
    },
    'operator': {
        'nice_name': 'Operator',
        'description of the suite': 'blah',
        'url_for_docs': 'https://blah.com',
    },
    'string': {
        'nice_name': 'String',
        'description of the suite': 'blah',
        'url_for_docs': 'https://blah.com',
    }
}
