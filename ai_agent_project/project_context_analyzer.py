"""

This module defines a class `ProjectContextAnalyzer` used for analyzing a given Python project.
The analysis includes scanning project directories for Python files, extracting module-level docstrings 
and other metadata, mapping module dependencies and saving the analysis results to a JSON file in the project root directory.

The class includes the following methods:
- __init__: Initialises the class. Accepts 'project_root' as an argument which should represent the path to the root of the project.
- scan_directories: Sc
"""

import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("ProjectContextAnalyzer")
logger.setLevel(logging.INFO)

class ProjectContextAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.context_data = {"modules": {}, "dependencies": {}, "summary": {}}

    def scan_directories(self):
        """Scans the project directory for Python files."""
        logger.info("📂 Scanning project directories...")
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                    self.context_data["modules"][rel_path.replace("\\", "/")] = {"dependencies": []}

    def extract_code_context(self):
        """Extracts module-level docstrings and other metadata."""
        logger.info("📜 Extracting docstrings and code context...")
        for file_path in self.context_data["modules"].keys():
            abs_path = os.path.join(self.project_root, file_path)
            with open(abs_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Extract the first docstring (if present)
            docstring = None
            if lines and lines[0].startswith('"""'):
                docstring = lines[0].strip().strip('"""')

            self.context_data["modules"][file_path]["purpose"] = docstring if docstring else "No docstring found."

    def map_dependencies(self):
        """Parses each file and extracts module dependencies."""
        import ast

        logger.info("🔗 Mapping module dependencies...")
        for file_path in self.context_data["modules"].keys():
            abs_path = os.path.join(self.project_root, file_path)
            with open(abs_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)

            dependencies = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for alias in node.names:
                        dependencies.add(f"{node.module}.{alias.name}")

            self.context_data["modules"][file_path]["dependencies"] = sorted(dependencies)

    def save_analysis(self):
        """Saves the analysis results to a JSON file."""
        output_path = os.path.join(self.project_root, "project_analysis.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.context_data, f, indent=4)
        logger.info(f"📄 Analysis saved to {output_path}")

    def analyze_project(self):
        """Runs a full project analysis."""
        logger.info("📊 Analyzing project structure...")
        self.scan_directories()
        self.extract_code_context()
        self.map_dependencies()
        self.save_analysis()
        logger.info("✅ Project analysis completed!")


# **Wrapper Function to Run Analysis Without Instantiating the Class**
def analyze_project(project_root: str = None) -> Dict[str, Any]:
    """
    Runs a full project analysis without explicitly creating an instance.
    """
    if project_root is None:
        project_root = os.path.dirname(os.path.abspath(__file__))

    analyzer = ProjectContextAnalyzer(project_root)
    analyzer.analyze_project()
    return analyzer.context_data  # Returns analysis result as a dictionary


# **Example Usage**
if __name__ == "__main__":
    project_data = analyze_project()
    print(json.dumps(project_data, indent=4))
