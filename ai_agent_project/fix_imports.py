import os
import re
import subprocess
import sys

# Paths
TESTS_FOLDER = "tests"


def fix_syntax_errors(file_path):
    """Attempts to fix common syntax issues in Python test files."""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    fixed_lines = []
    for line in lines:
        # Fix unterminated string literals (only if clearly cut off)
        if re.search(r'["\']\s*$', line):  
            line = line.strip() + '"\n'

        # Fix unmatched { or }
        if "{" in line and "}" not in line:
            line = line.rstrip() + " }\n"

        # Fix trailing commas outside brackets
        if re.search(r",\s*$", line) and not re.search(r"[\[\]{}]", line):
            line = line.rstrip(",\n") + "\n"

        fixed_lines.append(line)

    # Write back the fixed file
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(fixed_lines)


def fix_import_errors():
    """Adds PYTHONPATH fixes for modules that cannot be imported."""
    sys.path.insert(0, os.path.abspath("."))  # Add the root project path
    conftest_path = os.path.join(TESTS_FOLDER, "conftest.py")
    if not os.path.exists(conftest_path):
        with open(conftest_path, "w", encoding="utf-8") as f:
            f.write(
                "import sys\n"
                "import os\n"
                "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))\n"
            )


def run_auto_format():
    """Runs auto-formatting tools on the test files."""
    print("🔹 Running auto-formatting with Black...")
    subprocess.run(["black", TESTS_FOLDER], check=False)

    print("🔹 Running auto-linting with pylint...")
    subprocess.run(["pylint", "--errors-only", TESTS_FOLDER], check=False)


def check_syntax():
    """Runs syntax checks on all test files."""
    print("🔹 Checking syntax errors...")
    failed_files = []
    for root, _, files in os.walk(TESTS_FOLDER):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    subprocess.run(["python", "-m", "py_compile", file_path], check=True)
                except subprocess.CalledProcessError:
                    print(f"⚠️ Syntax error in {file_path}")
                    failed_files.append(file_path)

    return failed_files


def main():
    """Main automation flow."""
    print("🚀 Automating test fixes...")

    # Step 1: Fix Syntax Errors
    for root, _, files in os.walk(TESTS_FOLDER):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                fix_syntax_errors(file_path)

    # Step 2: Fix Import Errors
    fix_import_errors()

    # Step 3: Auto-format and Lint
    run_auto_format()

    # Step 4: Check for Remaining Syntax Issues
    failed_files = check_syntax()

    if failed_files:
        print("⚠️ Remaining issues in:", failed_files)
    else:
        print("✅ All syntax errors fixed!")

    print("🎯 Auto-fix process complete!")


if __name__ == "__main__":
    main()
