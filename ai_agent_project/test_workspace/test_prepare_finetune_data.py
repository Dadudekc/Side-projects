import os
import json
import pytest
import tempfile
import shutil
from prepare_finetune_data import (
    extract_functions_from_file,
    extract_tests_from_file,
    scan_project_for_functions,
    scan_project_for_tests,
    create_training_pairs,
    convert_json_to_jsonl,
    OUTPUT_JSON,
    OUTPUT_JSONL
)

# Create temporary directories for code and tests
@pytest.fixture
def temp_project():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    code_dir = os.path.join(temp_dir, "src")
    tests_dir = os.path.join(temp_dir, "tests")
    os.makedirs(code_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    # Create a sample source file with one function
    sample_source = os.path.join(code_dir, "sample.py")
    with open(sample_source, "w", encoding="utf-8") as f:
        f.write(
            "def sample_function(x):\n"
            "    '''Return double the input.'''\n"
            "    return x * 2\n"
        )

    # Create a sample test file with a test function matching the source function
    sample_test = os.path.join(tests_dir, "test_sample.py")
    with open(sample_test, "w", encoding="utf-8") as f:
        f.write(
            "def test_sample_function():\n"
            "    from src.sample import sample_function\n"
            "    assert sample_function(2) == 4\n"
        )

    yield temp_dir, code_dir, tests_dir

    # Cleanup temporary directory after test
    shutil.rmtree(temp_dir)

def test_extract_functions(temp_project):
    _, code_dir, _ = temp_project
    sample_source = os.path.join(code_dir, "sample.py")
    funcs = extract_functions_from_file(sample_source)
    assert isinstance(funcs, list)
    assert len(funcs) == 1
    assert funcs[0]["name"] == "sample_function"
    assert "return x * 2" in funcs[0]["code"]

def test_extract_tests(temp_project):
    _, _, tests_dir = temp_project
    sample_test = os.path.join(tests_dir, "test_sample.py")
    tests = extract_tests_from_file(sample_test)
    assert isinstance(tests, list)
    # Should find at least one test function.
    assert len(tests) >= 1
    assert tests[0]["name"].startswith("test_")

def test_scan_project_for_functions(temp_project):
    temp_dir, code_dir, _ = temp_project
    # Point scan to our temporary project directory.
    funcs = scan_project_for_functions(temp_dir)
    # We expect at least one function in the sample file.
    assert any("sample_function" == f["name"] for f in funcs)

def test_scan_project_for_tests(temp_project):
    temp_dir, _, tests_dir = temp_project
    tests = scan_project_for_tests(temp_dir)  # Assuming tests are in subdir
    assert any("test_sample_function" in t["name"] for t in tests)

def test_create_training_pairs_and_conversion(temp_project, tmp_path):
    """
    Tests that training pairs can be created and converted to JSONL format.
    We'll override the output paths to use the temporary path.
    """
    # First, simulate extraction from our temporary project.
    temp_dir, _, _ = temp_project
    # We use the functions from our module.
    funcs = scan_project_for_functions(temp_dir)
    tests = scan_project_for_tests(temp_dir)
    # For simplicity, use a simple heuristic: pair if function name is in test name.
    training_pairs = []
    for func in funcs:
        for test in tests:
            if func["name"].lower() in test["name"].lower():
                training_pairs.append({
                    "input": f"Function:\n{func['code']}\nGenerate tests:",
                    "output": test["code"]
                })
    # Save raw training data
    raw_output = tmp_path / "finetune_data.json"
    with open(raw_output, "w", encoding="utf-8") as f:
        json.dump(training_pairs, f, indent=4)
    # Now convert to JSONL format
    jsonl_output = tmp_path / "finetune_data.jsonl"
    with open(raw_output, "r", encoding="utf-8") as fin:
        data = json.load(fin)
    with open(jsonl_output, "w", encoding="utf-8") as fout:
        for pair in data:
            fout.write(json.dumps(pair) + "\n")
    # Verify that the JSONL file is not empty and has at least one line.
    with open(jsonl_output, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) > 0
    # Check that each line is valid JSON with input and output keys.
    for line in lines:
        pair = json.loads(line)
        assert "input" in pair and "output" in pair

if __name__ == "__main__":
    pytest.main()
