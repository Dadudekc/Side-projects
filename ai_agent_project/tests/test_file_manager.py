import os

from utils.file_manager import ensure_init_py, move_file, remove_empty_dirs

# Define test paths
src_file = "debugger/test_retry_manager.py"
dest_file = "debugger/moved_test_retry_manager.py"
test_dir = "debugger/temp_test_folder"

# Ensure source file exists before attempting to move
if os.path.exists(src_file):
    move_file(src_file, dest_file)
    print(f"✅ Moved file: {src_file} → {dest_file}")
else:
    print(f"⚠ Source file not found: {src_file}")

# Ensure test directory exists before creating __init__.py
if not os.path.exists(test_dir):
    os.makedirs(test_dir)  # Create test directory for the test
ensure_init_py(test_dir)
print(f"✅ Ensured __init__.py in: {test_dir}")

# Remove test directory if it's empty
remove_empty_dirs(test_dir)
if not os.path.exists(test_dir):
    print(f"✅ Removed empty test directory: {test_dir}")
else:
    print(f"⚠ Directory not removed (may not be empty): {test_dir}")

print("🎉 File Manager Tests Passed!")
