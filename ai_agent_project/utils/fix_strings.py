import os
import re

TEST_DIR = "tests"

def fix_unterminated_strings(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    original_content = content

    # Ensure all triple quotes are properly closed
    content = re.sub(r'("""[^"]*?$)', r'\1"""', content, flags=re.MULTILINE)
    content = re.sub(r"('''[^']*?$)", r"\1'''", content, flags=re.MULTILINE)

    # Fix decorators and docstrings that are improperly formatted
    content = re.sub(r'(@patch\(".*? from .*? import .*?)\n', r'\1")\n', content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"✅ Fixed strings in: {file_path}")

def scan_and_fix_strings():
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                fix_unterminated_strings(os.path.join(root, file))

if __name__ == "__main__":
    scan_and_fix_strings()
    print("🎯 String issues fixed.")
