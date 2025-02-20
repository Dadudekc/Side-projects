import os
import subprocess
import json
import logging
import ast
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# === Configuration ===
COVERAGE_REPORT_DIR = "htmlcov"                  # Directory for coverage HTML report
GENERATED_TESTS_FILE = "tests/generated_tests.py"  # File to store AI-generated tests
FUNCTION_MAP_FILE = "function_map.json"          # File containing function definitions
MAX_RETRIES = 3                                  # Maximum AI reattempts for test generation
# Optionally, if you have fine-tuned your model, update this model name:
FINE_TUNED_MODEL = "mistral-tuned"  # Use your fine-tuned model name; otherwise, use "mistral:latest"

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AITestAgent")

# --- Function Extraction Utilities ---
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
            end_line = node.end_lineno if hasattr(node, "end_lineno") else start_line
            functions.append({
                "name": node.name,
                "file": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "params": [arg.arg for arg in node.args.args],
                "docstring": ast.get_docstring(node)
            })
    return functions

def scan_project_for_functions(project_path="."):
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

def create_function_map():
    """Generates the function map and saves it to FUNCTION_MAP_FILE."""
    functions_data = scan_project_for_functions()
    with open(FUNCTION_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(functions_data, f, indent=4)
    logger.info("✅ Extracted %d functions. Saved to '%s'.", len(functions_data), FUNCTION_MAP_FILE)

# --- AITestAgent (TestSis) ---
class AITestAgent:
    """
    Hi there! I'm TestSis—the AI Test Agent and your friendly sister to AIRefactorAgent.
    
    My mission is to:
      - Run test coverage checks using pytest-cov.
      - Load (or dynamically create) a function map for your project.
      - Use AI to generate comprehensive pytest tests for each function.
      - Run those generated tests and, if any fail, generate debugging suggestions.
      - Auto-optimize my prompts and reattempt test generation if needed.
      - Cheer you on and keep your code safe while you sleep!
    """
    def __init__(self):
        if not os.path.exists(FUNCTION_MAP_FILE):
            logger.info("TestSis: Function map not found. Extracting functions now...")
            create_function_map()

    def run_coverage(self):
        """Runs pytest with coverage to generate an HTML report."""
        logger.info("TestSis: Running coverage analysis...")
        result = subprocess.run(
            ["pytest", "--cov=.", "--cov-report=html"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            logger.info("TestSis: Coverage report generated in '%s'.", COVERAGE_REPORT_DIR)
        else:
            logger.error("TestSis: Coverage analysis issues:\n%s", result.stderr)
        return result.stdout

    def load_function_map(self):
        """Loads the function map from FUNCTION_MAP_FILE."""
        if os.path.exists(FUNCTION_MAP_FILE):
            with open(FUNCTION_MAP_FILE, "r", encoding="utf-8") as f:
                functions = json.load(f)
            logger.info("TestSis: Loaded %d functions from '%s'.", len(functions), FUNCTION_MAP_FILE)
            return functions
        else:
            logger.info("TestSis: Function map not found. Creating new one...")
            create_function_map()
            return self.load_function_map()

    def generate_tests_for_function(self, function_data, retry_count=0):
        """
        Uses AI (via Ollama) to generate pytest unit tests for a given function.
        Automatically refines the prompt on failure.
        """
        prompt = f"""
You are a brilliant Python testing assistant. Please generate comprehensive pytest unit tests for the following function.
- Cover normal, edge, and error cases.
- If the function uses external dependencies, mock them.
- Ensure test assertions match expected behavior.

Function:
{function_data.get('code', 'def placeholder(): pass')}

Return only the test code.
"""
        if retry_count > 0:
            logger.warning("TestSis: Retrying AI test generation (Attempt %d)...", retry_count + 1)
            prompt += "\nPrevious test generation had issues. Please improve test robustness."
        logger.info("TestSis: Generating tests for function '%s' in %s...", 
                    function_data.get("name", "<unknown>"), function_data.get("file", "<unknown>"))
        try:
            # Use the fine-tuned model if available; otherwise, default to mistral:latest
            model = FINE_TUNED_MODEL if FINE_TUNED_MODEL else "mistral:latest"
            result = subprocess.run(
                ["ollama", "run", model],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )
            test_code = result.stdout.strip()
            if not test_code:
                raise ValueError("Empty AI response")
            logger.info("TestSis: Tests generated for '%s'.", function_data["name"])
            return test_code
        except Exception as e:
            if retry_count < MAX_RETRIES:
                return self.generate_tests_for_function(function_data, retry_count + 1)
            logger.error("TestSis: AI test generation failed for '%s': %s", function_data.get("name"), e)
            return None

    def save_generated_tests(self, test_code):
        """Appends the generated tests to the designated tests file."""
        try:
            with open(GENERATED_TESTS_FILE, "a", encoding="utf-8") as f:
                f.write("\n" + test_code + "\n")
            logger.info("TestSis: Generated tests saved to '%s'.", GENERATED_TESTS_FILE)
        except Exception as e:
            logger.error("TestSis: Failed to save generated tests: %s", e)

    def run_generated_tests(self):
        """Runs the generated tests using pytest and returns the output."""
        logger.info("TestSis: Running generated tests...")
        result = subprocess.run(
            ["pytest", GENERATED_TESTS_FILE],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return result.stdout

    def debug_failed_tests(self, error_logs):
        """
        Uses AI to generate debugging suggestions based on test error logs.
        """
        prompt = f"""
You are a top-notch debugging assistant. Based on the following test error logs, please suggest detailed fixes for the underlying issues:
{error_logs}

Return only your suggested fixes.
"""
        logger.info("TestSis: Generating debug suggestions...")
        try:
            result = subprocess.run(
                ["ollama", "run", "mistral:latest"],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )
            suggestions = result.stdout.strip()
            logger.info("TestSis: Debug suggestions generated.")
            return suggestions
        except Exception as e:
            logger.error("TestSis: Failed to generate debug suggestions: %s", e)
            return "No suggestions available."

    def test_and_debug_mode(self):
        """
        Runs the complete test and debug process:
          1. Runs coverage analysis.
          2. Loads (or creates) the function map and extracts each function's code.
          3. For each function, uses AI to generate tests.
          4. Saves the generated tests.
          5. Runs the generated tests.
          6. If tests fail, recursively reattempts test generation (self-healing) and generates debug suggestions.
        """
        logger.info("TestSis: Starting test and debug mode! Let's ensure everything's perfect for you!")
        self.run_coverage()
        functions = self.load_function_map()
        if not functions:
            logger.error("TestSis: No functions found. Please generate your function map first.")
            return

        # Clear any previous generated tests
        if os.path.exists(GENERATED_TESTS_FILE):
            os.remove(GENERATED_TESTS_FILE)

        for func in functions:
            if "code" not in func:
                try:
                    with open(func["file"], "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    func["code"] = "".join(lines[func["start_line"] - 1 : func["end_line"]])
                except Exception as e:
                    logger.error("TestSis: Failed to read code for %s: %s", func["name"], e)
                    continue

            generated_tests = self.generate_tests_for_function(func)
            if generated_tests:
                self.save_generated_tests(generated_tests)
            else:
                logger.warning("TestSis: No tests generated for function %s.", func["name"])

        test_output = self.run_generated_tests()
        logger.info("TestSis: Generated test output:\n%s", test_output)

        if "FAILED" in test_output:
            logger.warning("TestSis: Some tests failed. Auto-regenerating improved tests...")
            self.test_and_debug_mode()  # Recursive self-healing
        else:
            logger.info("TestSis: All generated tests passed! Great job, sis!")

# === Main Execution ===
if __name__ == "__main__":
    agent = AITestAgent()
    agent.test_and_debug_mode()
