#!/usr/bin/env python3
import os
import re
import json
import yaml
import argparse
import logging
from datetime import datetime

# -----------------------------
# Regex patterns for PHP parsing
# -----------------------------
NAMESPACE_PATTERN = re.compile(r'namespace\s+([\w\\]+)')
CLASS_PATTERN     = re.compile(r'\bclass\s+(\w+)', re.IGNORECASE)
INTERFACE_PATTERN = re.compile(r'\binterface\s+(\w+)', re.IGNORECASE)
TRAIT_PATTERN     = re.compile(r'\btrait\s+(\w+)', re.IGNORECASE)
FUNCTION_PATTERN  = re.compile(r'\bfunction\s+(\w+)\s*\((.*?)\)', re.IGNORECASE)
# Match PHPDoc block comments (non-greedy)
COMMENT_PATTERN   = re.compile(r'/\*\*(.*?)\*/', re.DOTALL)
CONSTANT_PATTERN  = re.compile(r'define\(\s*[\'"](\w+)[\'"]\s*,\s*[\'"](.*?)[\'"]\s*\)', re.IGNORECASE)
API_CALL_PATTERN  = re.compile(r'(https?://[\w\./?=&%-]+)')
# Allow for includes with or without parentheses
INCLUDE_PATTERN   = re.compile(r'\b(include|require)(_once)?\s*\(?\s*[\'"]([^\'"]+)[\'"]\s*\)?', re.IGNORECASE)
# Detect class properties with visibility keywords.
PROPERTY_PATTERN  = re.compile(r'\b(public|protected|private)\s+\$([\w_]+)', re.IGNORECASE)

# -----------------------------
# Extraction function for one PHP file
# -----------------------------
def extract_php_details(file_path):
    """
    Extract details from a PHP file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return None

    # Extract details using regex searches
    namespace   = NAMESPACE_PATTERN.search(content)
    class_match = CLASS_PATTERN.search(content)
    interfaces  = INTERFACE_PATTERN.findall(content)
    traits      = TRAIT_PATTERN.findall(content)
    functions   = FUNCTION_PATTERN.findall(content)
    comments    = COMMENT_PATTERN.findall(content)
    constants   = CONSTANT_PATTERN.findall(content)
    api_calls   = API_CALL_PATTERN.findall(content)
    includes    = INCLUDE_PATTERN.findall(content)
    properties  = PROPERTY_PATTERN.findall(content)

    # Use the first PHPDoc comment as a description if available
    description = "No description available."
    if comments:
        clean_lines = [line.strip(" *") for line in comments[0].strip().splitlines() if line.strip(" *")]
        description = " ".join(clean_lines)

    details = {
        "file": os.path.basename(file_path),
        "path": os.path.abspath(file_path),
        "analyzed_at": datetime.now().isoformat(),
        "namespace": namespace.group(1) if namespace else None,
        "class": class_match.group(1) if class_match else None,
        "interfaces": interfaces if interfaces else [],
        "traits": traits if traits else [],
        "description": description,
        "functions": [{"name": name, "parameters": params.strip()} for name, params in functions],
        "constants": [{"name": const_name, "value": const_value} for const_name, const_value in constants],
        "api_calls": list(set(api_calls)),  # unique API calls
        "includes": list(set([inc[2] for inc in includes])),
        "properties": [{"visibility": vis, "name": prop_name} for vis, prop_name in properties]
    }

    # Log the raw details for debugging purposes.
    logging.debug(f"Extracted details for {file_path}: {json.dumps(details, indent=2, ensure_ascii=False)}")
    return details

# -----------------------------
# Scan a directory recursively for PHP files
# -----------------------------
def scan_project(directory):
    """
    Walk through the directory recursively and analyze all PHP files.
    """
    project_summary = {
        "project": os.path.basename(os.path.abspath(directory)),
        "analyzed_at": datetime.now().isoformat(),
        "files": []
    }

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.php'):
                file_path = os.path.join(root, file)
                logging.info(f"Analyzing: {file_path}")
                details = extract_php_details(file_path)
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

    # Debug: Dump summary to console
    logging.debug("Final project summary:")
    logging.debug(json.dumps(summary, indent=2, ensure_ascii=False))

    # Save JSON
    json_path = os.path.join(output_dir, 'project_summary.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(summary, json_file, indent=4, ensure_ascii=False)
        logging.info(f"JSON summary saved to {json_path}")
    except Exception as e:
        logging.error(f"Error saving JSON: {e}")

    # Save YAML
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
    parser = argparse.ArgumentParser(
        description="Advanced PHP Project Analyzer with Debug: Scans PHP files to extract classes, functions, includes, and more."
    )
    parser.add_argument("directory", help="Path to the PHP project directory")
    parser.add_argument("-o", "--output", default="summaries", help="Output directory for summaries (default: summaries)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # Set logging level based on debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled.")

    if not os.path.isdir(args.directory):
        logging.error(f"The provided path '{args.directory}' is not a directory.")
        exit(1)

    logging.info(f"Starting analysis of project: {args.directory}")
    summary = scan_project(args.directory)

    # If no PHP files were found, warn the user.
    if not summary["files"]:
        logging.warning("No PHP files were analyzed. The output may be empty.")

    save_summary(summary, args.output)
    logging.info("Project analysis complete.")

if __name__ == "__main__":
    main()
