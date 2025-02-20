"""
advanced_init_setup.py

This module integrates project analysis with automatic __init__.py setup.
It defines two main classes:

  1. ProjectContextAnalyzer:
     - Scans a Python project for modules.
     - Extracts module-level docstrings and maps dependencies.
     - Saves the analysis results (metadata) to a JSON file.
     - Provides package-level metadata for directories.

  2. InitFileSetupManager:
     - Uses the analysis from ProjectContextAnalyzer to determine which directories
       should be treated as Python packages.
     - Creates missing __init__.py files in those directories.
     - Optionally includes metadata (e.g. extracted docstrings) in the generated __init__.py files.

This advanced setup can be used by your debugger to “understand” the project context and
improve automated repairs by providing a guide to the project structure and intent.
"""

import os
import json
import logging
import ast
from typing import Dict, Any, Set, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ProjectContextAnalyzer:
    """
    Analyzes a given Python project.

    The analysis includes:
      - Scanning project directories for Python files.
      - Extracting module-level docstrings as a proxy for module purpose.
      - Mapping module dependencies (via AST analysis).
      - Saving the analysis results to a JSON file in the project root.
    """

    def __init__(self, project_root: str) -> None:
        """
        Initialize the analyzer.

        Args:
            project_root (str): Path to the root of the project.
        """
        self.project_root: str = project_root
        self.context_data: Dict[str, Any] = {"modules": {}, "dependencies": {}, "summary": {}}
        self.package_dirs: Set[str] = set()

    def scan_directories(self) -> None:
        """Recursively scans the project directory for Python files."""
        logger.info("📂 Scanning project directories for Python files...")
        for root, _, files in os.walk(self.project_root):
            # Skip hidden files
            files = [f for f in files if not f.startswith('.')]
            if any(f.endswith(".py") for f in files):
                rel_path = os.path.relpath(root, self.project_root)
                norm_path = rel_path.replace("\\", "/")
                self.package_dirs.add(os.path.abspath(root))
                # Initialize module info for each Python file in this directory
                for file in files:
                    if file.endswith(".py"):
                        module_rel_path = os.path.join(norm_path, file) if norm_path != "." else file
                        self.context_data["modules"][module_rel_path] = {"dependencies": []}

    def extract_code_context(self) -> None:
        """
        Extracts module-level docstrings (if present) from each Python file.
        For each module, stores a "purpose" field in the context data.
        """
        logger.info("📜 Extracting docstrings and code context...")
        for module_path in self.context_data["modules"].keys():
            abs_path = os.path.join(self.project_root, module_path)
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Look for a module-level docstring (triple-quoted string at the top)
                docstring: Optional[str] = None
                if content.startswith('"""'):
                    end = content.find('"""', 3)
                    if end != -1:
                        docstring = content[3:end].strip()
                self.context_data["modules"][module_path]["purpose"] = docstring or "No docstring found."
            except Exception as e:
                logger.error(f"Failed to extract docstring from {module_path}: {e}")
                self.context_data["modules"][module_path]["purpose"] = "Error extracting docstring."

    def map_dependencies(self) -> None:
        """Parses each Python file and extracts import dependencies using AST."""
        logger.info("🔗 Mapping module dependencies...")
        for module_path in self.context_data["modules"].keys():
            abs_path = os.path.join(self.project_root, module_path)
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source, filename=module_path)
                dependencies = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            dependencies.add(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        for alias in node.names:
                            dependencies.add(f"{node.module}.{alias.name}")
                self.context_data["modules"][module_path]["dependencies"] = sorted(dependencies)
            except Exception as e:
                logger.error(f"Error mapping dependencies in {module_path}: {e}")
                self.context_data["modules"][module_path]["dependencies"] = []

    def save_analysis(self) -> None:
        """Saves the analysis results to a JSON file in the project root."""
        output_path = os.path.join(self.project_root, "project_analysis.json")
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(self.context_data, f, indent=4)
            logger.info(f"📄 Analysis saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save analysis to {output_path}: {e}")

    def analyze_project(self) -> None:
        """Runs a full analysis of the project."""
        logger.info("📊 Analyzing project structure...")
        self.scan_directories()
        self.extract_code_context()
        self.map_dependencies()
        self.save_analysis()
        logger.info("✅ Project analysis completed!")

    def get_analysis_data(self) -> Dict[str, Any]:
        """Returns the full analysis data as a dictionary."""
        return self.context_data

    def get_package_dirs(self) -> Set[str]:
        """Returns the set of directories (absolute paths) that contain Python files."""
        return self.package_dirs

    def get_docstring_for_directory(self, directory: str) -> str:
        """
        Returns a package docstring based on the directory name or analysis data.
        For now, returns a placeholder value.

        Args:
            directory (str): The absolute path to the directory.
        
        Returns:
            str: A package-level docstring.
        """
        return f'"""Package: {os.path.basename(directory)} - Auto-generated init file."""'


class InitFileSetupManager:
    """
    Uses the analysis provided by ProjectContextAnalyzer to automatically create missing
    __init__.py files in directories that contain Python modules.

    It can include additional metadata (e.g. a package docstring) in the generated __init__.py files.
    """

    def __init__(self, analyzer: ProjectContextAnalyzer, default_header: str = "# Automatically generated __init__.py\n") -> None:
        """
        Args:
            analyzer (ProjectContextAnalyzer): The analyzer with project context.
            default_header (str): Default header content for __init__.py files.
        """
        self.analyzer = analyzer
        self.default_header = default_header

    def setup_init_files(self) -> None:
        """
        Iterates over all package directories (from the analyzer) and creates __init__.py
        files where they are missing. If available, includes extracted metadata in the file.
        """
        package_dirs = self.analyzer.get_package_dirs()
        logger.info(f"Setting up __init__.py files in {len(package_dirs)} directories...")
        for directory in package_dirs:
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                # Optionally, include additional metadata for this package.
                metadata = self.analyzer.get_docstring_for_directory(directory)
                content = self.default_header + (metadata + "\n" if metadata else "")
                self._create_init_file(init_file, content)

    def _create_init_file(self, file_path: str, content: str) -> None:
        """
        Creates an __init__.py file with the specified content.

        Args:
            file_path (str): The path to the __init__.py file.
            content (str): The content to write in the file.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Created __init__.py at {file_path}")
        except Exception as e:
            logger.error(f"Failed to create __init__.py at {file_path}: {e}")


def run_project_setup(project_root: Optional[str] = None) -> None:
    """
    Runs the project analysis and then sets up missing __init__.py files based on the analysis.
    
    Args:
        project_root (str, optional): The project root directory. Defaults to current working directory.
    """
    if project_root is None:
        project_root = os.getcwd()
    logger.info(f"Running project setup for: {project_root}")

    analyzer = ProjectContextAnalyzer(project_root)
    analyzer.analyze_project()

    setup_manager = InitFileSetupManager(analyzer)
    setup_manager.setup_init_files()


if __name__ == "__main__":
    import sys
    # Use command-line argument as project root, if provided
    root_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    run_project_setup(root_dir)
