import os
import json
import pytest
from ai_test_agent import AITestAgent, GENERATED_TESTS_FILE, FUNCTION_MAP_FILE

@pytest.fixture
def test_agent():
    return AITestAgent()

def test_run_coverage(test_agent):
    """Ensure that coverage analysis runs and returns output."""
    output = test_agent.run_coverage()
    assert output is not None and len(output) > 0, "Coverage output is empty."

def test_load_function_map(test_agent):
    """Ensure the function map loads or is created."""
    if os.path.exists(FUNCTION_MAP_FILE):
        os.remove(FUNCTION_MAP_FILE)
    functions = test_agent.load_function_map()
    assert isinstance(functions, list), "Function map should be a list."
    assert len(functions) > 0, "Function map should not be empty."

def test_generate_tests_for_function(test_agent):
    """Ensure AI generates valid test code for a sample function."""
    sample_function = {
        "name": "sample_function",
        "file": "sample.py",
        "code": "def sample_function(x):\n    return x * 2"
    }
    test_code = test_agent.generate_tests_for_function(sample_function)
    assert test_code is not None, "Generated test code is None."
    assert "def test_" in test_code, "Generated test should contain a test function definition."

def test_save_and_run_generated_tests(test_agent):
    """Ensure that generated tests are saved properly and run without failures."""
    if os.path.exists(GENERATED_TESTS_FILE):
        os.remove(GENERATED_TESTS_FILE)
    sample_test_code = "def test_sample():\n    assert 1 == 1"
    test_agent.save_generated_tests(sample_test_code)
    with open(GENERATED_TESTS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    assert "def test_sample():" in content, "Generated test not saved properly."
    
    result = test_agent.run_generated_tests()
    assert "FAILED" not in result, "Generated tests should pass."

def test_debug_failed_tests(test_agent):
    """Ensure that debug suggestions are generated for a fake error log."""
    fake_error_log = "FAILED test_sample.py::test_example - AssertionError"
    suggestions = test_agent.debug_failed_tests(fake_error_log)
    assert suggestions is not None and len(suggestions) > 0, "No debug suggestions generated."

if __name__ == "__main__":
    pytest.main()
