#!/usr/bin/env python
"""
auto_fix.py

This script automates common fixes in the project to help resolve issues such as:
  - Missing modules (by creating placeholders from dependencies.json)
  - Broken import paths in test files
  - Unterminated string literals in test files
  - Syntax errors (via auto-formatting with Black)
  - Dependency installation

It then runs tests repeatedly until no obvious import or syntax errors remain.
"""

import os
import json
import re
import subprocess
import sys

# Define Paths
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEPENDENCY_FILE = os.path.join(PROJECT_DIR, "dependencies.json")
TESTS_DIR = os.path.join(PROJECT_DIR, "tests")
LOG_FILE = os.path.join(PROJECT_DIR, "fix_tests.log")
BACKUP_DIR = os.path.join(PROJECT_DIR, "rollback_backups")

# Load dependency structure
with open(DEPENDENCY_FILE, "r", encoding="utf-8") as f:
    dependency_data = json.load(f)

MODULES = dependency_data.get("modules", {})
DEPENDENCIES = dependency_data.get("dependencies", {})

def log_message(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(message + "\n")
    print(message)

def ensure_directory_exists(path):
    """Ensure the given directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)

def create_missing_files():
    """Create missing Python files and their corresponding classes based on dependencies.json."""
    log_message("\n🔍 Checking for missing files...")
    for module_path, details in MODULES.items():
        file_path = os.path.join(PROJECT_DIR, module_path.replace("\\", "/"))
        dir_path = os.path.dirname(file_path)
        class_name = os.path.basename(file_path).replace(".py", "")
        ensure_directory_exists(dir_path)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"class {class_name}:\n    pass\n")
            log_message(f"✅ Created missing file: {file_path} (class {class_name})")
    # Ensure __init__.py exists in all directories
    for module_path in MODULES:
        normalized_path = module_path.replace("\\", "/")
        dir_path = os.path.dirname(os.path.join(PROJECT_DIR, normalized_path))
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# Auto-created __init__.py\n")
            log_message(f"✅ Created missing __init__.py in {dir_path}")

def fix_imports():
    """Fix import issues dynamically by adjusting import paths."""
    log_message("\n🔧 Fixing import paths...")
    pattern = re.compile(r"from agents\.(\w+)\.(\w+) import (\w+)")
    for module_path in MODULES:
        file_path = os.path.join(PROJECT_DIR, module_path.replace("\\", "/"))
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            fixed_content = pattern.sub(r"from agents.core.\1 import \3", content)
            if fixed_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                log_message(f"🔧 Fixed imports in {file_path}")

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
        "black"  # Add black for code formatting
    ]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            log_message(f"📦 Installing missing package: {package}")
            subprocess.run([sys.executable, "-m", "pip", "install", package])

def fix_unterminated_strings_in_tests():
    """
    Fix unterminated string literals in test files.
    For each .py file in the tests directory, if a line contains an odd number of
    single or double quotes, append a closing quote.
    """
    log_message("🩹 Attempting to fix unterminated strings in test files...")
    for root, _, files in os.walk(TESTS_DIR):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    fixed_lines = []
                    for line in lines:
                        if line.count('"') % 2 != 0:
                            line = line.rstrip("\n") + '"\n'
                        elif line.count("'") % 2 != 0:
                            line = line.rstrip("\n") + "'\n"
                        fixed_lines.append(line)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(fixed_lines)
                    log_message(f"✅ Fixed unterminated strings in {file_path}")
                except Exception as e:
                    log_message(f"⚠️ Could not fix {file_path}: {e}")

def run_black_formatter():
    """Runs Black code formatter on all Python files in the tests directory."""
    log_message("\n🔧 Running Black code formatter on test files...")
    try:
        result = subprocess.run([sys.executable, "-m", "black", TESTS_DIR],
                                capture_output=True, text=True)
        log_message(result.stdout.strip())
    except Exception as e:
        log_message(f"⚠️ Failed to run Black: {e}")

def check_syntax_errors():
    """Check for syntax errors in test files and log any issues."""
    log_message("🚀 Checking for syntax errors in test files...")
    for root, _, files in os.walk(TESTS_DIR):
        for file_name in files:
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    compile(source, file_path, 'exec')
                except SyntaxError as e:
                    log_message(f"❌ Syntax Error in {file_path}: {e}")

def run_tests():
    """
    Run tests and retry until all obvious import and syntax errors are resolved.
    If errors persist without progress, exit the loop.
    """
    last_output = ""
    while True:
        log_message("\n🚀 Running tests...")
        result = subprocess.run(["pytest", "tests/", "--import-mode=importlib"],
                                capture_output=True, text=True)
        output = result.stdout
        print(output)
        if ("ModuleNotFoundError" not in output and
            "unterminated string literal" not in output and
            "SyntaxError" not in output):
            log_message("✅ Tests passed or no obvious errors remain!")
            break
        else:
            if output == last_output:
                log_message("⚠️ No progress made on repeated errors. Stopping auto-fix attempts.")
                break
            last_output = output
            if "ModuleNotFoundError" in output:
                log_message("⚠️ Import errors detected. Attempting to fix missing files & imports.")
                create_missing_files()
                fix_imports()
            if ("unterminated string literal" in output) or ("SyntaxError" in output):
                log_message("⚠️ Unterminated strings or syntax errors detected. Attempting to fix them.")
                fix_unterminated_strings_in_tests()
                run_black_formatter()  # Use Black to autoformat code
            # Optionally, re-run dependency installation in case missing packages cause issues
            install_dependencies()

if __name__ == "__main__":
    # Clear previous log file
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    log_message("🚀 Starting auto-fix process...")
    create_missing_files()
    fix_imports()
    install_dependencies()
    run_tests()
