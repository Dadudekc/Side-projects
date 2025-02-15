import os
import re

TESTS_FOLDER = "tests"

def fix_unterminated_strings(file_path):
    """Fix unterminated string literals in a Python file."""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    fixed_lines = []
    open_string = False  # Tracks if we are inside an open string

    for line in lines:
        stripped = line.strip()

        # Check if line contains an unterminated string
        if re.search(r'["\']\s*$', stripped):  
            line = line.rstrip() + '"\n'  # Close the string

        # Fix unterminated docstrings
        if stripped.startswith('"""') and stripped.count('"""') == 1:
            if open_string:
                line = stripped + ' """\n'  # Close the docstring
                open_string = False
            else:
                line = stripped + ' """\n'  # Ensure it closes
                open_string = True

        fixed_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(fixed_lines)

def fix_all_test_files():
    """Fix all Python test files with unterminated string issues."""
    print("🚀 Fixing unterminated string errors...")
    for root, _, files in os.walk(TESTS_FOLDER):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                fix_unterminated_strings(file_path)
    print("✅ Unterminated string errors fixed.")

if __name__ == "__main__":
    fix_all_test_files()
