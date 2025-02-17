import json
import os
import shutil

import pytest

from ai_engine.models.debugger.project_context_analyzer import ProjectContextAnalyzer

# Define a temporary test project structure
TEST_PROJECT_ROOT = "test_project"


@pytest.fixture(scope="function")
def setup_test_project():
    """Sets up a mock Python project for testing."""
    if os.path.exists(TEST_PROJECT_ROOT):
        shutil.rmtree(TEST_PROJECT_ROOT)  # Clean up before running test
    os.makedirs(TEST_PROJECT_ROOT)

    # Create dummy Python modules with dependencies
    os.makedirs(os.path.join(TEST_PROJECT_ROOT, "module1"))
    os.makedirs(os.path.join(TEST_PROJECT_ROOT, "module2"))
    os.makedirs(os.path.join(TEST_PROJECT_ROOT, "module3"))

    # Create test Python files
    test_files = {
        "module1/file1.py": '"""This is Module 1."""\nimport module2.file2\nfrom module3 import missing_module\n',
        "module2/file2.py": '"""This is Module 2."""\nimport os\nimport sys\n',
        "module3/file3.py": '"""This is Module 3."""\n',
    }

    for filename, content in test_files.items():
        file_path = os.path.join(TEST_PROJECT_ROOT, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    yield TEST_PROJECT_ROOT  # Provide the test directory for the test

    # Clean up after the test
    shutil.rmtree(TEST_PROJECT_ROOT)


# ** Test Directory Scanning **
def test_directory_scanning(setup_test_project):
    """Tests that Python files are detected correctly."""
    analyzer = ProjectContextAnalyzer(setup_test_project)
    analyzer.scan_directories()

    detected_files = set(analyzer.context_data["modules"].keys())

    expected_files = {"module1/file1.py", "module2/file2.py", "module3/file3.py"}
    assert (
        detected_files == expected_files
    ), f"Expected {expected_files}, but got {detected_files}"
    print("✅ Test passed: Directory scanning works correctly.")


# ** Test Docstring Extraction **
def test_docstring_extraction(setup_test_project):
    """Tests that docstrings are correctly extracted from Python files."""
    analyzer = ProjectContextAnalyzer(setup_test_project)
    analyzer.scan_directories()
    analyzer.extract_code_context()

    assert (
        analyzer.context_data["modules"]["module1/file1.py"]["purpose"]
        == "This is Module 1."
    )
    assert (
        analyzer.context_data["modules"]["module2/file2.py"]["purpose"]
        == "This is Module 2."
    )
    assert (
        analyzer.context_data["modules"]["module3/file3.py"]["purpose"]
        == "This is Module 3."
    )

    print("✅ Test passed: Docstring extraction works correctly.")


# ** Test Dependency Mapping **
def test_dependency_mapping(setup_test_project):
    """Tests that module dependencies are correctly detected."""
    analyzer = ProjectContextAnalyzer(setup_test_project)
    analyzer.scan_directories()
    analyzer.map_dependencies()

    dependencies = analyzer.context_data["modules"]["module1/file1.py"]["dependencies"]
    assert "module2.file2" in dependencies
    assert "module3.missing_module" in dependencies

    dependencies = analyzer.context_data["modules"]["module2/file2.py"]["dependencies"]
    assert "os" in dependencies
    assert "sys" in dependencies

    print("✅ Test passed: Dependency mapping works correctly.")


# ** Test Project Analysis Save **
def test_project_analysis_save(setup_test_project):
    """Tests that project analysis is saved to a JSON file."""
    analyzer = ProjectContextAnalyzer(setup_test_project)
    analyzer.analyze_project()

    json_path = os.path.join(setup_test_project, "project_analysis.json")
    assert os.path.exists(json_path), "Expected project analysis file to be created."

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "modules" in data
    assert "dependencies" in data
    assert "summary" in data

    print("✅ Test passed: Project analysis is saved correctly.")


# Run with: `pytest test_project_context_analyzer.py -v`
