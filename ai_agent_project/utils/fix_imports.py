import os
import re

TEST_DIR = "tests"

def fix_imports(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    original_content = content

    # Fix misplaced 'from' keywords
    content = re.sub(r'from ([\w\.]+) import (.*?), from ([\w\.]+) import (.*?)', r'from \1 import \2\nfrom \3 import \4', content)
    content = re.sub(r'from (\w+)\.from (\w+)', r'from \1.\2', content)

    # Fix cases where "from" appears twice
    content = re.sub(r'from (\w+)\s+from (\w+)', r'from \1 import \2', content)

    # Fix incorrectly assigned imports
    content = re.sub(r'self\.(\w+)\s*=\s*from (\w+) import (\w+)', r'self.\1 = \3', content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"✅ Fixed imports in: {file_path}")

def scan_and_fix_imports():
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                fix_imports(os.path.join(root, file))

if __name__ == "__main__":
    scan_and_fix_imports()
    print("🎯 Import issues fixed.")
