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

CALCS_EXPRESSION_EXCLUSIONS = [
    '[bool0_]',
    '[bool1_]',
    '[bool2_]',
    '[bool3_]'
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

# Constants for custom test generation
TEST_ARGUMENT_DATA_TYPES = {
    'key': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'VARCHAR',
    },
    'num0': {
        'empties': False,
        'negatives': True,
        'nulls': True,
        'type': 'FLOAT',
    },
    'num1': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'FLOAT',
    },
    'num2': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'FLOAT',
    },
    'num3': {
        'empties': False,
        'negatives': True,
        'nulls': False,
        'type': 'FLOAT',
    },
    'num4': {
        'empties': False,
        'negatives': True,
        'nulls': True,
        'type': 'FLOAT',
    },
    'str0': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'VARCHAR',
    },
    'str1': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'VARCHAR',
    },
    'str2': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'VARCHAR',
    },
    'str3': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'VARCHAR',
    },
    'int0': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'INTEGER',
    },
    'int1': {
        'empties': False,
        'negatives': True,
        'nulls': True,
        'type': 'INTEGER',
    },
    'int2': {
        'empties': False,
        'negatives': True,
        'nulls': False,
        'type': 'INTEGER',
    },
    'int3': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'INTEGER',
    },
    'bool0': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'BOOLEAN',
    },
    'bool1': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'BOOLEAN',
    },
    'bool2': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'BOOLEAN',
    },
    'bool3': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'BOOLEAN',
    },
    'date0': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'DATE',
    },
    'date1': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'DATE',
    },
    'date2': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'DATE',
    },
    'date3': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'DATE',
    },
    'time0': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'TIMESTAMP',
    },
    'time1': {
        'empties': False,
        'negatives': False,
        'nulls': True,
        'type': 'TIME',
    },
    'datetime0': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'TIMESTAMP',
    },
    'datetime1': {
        'empties': True,
        'negatives': False,
        'nulls': True,
        'type': 'VARCHAR',
    },
    'zzz': {
        'empties': False,
        'negatives': False,
        'nulls': False,
        'type': 'VARCHAR',
    },
}

CUSTOM_TABLE_TEST_SET = {
    # the dict keys align with the name of test sets in tdvt/exprtests/standard
    # the keys are used to find the test files (e.g. setup.agg) in tdvt/exprtests/standard
    'agg': {
        'nice_name': 'Aggregation',
        'description': 'tests aggregation functions including sum, count, avg, min, max, and distinct',
        'url_for_docs': 'https://tableau.github.io/connector-plugin-sdk/docs/tdvt#agg-suite',
    },
    'cast': {
        'nice_name': 'Cast',
        'description': 'tests casting functions',
        'url_for_docs': 'https://tableau.github.io/connector-plugin-sdk/docs/tdvt#cast-suite',
    },
    'date': {
        'nice_name': 'Date',
        'description': 'tests date functions max, min, misc, today, and cast',
        'url_for_docs': 'https://tableau.github.io/connector-plugin-sdk/docs/tdvt#date-suite',
    },
    'math': {
        'nice_name': 'Math',
        'description': 'tests a variety of math functions',
        'url_for_docs': 'https://tableau.github.io/connector-plugin-sdk/docs/tdvt#math-suite',
    },
    'operator': {
        'nice_name': 'Operator',
        'description': 'tests operator functions bool, date, int, num, and str',
        'url_for_docs': 'https://tableau.github.io/connector-plugin-sdk/docs/tdvt#operator-suite',
    },
    'string': {
        'nice_name': 'String',
        'description': 'tests a variety of string functions',
        'url_for_docs': 'https://tableau.github.io/connector-plugin-sdk/docs/tdvt#string-suite',
    }
}

CUSTOM_TABLE_EXPRESSION_TEST_EXCLUSIONS = (
    # a list of (expression [for now]) test sets that should be excluded
    # these tests have hard-coded args (e.g. strings) that were chosen specifically
    # for data in cast_calcs.
    # This is a tuple because the str.startswith() method won't take a list.
    'setup.date.cast',
    'setup.date.dateadd',
    'setup.date.datediff',
    'setup.date.datename',
    'setup.date.datepart',
    'setup.date.datetrunc',
    'setup.date.datetrunc',
    'setup.operator.str',
    'setup.string.contains',
    'setup.string.endswith',
    'setup.string.find',
    'setup.string.space',
    'setup.string.startswith',
)

# Constants for CSV output
DEFAULT_CSV_HEADERS = [
    'Suite',
    'Test Set',
    'TDSName',
    'TestName',
    'TestPath',
    'Passed',
    'Closest Expected',
    'Diff count',
    'Test Case',
    'Test Type',
    'Priority',
    'Categories',
    'Functions',
    'Process Output',
    'Error Msg',
    'Error Type',
    'Query Time (ms)',
    'Generated SQL',
]

PERFLAB_CSV_HEADERS = [
    "TestGroup",
    "TestSubGroup",
    "Test",
    "TestComment1",
    "TestComment2",
    "TestComment3",
    "Iteration",
    "IterationStartTime",
    "IterationEndTime",
    "ErrorString",
    "IterationComment1",
    "IterationComment2",
    "IterationComment3",
    "MetricResourceType",
    "MetricResourceInstance",
    "Result"
]

TUPLE_DISPLAY_LIMIT = 100
