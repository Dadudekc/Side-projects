# modules/analyzer_core.py

import os
import re
from datetime import datetime

# -----------------------------
# Regex patterns for Python parsing
# -----------------------------
IMPORT_PATTERN    = re.compile(r'^import\s+(\w+)|^from\s+(\w+)\s+import', re.MULTILINE)
CLASS_PATTERN     = re.compile(r'^class\s+(\w+)\s*\(?', re.MULTILINE)
FUNCTION_PATTERN  = re.compile(r'^def\s+(\w+)\s*\((.*?)\):', re.MULTILINE)
DOCSTRING_PATTERN = re.compile(r'"""(.*?)"""|\'\'(.*?)\'\'', re.DOTALL)
CONSTANT_PATTERN  = re.compile(r'^(\w+)?\s*=\s*(.+)', re.MULTILINE)
API_CALL_PATTERN  = re.compile(r'(https?://[\w\./?=&%-]+)')

def extract_python_details(file_path):
    """
    Extracts various components (imports, classes, functions, etc.) from a Python file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    imports    = IMPORT_PATTERN.findall(content)
    classes    = CLASS_PATTERN.findall(content)
    functions  = FUNCTION_PATTERN.findall(content)
    docstrings = DOCSTRING_PATTERN.findall(content)
    constants  = CONSTANT_PATTERN.findall(content)
    api_calls  = API_CALL_PATTERN.findall(content)

    # Use the first found docstring as a description if available.
    description = "No description available."
    if docstrings:
        description = (docstrings[0][0] or docstrings[0][1]).strip()

    details = {
        "file": os.path.basename(file_path),
        "path": os.path.abspath(file_path),
        "analyzed_at": datetime.now().isoformat(),
        "imports": list(set([imp[0] or imp[1] for imp in imports if imp[0] or imp[1]])),
        "classes": classes,
        "description": description,
        "functions": [{"name": name, "parameters": params.strip()} for name, params in functions],
        "constants": [{"name": const_name.strip(), "value": const_value.strip()} for const_name, const_value in constants if const_name],
        "api_calls": list(set(api_calls))
    }
    return details

def scan_project(directory):
    """
    Recursively scans a directory for Python files and extracts their details.
    Returns a summary dictionary of the analysis.
    """
    project_summary = {
        "project": os.path.basename(os.path.abspath(directory)),
        "analyzed_at": datetime.now().isoformat(),
        "files": []
    }
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                details = extract_python_details(file_path)
                if details:
                    project_summary["files"].append(details)
    return project_summary
