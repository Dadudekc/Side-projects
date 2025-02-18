import importlib.util
import sys
import os

# Ensure project root is in sys.path
sys.path.append(os.path.abspath("D:/side_projects/Side-projects/ai_agent_project"))

# List of modules to check
modules = [
    "ai_engine.models.memory",  # Use full path for project modules
    "email.mime.text", 
    "email.mime.multipart",
    "PyQt5.QtWidgets",
    "PyQt5.QtCore",
    "unittest.mock",
    "pytest"
]

# Check if modules exist
missing_modules = [m for m in modules if importlib.util.find_spec(m) is None]

if missing_modules:
    print(f"Missing modules: {missing_modules}")
else:
    print("All modules are available!")
