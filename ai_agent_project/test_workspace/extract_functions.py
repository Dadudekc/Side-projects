import ast
import os
import json

def extract_functions_from_file(file_path):
    """Extracts function definitions from a Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line

            functions.append({
                "name": node.name,
                "file": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "params": [arg.arg for arg in node.args.args],
                "docstring": ast.get_docstring(node),
            })

    return functions

def scan_project_for_functions(project_path="."):
    """Scans all Python files in the project and extracts function definitions."""
    all_functions = []
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                functions = extract_functions_from_file(file_path)
                if functions:
                    all_functions.extend(functions)

    return all_functions

# Extract and save function map for AI processing
functions_data = scan_project_for_functions()
with open("function_map.json", "w", encoding="utf-8") as f:
    json.dump(functions_data, f, indent=4)

print(f"✅ Extracted {len(functions_data)} functions. Saved to 'function_map.json'.")
