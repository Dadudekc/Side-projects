import os
import re

TEST_DIR = "tests"

def fix_parentheses(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    original_content = content

    # Remove unmatched closing parentheses and brackets
    content = re.sub(r'\n\s*\)', '', content)
    content = re.sub(r'\n\s*\}', '', content)

    # Ensure function parentheses are closed properly
    content = re.sub(r'(\w+)\s*=\s*{\s*\n\s*', r'\1 = { }', content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"✅ Fixed parentheses in: {file_path}")

def scan_and_fix_parentheses():
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                fix_parentheses(os.path.join(root, file))

if __name__ == "__main__":
    scan_and_fix_parentheses()
    print("🎯 Parentheses issues fixed.")
