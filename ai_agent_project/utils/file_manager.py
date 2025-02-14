import os
import shutil
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory: str):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"📁 Created directory: {directory}")

def move_file(source: str, destination: str):
    """Move a file from source to destination."""
    if os.path.exists(source):
        ensure_directory_exists(os.path.dirname(destination))
        shutil.move(source, destination)
        logger.info(f"📂 Moved: {source} → {destination}")
    else:
        logger.warning(f"⚠ File not found: {source}")

def ensure_init_py(directory: str):
    """Ensure __init__.py exists in a directory to mark it as a Python package."""
    init_file = os.path.join(directory, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Auto-generated __init__.py\n")
        logger.info(f"📝 Created {init_file}")

def remove_empty_dirs(directory: str):
    """Recursively remove empty directories within a given directory."""
    for root, dirs, _ in os.walk(directory, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                logger.info(f"🗑 Removed empty directory: {dir_path}")

if __name__ == "__main__":
    # Example usage
    move_file("old_location/sample.py", "new_location/sample.py")
    ensure_init_py("new_location")
    remove_empty_dirs("old_location")
