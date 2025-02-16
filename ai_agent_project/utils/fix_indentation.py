import os
import re

TEST_DIR = "tests"

def fix_indentation(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    original_lines = lines[:]
    fixed_lines = []

    for line in lines:
        # Fix unexpected indent errors
        fixed_line = re.sub(r'^\s{2,}', '    ', line)  # Normalize to 4 spaces

        # Ensure function definitions have proper indentation
        if re.match(r'def .+\(\):', fixed_line):
            fixed_lines.append(fixed_line)
            fixed_lines.append("    pass\n")  # Add a placeholder to avoid indentation errors
        else:
            fixed_lines.append(fixed_line)

    if fixed_lines != original_lines:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(fixed_lines)
        print(f"✅ Fixed indentation in: {file_path}")

def scan_and_fix_indentation():
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                fix_indentation(os.path.join(root, file))

if __name__ == "__main__":
    scan_and_fix_indentation()
    print("🎯 Indentation issues fixed.")
