import os
import json
import re
import subprocess
import sys

# Define Paths
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEPENDENCY_FILE = os.path.join(PROJECT_DIR, "dependencies.json")
TESTS_DIR = os.path.join(PROJECT_DIR, "tests")

# Load dependency structure
with open(DEPENDENCY_FILE, "r", encoding="utf-8") as f:
    dependency_data = json.load(f)

MODULES = dependency_data.get("modules", {})
DEPENDENCIES = dependency_data.get("dependencies", {})

def ensure_directory_exists(path):
    """Ensure the given directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)

def create_missing_files():
    """Create missing Python files and their corresponding classes based on dependencies.json."""
    print("\n🔍 Checking for missing files...")

    for module_path, details in MODULES.items():
        file_path = os.path.join(PROJECT_DIR, module_path.replace("\\", "/"))
        dir_path = os.path.dirname(file_path)
        class_name = os.path.basename(file_path).replace(".py", "")

        ensure_directory_exists(dir_path)

        # Check if the file is missing
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"class {class_name}:\n    pass\n")
            print(f"✅ Created missing file: {file_path} (class {class_name})")

    # Ensure __init__.py exists in all directories
    for module_path in MODULES:
        # Convert backslashes to slashes for consistency
        normalized_path = module_path.replace("\\", "/")
        dir_path = os.path.dirname(os.path.join(PROJECT_DIR, normalized_path))
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# Auto-created __init__.py\n")
            print(f"✅ Created missing __init__.py in {dir_path}")

def fix_imports():
    """Fix import issues dynamically by adjusting import paths."""
    print("\n🔧 Fixing import paths...")
    pattern = re.compile(r"from agents\.(\w+)\.(\w+) import (\w+)")

    for module_path in MODULES:
        file_path = os.path.join(PROJECT_DIR, module_path.replace("\\", "/"))

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Update incorrect import paths
            fixed_content = pattern.sub(r"from agents.core.\1 import \3", content)

            if fixed_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                print(f"🔧 Fixed imports in {file_path}")

def install_dependencies():
    """Ensure required dependencies are installed."""
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "PyQt5",
        "alpaca-trade-api",
        "tqdm",
        "openai",
        "unidiff",
        "pandas",
        "matplotlib",
    ]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            print(f"📦 Installing missing package: {package}")
            subprocess.run([sys.executable, "-m", "pip", "install", package])

def fix_unterminated_strings_in_tests():
    """
    Attempts to fix unterminated string literals in test files by scanning for lines
    with an odd number of quotes. This is a heuristic and may not fix all cases,
    but often resolves 'unterminated string literal' errors.
    """
    print("\n🩹 Attempting to fix unterminated strings in test files...")
    for root, _, files in os.walk(TESTS_DIR):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    fixed_lines = []
                    for line in lines:
                        # Count quotes
                        double_quotes = line.count('"')
                        single_quotes = line.count("'")
                        # Quick fix approach: if we have an odd number of either type, add one more
                        if double_quotes % 2 != 0:
                            line = line.rstrip("\n") + '"\n'
                        elif single_quotes % 2 != 0:
                            line = line.rstrip("\n") + "'\n"
                        fixed_lines.append(line)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(fixed_lines)

                except Exception as e:
                    print(f"⚠️ Could not fix {file_path}: {e}")

def run_tests():
    """
    Run tests and retry until all import errors and unterminated string
    issues are resolved (or no progress can be made).
    """
    # Keep track of the last output to detect if we're stuck
    last_output = ""
    while True:
        print("\n🚀 Running tests...")
        result = subprocess.run(["pytest", "tests/", "--import-mode=importlib"], capture_output=True, text=True)
        output = result.stdout
        print(output)

        # Check for "ModuleNotFoundError" or "unterminated string" or "SyntaxError"
        if ("ModuleNotFoundError" not in output
                and "unterminated string literal" not in output
                and "SyntaxError" not in output):
            print("✅ Tests either passed or no obvious errors remain!")
            break
        else:
            # If the output hasn't changed since last attempt, we might be stuck
            if output == last_output:
                print("⚠️ No progress made on repeated errors. Stopping auto-fix attempts.")
                break
            last_output = output

            if "ModuleNotFoundError" in output:
                print("⚠️ Import errors detected. Attempting to fix missing files & imports.")
                create_missing_files()
                fix_imports()
            if ("unterminated string literal" in output) or ("SyntaxError" in output):
                print("⚠️ Unterminated strings or syntax errors detected. Attempting to fix them.")
                fix_unterminated_strings_in_tests()

if __name__ == "__main__":
    create_missing_files()
    fix_imports()
    install_dependencies()
    run_tests()
