import os
import json
import ast
import re
import logging
from typing import Dict, List, Any

# Setup Logging
logger = logging.getLogger("ProjectContextAnalyzer")
logger.setLevel(logging.INFO)

class ProjectContextAnalyzer:
    """
    Analyzes the project structure and extracts high-level insights.
    """

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.context_data = {"modules": {}, "dependencies": {}, "summary": {}}

    def analyze_project(self):
        """
        Runs a full project analysis.
        """
        logger.info("📊 Analyzing project structure...")
        self.scan_directories()
        self.extract_code_context()
        self.map_dependencies()
        self.save_analysis()
        logger.info("✅ Project analysis completed!")

    def scan_directories(self):
        """
        Scans the project structure and categorizes files.
        """
        logger.info("🔍 Scanning project directories...")
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), self.project_root)
                    self.context_data["modules"][rel_path] = {"dependencies": [], "purpose": "Unknown"}

    def extract_code_context(self):
        """
        Reads Python files and extracts docstrings & module-level comments.
        """
        logger.info("📖 Extracting docstrings and metadata...")
        for rel_path in self.context_data["modules"]:
            abs_path = os.path.join(self.project_root, rel_path)
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
                parsed_tree = ast.parse(content)

                # Extract module-level docstring
                docstring = ast.get_docstring(parsed_tree)
                self.context_data["modules"][rel_path]["purpose"] = docstring if docstring else "No docstring provided"

            except Exception as e:
                logger.warning(f"⚠️ Failed to analyze {rel_path}: {e}")

    def map_dependencies(self):
        """
        Maps dependencies between project modules by analyzing imports.
        """
        logger.info("🔗 Mapping dependencies...")
        import_pattern = re.compile(r'^\s*(?:from|import)\s+([\w\d_.]+)', re.MULTILINE)

        for rel_path in self.context_data["modules"]:
            abs_path = os.path.join(self.project_root, rel_path)
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    content = f.read()
                imports = import_pattern.findall(content)

                self.context_data["modules"][rel_path]["dependencies"] = imports
                for imp in imports:
                    self.context_data["dependencies"].setdefault(imp, []).append(rel_path)

            except Exception as e:
                logger.warning(f"⚠️ Failed to parse dependencies in {rel_path}: {e}")

    def save_analysis(self):
        """
        Saves the project context analysis as a JSON file.
        """
        output_file = os.path.join(self.project_root, "project_analysis.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.context_data, f, indent=4)
        logger.info(f"📂 Project analysis saved to {output_file}")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    analyzer = ProjectContextAnalyzer(project_root)
    analyzer.analyze_project()
