import os
import re
import json
import yaml
import argparse
import logging
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

# -----------------------------
# Extraction function for one Python file
# -----------------------------
def extract_python_details(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return None

    imports    = IMPORT_PATTERN.findall(content)
    classes    = CLASS_PATTERN.findall(content)
    functions  = FUNCTION_PATTERN.findall(content)
    docstrings = DOCSTRING_PATTERN.findall(content)
    constants  = CONSTANT_PATTERN.findall(content)
    api_calls  = API_CALL_PATTERN.findall(content)

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

    logging.debug(f"Extracted details for {file_path}: {json.dumps(details, indent=2, ensure_ascii=False)}")
    return details

# -----------------------------
# Scan a directory recursively for Python files
# -----------------------------
def scan_project(directory):
    project_summary = {
        "project": os.path.basename(os.path.abspath(directory)),
        "analyzed_at": datetime.now().isoformat(),
        "files": []
    }

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                logging.info(f"Analyzing: {file_path}")
                details = extract_python_details(file_path)
                if details:
                    project_summary["files"].append(details)
                else:
                    logging.warning(f"No details extracted from {file_path}")
    return project_summary

# -----------------------------
# Save summary as JSON and YAML
# -----------------------------
def save_summary(summary, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, 'project_summary.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(summary, json_file, indent=4, ensure_ascii=False)
        logging.info(f"JSON summary saved to {json_path}")
    except Exception as e:
        logging.error(f"Error saving JSON: {e}")

    yaml_path = os.path.join(output_dir, 'project_summary.yaml')
    try:
        with open(yaml_path, 'w', encoding='utf-8') as yaml_file:
            yaml.dump(summary, yaml_file, default_flow_style=False, allow_unicode=True, sort_keys=False)
        logging.info(f"YAML summary saved to {yaml_path}")
    except Exception as e:
        logging.error(f"Error saving YAML: {e}")

# -----------------------------
# Main function with argparse
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="Python Project Analyzer: Scans Python files to extract classes, functions, imports, and more.")
    parser.add_argument("directory", help="Path to the Python project directory")
    parser.add_argument("-o", "--output", default="summaries", help="Output directory for summaries (default: summaries)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled.")

    if not os.path.isdir(args.directory):
        logging.error(f"The provided path '{args.directory}' is not a directory.")
        exit(1)

    logging.info(f"Starting analysis of project: {args.directory}")
    summary = scan_project(args.directory)

    if not summary["files"]:
        logging.warning("No Python files were analyzed. The output may be empty.")

    save_summary(summary, args.output)
    logging.info("Project analysis complete.")

if __name__ == "__main__":
    main()
