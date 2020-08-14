
# TDVT Error Codes
EXIT_SUCCESS = 0
EXIT_TESTS_FAILED = 1
EXIT_SMOKE_TEST_FAIL = 2
EXIT_NO_TESTS_FOUND = 3
EXIT_DATA_SOURCE_NOT_FOUND = 4
EXIT_TABQUERY_NOT_FOUND = 5
EXIT_BAD_COMMAND = 6

# Tags used by internal CI
SENTRY_TAGS_LIST = [
  'connectorName',
  'dataSourceName',
  'driverName',
  'driverType',
  'email',
  'os',
  'submissionId',
  'submissionTrigger',
  'tableauBranch',
  'tableauVersion',
  'jobId',
  'tdvtTestSuites',
]
