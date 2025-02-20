import os
import json
import pytest
from pathlib import Path

# Import the module being tested.
from ai_engine.models.debugger.advanced_init_setup import (
    ProjectContextAnalyzer,
    InitFileSetupManager,
    run_project_setup,
)


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """
    Creates a temporary sample project with the following structure:
    
    sample_project/
      module1/
        file1.py   -> Contains a module-level docstring and an import.
      module2/
        file2.py   -> Contains a module-level docstring and a different import.
      file3.py     -> Contains code without a docstring.
    """
    project_root = tmp_path / "sample_project"
    project_root.mkdir()

    # Create module1 with a Python file containing a docstring and an import.
    module1 = project_root / "module1"
    module1.mkdir()
    file1 = module1 / "file1.py"
    file1.write_text('"""Module 1 docstring"""\nimport os\n', encoding="utf-8")

    # Create module2 with a Python file containing a docstring and an import.
    module2 = project_root / "module2"
    module2.mkdir()
    file2 = module2 / "file2.py"
    file2.write_text('"""Module 2 docstring"""\nfrom sys import exit\n', encoding="utf-8")

    # Create a file at the root with no docstring.
    file3 = project_root / "file3.py"
    file3.write_text("import json\n", encoding="utf-8")

    return project_root


def test_scan_directories(sample_project: Path):
    analyzer = ProjectContextAnalyzer(str(sample_project))
    analyzer.scan_directories()
    package_dirs = analyzer.get_package_dirs()
    expected_dirs = {
        os.path.abspath(str(sample_project)),
        os.path.abspath(str(sample_project / "module1")),
        os.path.abspath(str(sample_project / "module2")),
    }
    # All expected directories should be present in package_dirs.
    assert expected_dirs.issubset(package_dirs)


def test_extract_code_context(sample_project: Path):
    analyzer = ProjectContextAnalyzer(str(sample_project))
    analyzer.scan_directories()
    analyzer.extract_code_context()
    analysis = analyzer.get_analysis_data()

    # file1.py should have its docstring extracted.
    file1_key = os.path.join("module1", "file1.py")
    assert "Module 1 docstring" in analysis["modules"][file1_key]["purpose"]

    # file3.py has no docstring; should return the default message.
    assert analysis["modules"]["file3.py"]["purpose"] == "No docstring found."


def test_map_dependencies(sample_project: Path):
    analyzer = ProjectContextAnalyzer(str(sample_project))
    analyzer.scan_directories()
    analyzer.map_dependencies()
    analysis = analyzer.get_analysis_data()

    # file1.py should have "os" as a dependency.
    file1_key = os.path.join("module1", "file1.py")
    dependencies1 = analysis["modules"][file1_key]["dependencies"]
    assert "os" in dependencies1

    # file2.py should have a dependency from the import from sys.
    file2_key = os.path.join("module2", "file2.py")
    dependencies2 = analysis["modules"][file2_key]["dependencies"]
    # Depending on AST parsing, we expect either "sys" or "sys.exit" in the dependency list.
    assert any("sys" in dep for dep in dependencies2)


def test_save_analysis(tmp_path: Path):
    # Create a simple project with one file.
    project_root = tmp_path / "sample_project"
    project_root.mkdir()
    test_file = project_root / "test.py"
    test_file.write_text('print("Hello")', encoding="utf-8")

    analyzer = ProjectContextAnalyzer(str(project_root))
    analyzer.scan_directories()
    analyzer.extract_code_context()
    analyzer.map_dependencies()
    analyzer.save_analysis()

    analysis_file = project_root / "project_analysis.json"
    assert analysis_file.exists()

    with analysis_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert "modules" in data


def test_init_file_setup_manager(tmp_path: Path):
    # Create a project with a module missing __init__.py.
    project_root = tmp_path / "sample_project"
    project_root.mkdir()
    module_dir = project_root / "module"
    module_dir.mkdir()
    test_file = module_dir / "test.py"
    test_file.write_text('print("Hello")', encoding="utf-8")

    analyzer = ProjectContextAnalyzer(str(project_root))
    analyzer.scan_directories()
    # For __init__.py creation, we don't need to run extract_code_context or map_dependencies.
    setup_manager = InitFileSetupManager(analyzer)
    setup_manager.setup_init_files()

    init_file = module_dir / "__init__.py"
    assert init_file.exists()
    content = init_file.read_text(encoding="utf-8")
    assert "# Automatically generated __init__.py" in content
    # Check that the package metadata (docstring) is included.
    assert "Package:" in content


def test_run_project_setup(tmp_path: Path):
    # Test the wrapper function that runs both analysis and init file setup.
    project_root = tmp_path / "sample_project"
    project_root.mkdir()
    module_dir = project_root / "module"
    module_dir.mkdir()
    test_file = module_dir / "test.py"
    test_file.write_text('print("Hello")', encoding="utf-8")

    run_project_setup(str(project_root))

    # Verify that the analysis JSON file was created.
    analysis_file = project_root / "project_analysis.json"
    assert analysis_file.exists()

    # Verify that __init__.py was created in the module directory.
    init_file = module_dir / "__init__.py"
    assert init_file.exists()
