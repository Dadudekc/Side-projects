import os
import ast
import json
import logging
import subprocess
from datetime import datetime

# === Configuration ===
CODE_DIR = "."                  # Directory with your code (can be adjusted)
TESTS_DIR = "tests"             # Directory containing test files
OUTPUT_JSON = "mistral_finetune_data.json"   # Raw JSON dataset
OUTPUT_JSONL = "mistral_finetune.jsonl"        # JSONL dataset for fine-tuning

# Fine-tuning command configuration (adjust as needed)
# Option 1: Using Ollama CLI for local fine-tuning:
FINE_TUNE_CMD = ["ollama", "create", "mistral-tuned", "-f", OUTPUT_JSONL]
# Option 2: Alternatively, you might use a Hugging Face CLI command.
# For this example, we'll use the Ollama command.

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PrepareFineTuneData")

# --- Function and Test Extraction Utilities ---
def extract_functions_from_file(file_path):
    """Extracts function definitions from a Python file using AST."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception as e:
        logger.error("Error parsing %s: %s", file_path, e)
        return []
    
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            end_line = getattr(node, "end_lineno", node.lineno)
            # Capture the function code if possible.
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                code = "".join(lines[start_line - 1:end_line])
            except Exception as ex:
                logger.error("Error reading code for function %s: %s", node.name, ex)
                code = ""
            functions.append({
                "name": node.name,
                "file": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "params": [arg.arg for arg in node.args.args],
                "docstring": ast.get_docstring(node),
                "code": code
            })
    return functions

def extract_tests_from_file(file_path):
    """Extracts test function definitions (starting with 'test_') from a file using AST."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception as e:
        logger.error("Error parsing %s: %s", file_path, e)
        return []
    
    tests = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            start_line = node.lineno
            end_line = getattr(node, "end_lineno", node.lineno)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                code = "".join(lines[start_line - 1:end_line])
            except Exception as ex:
                logger.error("Error reading code for test %s: %s", node.name, ex)
                code = ""
            tests.append({
                "name": node.name,
                "file": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "code": code
            })
    return tests

def scan_project_for_functions(project_path=CODE_DIR):
    """Scans all Python files in the project and extracts function definitions."""
    all_functions = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                funcs = extract_functions_from_file(file_path)
                if funcs:
                    all_functions.extend(funcs)
    return all_functions

def scan_project_for_tests(project_path=TESTS_DIR):
    """Scans all Python test files in the project and extracts test function definitions."""
    all_tests = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                tests = extract_tests_from_file(file_path)
                if tests:
                    all_tests.extend(tests)
    return all_tests

def create_training_pairs():
    """
    Matches functions with test functions to create training pairs.
    Uses a simple heuristic: if a test function name contains the function name.
    """
    functions = scan_project_for_functions()
    tests = scan_project_for_tests()
    training_pairs = []
    for func in functions:
        for test in tests:
            # Simple match: if the function name appears in the test function name.
            if func["name"].lower() in test["name"].lower():
                pair = {
                    "input": f"Function:\n{func['code']}\nGenerate tests:",
                    "output": test["code"]
                }
                training_pairs.append(pair)
    logger.info("Extracted %d function-test pairs for training.", len(training_pairs))
    return training_pairs

def save_training_data(training_pairs, output_file=OUTPUT_JSON):
    """Saves the training pairs as JSON."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(training_pairs, f, indent=4)
    logger.info("Training data saved to '%s'.", output_file)

def convert_json_to_jsonl(input_json=OUTPUT_JSON, output_jsonl=OUTPUT_JSONL):
    """Converts the JSON training data to JSONL format for fine-tuning."""
    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(output_jsonl, "w", encoding="utf-8") as f:
        for pair in data:
            f.write(json.dumps(pair) + "\n")
    logger.info("Converted training data to JSONL format and saved to '%s'.", output_jsonl)

def fine_tune_model():
    """
    Initiates the fine-tuning process using the prepared JSONL file.
    This example uses Ollama's CLI command; adjust as needed for your setup.
    """
    logger.info("Starting fine-tuning process using data in '%s'...", OUTPUT_JSONL)
    try:
        result = subprocess.run(
            FINE_TUNE_CMD,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )
        logger.info("Fine-tuning initiated successfully. Output:\n%s", result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("Fine-tuning failed: %s\nStderr:\n%s", e, e.stderr)

if __name__ == "__main__":
    # Step 1: Create training pairs from functions and tests
    logger.info("Preparing fine-tuning data...")
    training_pairs = create_training_pairs()
    save_training_data(training_pairs)
    convert_json_to_jsonl()
    
    # Step 2: Initiate fine-tuning (choose your option)
    fine_tune_model()
