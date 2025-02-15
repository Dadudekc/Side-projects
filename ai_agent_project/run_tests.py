import os
import sys
import subprocess
import glob

# Required directories
REQUIRED_DIRS = [
    "agents",
    "agents/core",
    "agents/core/utilities",
    "agents/utilities",
    "ai_engine",
    "ai_engine/models",
    "debugger",
    "debugger/temp_test_folder",
    "tests"
]

# Required files to exist inside "agents/core/"
REQUIRED_FILES = [
    "agents/core/AgentBase.py",
    "agents/core/CustomAgent.py",
    "agents/core/TradingAgent.py",
    "agents/core/DebuggerAgent.py",
    "agents/core/JournalAgent.py"
]


def ensure_init_files():
    """Ensure all required directories exist and create `__init__.py`."""
    for directory in REQUIRED_DIRS:
        full_path = os.path.join(os.getcwd(), directory)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"📂 Created missing directory: {full_path}")

        init_file = os.path.join(full_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Init file to make the directory a package\n")
            print(f"✅ Created {init_file}")


def ensure_files_exist():
    """Ensure critical module files exist inside `agents/core/`."""
    missing_files = []
    for file in REQUIRED_FILES:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"🚨 Missing critical files: {missing_files}")
        print("⚠️ Ensure these files are created or moved into `agents/core/`.")
        sys.exit(1)  # Stop execution if files are missing


def fix_imports():
    """Fix incorrect imports dynamically in Python files."""
    all_python_files = glob.glob("**/*.py", recursive=True)

    for file in all_python_files:
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        modified = False
        new_lines = []
        for line in lines:
            if "agents.core.AgentBase" in line:
                new_line = line.replace("agents.core.AgentBase", "agents.core.AgentBase")
                new_lines.append(new_line)
                modified = True
            else:
                new_lines.append(line)

        if modified:
            with open(file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"🔧 Fixed import issues in {file}")


def set_pythonpath():
    """Ensure the project root is in PYTHONPATH."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.environ["PYTHONPATH"] = project_root
    sys.path.insert(0, project_root)  # Force absolute imports
    print(f"✅ PYTHONPATH set to: {project_root}")


def run_tests():
    """Run tests with pytest."""
    try:
        print("\n🚀 Running tests...\n")
        subprocess.run(["pytest", "tests/", "--import-mode=importlib"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    set_pythonpath()
    ensure_init_files()
    ensure_files_exist()
    fix_imports()
    run_tests()
