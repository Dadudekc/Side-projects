import os
import ast
import importlib.util

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def find_python_files(directory):
    """Recursively find all Python files in the given directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def extract_imports(file_path):
    """Extract all import statements from a given Python file."""
    imports = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module
                    for alias in node.names:
                        if module:
                            imports.add(f"{module}.{alias.name}")
                        else:
                            imports.add(alias.name)
    except Exception as e:
        print(f"⚠ Error parsing {file_path}: {e}")
    return imports


def check_imports(imports):
    """Check if the extracted imports exist and can be imported."""
    missing_imports = set()
    for module in imports:
        if not importlib.util.find_spec(module.split(".")[0]):
            missing_imports.add(module)
    return missing_imports


def main():
    print("🔍 Scanning project for import issues...\n")
    python_files = find_python_files(PROJECT_ROOT)

    all_imports = set()
    for file in python_files:
        file_imports = extract_imports(file)
        all_imports.update(file_imports)

    missing_imports = check_imports(all_imports)

    if missing_imports:
        print("\n❌ Missing or incorrect imports detected:")
        for imp in sorted(missing_imports):
            print(f"   - {imp}")

        print("\n🔧 Suggested Fix:")
        print("   1. Check if the module is installed (`pip install missing_module`).")
        print("   2. Verify if the import path is correct.")
        print("   3. Ensure the module exists in the project.")
    else:
        print("\n✅ All imports are correct!")

    print("\n🔄 Run `python check_imports.py` before committing to catch import issues early!\n")


if __name__ == "__main__":
    main()
