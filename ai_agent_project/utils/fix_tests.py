import os
import re

# Directory containing test files
TEST_DIR = "d:\\side_projects\\Side-projects\\ai_agent_project\\tests"

# Regex patterns to detect issues
STRING_LIT_PATTERN = re.compile(r'""".*?"?"?$|\'\'\'.*?\'?\'?$', re.DOTALL)  # Fix unterminated string literals
FIXME_PATTERN = re.compile(r'FIXME')  # Remove placeholders
UNMATCHED_BRACKETS = re.compile(r'(\{|\})')  # Detect bracket mismatches
CLASS_DEF_PATTERN = re.compile(r'class\s+\w+\s*\(?.*?\)?:\s*$')  # Detect class definitions
FUNC_DEF_PATTERN = re.compile(r'def\s+\w+\s*\(.*?\):\s*$')  # Detect function definitions
INDENT_FIX_PATTERN = re.compile(r'^(\s*)(class|def) (\w+)')  # Detect missing indentation

def fix_file(file_path):
    """Scans and auto-fixes issues in a test file."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    bracket_stack = []
    inside_string = False
    last_class_or_func = None

    for i, line in enumerate(lines):
        original_line = line

        # Fix unterminated string literals
        if '"""' in line or "'''" in line:
            if STRING_LIT_PATTERN.search(line):
                inside_string = not inside_string
            if inside_string:
                line = line.rstrip("\n") + ' """\n'

        # Fix indentation errors (expected block after class or function)
        if CLASS_DEF_PATTERN.match(line) or FUNC_DEF_PATTERN.match(line):
            last_class_or_func = i  # Track last class/function definition

        if last_class_or_func is not None and i == last_class_or_func + 1 and not lines[i].strip():
            line = "    pass  # Auto-fixed missing block\n"

        # Fix unmatched brackets
        if "{" in line or "}" in line:
            bracket_stack.append(line.strip())

        # Remove FIXME placeholders
        line = FIXME_PATTERN.sub("", line)

        # Append fixed line
        fixed_lines.append(line)

    # If unmatched brackets remain, warn the user
    if bracket_stack.count("{") != bracket_stack.count("}"):
        print(f"⚠️ Unmatched brackets detected in {file_path}")

    # Write fixes back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    print(f"✅ Fixed {file_path}")

def main():
    """Iterates through test files and applies fixes."""
    for root, _, files in os.walk(TEST_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                fix_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
