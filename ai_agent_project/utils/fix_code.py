import os
import re

TEST_DIR = "tests"

def fix_code(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    original_content = content

    # Fix unterminated strings
    content = re.sub(r'("""[^"]*?$)', r'\1"""', content, flags=re.MULTILINE)
    content = re.sub(r"('''[^']*?$)", r"\1'''", content, flags=re.MULTILINE)

    # Fix unterminated decorators
    content = re.sub(r'@patch\("(.*?)\n', r'@patch("\1")\n', content)
    content = re.sub(r'@patch\("(.*?)"\)"\)', r'@patch("\1")', content)

    # Fix function definitions with missing indents
    content = re.sub(r'(def .+\(\):)', r'\1\n    pass', content)

    # Fix missing closing parentheses
    content = re.sub(r'(\w+\()", re.DOTALL', r'\1)', content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"✅ Fixed issues in: {file_path}")

def scan_and_fix():
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                fix_code(os.path.join(root, file))

if __name__ == "__main__":
    scan_and_fix()
    print("🎯 Issues fixed. Try compiling again!")
