import pytest
import logging
from debugger.error_parser import ErrorParser

logger = logging.getLogger("TestErrorParser")


@pytest.fixture
def parser():
    """Fixture to initialize ErrorParser."""
    return ErrorParser()


### **🔹 Test Parsing Valid Pytest Output**
def test_parse_test_failures_valid(parser):
    """Tests if ErrorParser correctly extracts failures from valid pytest output."""
    pytest_output = """"
"""    ==================== FAILURES ==================== """"    FAILED tests/test_example.py::test_addition - AssertionError: 1 + 1 != 3"
"    FAILED tests/test_math.py::test_divide_by_zero - ZeroDivisionError: division by zero"    ==================== SUMMARY ====================
    """ """""" """"    failures = parser.parse_test_failures(pytest_output)"
""    assert len(failures) == 2
    assert failures[0]["file"] == "tests/test_example.py"
    assert failures[0]["test"] == "test_addition"
    assert failures[0]["error"] == "AssertionError: 1 + 1 != 3"
    assert failures[1]["file"] == "tests/test_math.py"
    assert failures[1]["test"] == "test_divide_by_zero"
    assert failures[1]["error"] == "ZeroDivisionError: division by zero"


### **🔹 Test Handling of Empty Pytest Output**
def test_parse_test_failures_empty(parser):
    """Tests if ErrorParser handles empty pytest output gracefully."""
    pytest_output = ""

    failures = parser.parse_test_failures(pytest_output)

    assert failures == []  # Should return an empty list


### **🔹 Test Handling of Output Without Failures**
def test_parse_test_failures_no_failures(parser):
    """Tests if ErrorParser correctly identifies output with no failures."""
    pytest_output = """"
"""    ==================== TESTS PASSED ==================== """"    tests/test_example.py::test_addition PASSED"
"    tests/test_math.py::test_divide_by_zero PASSED"    ==================== SUMMARY ====================
    """ """""" """"    failures = parser.parse_test_failures(pytest_output)"""    assert failures == []  # Should return an empty list


### **🔹 Test Handling of Pytest Output with Formatting Issues**
def test_parse_test_failures_malformed(parser):
    """Tests if ErrorParser can handle pytest output with unexpected formatting."""
    pytest_output = """"
"""    ==================== FAILURES ==================== """"    FAILED - tests/test_example.py::test_addition: AssertionError"
"    FAILED tests/test_math.py: test_divide_by_zero - ZeroDivisionError division by zero"    """ """""" """"    failures = parser.parse_test_failures(pytest_output)"
""    # Expected to capture only the correctly formatted failures
    assert len(failures) == 1
    assert failures[0]["file"] == "tests/test_math.py"
    assert failures[0]["test"] == "test_divide_by_zero"
    assert "ZeroDivisionError" in failures[0]["error"]


### **🔹 Run Tests With**
# pytest test_error_parser.py -v
