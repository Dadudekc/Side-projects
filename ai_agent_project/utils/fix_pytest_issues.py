import os
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Dict

def find_python_files(root_dir: str) -> List[Path]:
    """Find all Python files in the project."""
    return [p for p in Path(root_dir).rglob("*.py")]

def extract_imports(file_path: Path) -> List[str]:
    """Extract import statements from a Python file."""
    imports = []
    with file_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = re.match(r"^(?:from|import) ([\w\.]+)", line)
            if match:
                imports.append(match.group(1))
    return imports

def check_imports(imports: List[str]) -> Dict[str, str]:
    """Check if imports are available in the environment."""
    missing_imports = {}
    for module in imports:
        try:
            __import__(module)
        except ModuleNotFoundError:
            missing_imports[module] = "ModuleNotFoundError"
    return missing_imports

def suggest_fixes(missing_imports: Dict[str, str]) -> None:
    """Suggest fixes for missing imports."""
    print("\n=== Missing Imports & Fix Suggestions ===")
    for module, error in missing_imports.items():
        print(f"- {module}: {error}")
        if module.startswith("agents.") or module.startswith("ai_engine."):
            print(f"  [Suggestion] Check if {module} exists in the project or if the import path is incorrect.")
        elif module in sys.stdlib_module_names:
            print(f"  [Suggestion] This is a standard module, but check your Python version.")
        else:
            print(f"  [Suggestion] Run: pip install {module}")

def main():
    root_dir = os.getcwd()  # Project root
    print(f"Scanning Python files in {root_dir}...")
    
    python_files = find_python_files(root_dir)
    all_imports = set()
    
    for file in python_files:
        all_imports.update(extract_imports(file))
    
    missing_imports = check_imports(list(all_imports))
    if missing_imports:
        suggest_fixes(missing_imports)
    else:
        print("\nNo missing imports detected!")

if __name__ == "__main__":
    main()
