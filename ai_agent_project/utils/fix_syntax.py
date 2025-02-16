import os
import re
import ast
import sys
from pathlib import Path

# Define test directory
TEST_DIR = Path("tests")

# Define common issues and fixes
ISSUE_FIXES = {
    r'(@patch\(.*)\)"\)': r'\1)',  # Fix unterminated decorators
    r'(""".*?""")"': r'\1',  # Fix unterminated string literals
    r'(from .* import) pass': r'\1',  # Fix malformed imports
    r'(@patch\(.*\))"': r'\1',  # Fix incorrectly terminated @patch
    r'(\bVectorMemoryManager, :)': r'\1',  # Fix malformed list separator
}

def auto_fix_syntax(file_path):
    """Automatically fix common syntax errors in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixed_content = content
    for pattern, replacement in ISSUE_FIXES.items():
        fixed_content = re.sub(pattern, replacement, fixed_content)
    
    if fixed_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ Fixed syntax issues in {file_path}")

def validate_python_file(file_path):
    """Check if the Python file has valid syntax after fixes."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_contents = f.read()
        ast.parse(file_contents)
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error still present in {file_path}: {e}")
        return False

def scan_and_fix_tests():
    """Scan the tests directory, identify syntax errors, and apply fixes."""
    if not TEST_DIR.exists():
        print("⚠ Test directory not found.")
        return

    for file in TEST_DIR.rglob("*.py"):
        print(f"🔍 Checking {file}...")
        auto_fix_syntax(file)
        if validate_python_file(file):
            print(f"✅ {file} is now valid.")
        else:
            print(f"⚠ {file} still has issues.")

if __name__ == "__main__":
    scan_and_fix_tests()
