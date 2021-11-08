PERF_CSV_HEADERS = [
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

PERF_CSV_ROW = [
    suite,
    test_set_name,
    test_name,
    tds_name,
    None,
    None,
    perf_iteration,
    None,
    None,
    None,
    passed,
    None,
    None,
    "Query Time",
    "TimeTest",
    case.execution_time
]