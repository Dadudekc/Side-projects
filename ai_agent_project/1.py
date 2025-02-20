import os
import json

# Define the root directory of the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Directories to exclude from scanning
EXCLUDED_DIRS = {".git", "__pycache__", "venv", "node_modules", "logs"}

# File extensions categorized by type
FILE_TYPES = {
    "Python Scripts": {".py"},
    "Config Files": {".toml", ".json", ".yaml", ".ini"},
    "UI Files": {".ui", ".qss"},
    "Shell Scripts": {".sh", ".bat"},
    "Jupyter Notebooks": {".ipynb"},
    "Text Files": {".md", ".txt"},
    "Other": set()
}

def categorize_file(file_name):
    """Determine the category of a file based on its extension."""
    ext = os.path.splitext(file_name)[1].lower()
    for category, extensions in FILE_TYPES.items():
        if ext in extensions:
            return category
    return "Other"

def scan_directory(directory):
    """Recursively scans the project directory and categorizes files."""
    file_inventory = {category: [] for category in FILE_TYPES.keys()}

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            category = categorize_file(file)
            relative_path = os.path.relpath(os.path.join(root, file), ROOT_DIR)
            file_inventory[category].append(relative_path)

    return file_inventory

if __name__ == "__main__":
    project_files = scan_directory(ROOT_DIR)

    # Save results to a JSON file for easy reference
    output_file = os.path.join(ROOT_DIR, "project_inventory.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(project_files, f, indent=4)

    print(f"✅ Project inventory saved to: {output_file}")
