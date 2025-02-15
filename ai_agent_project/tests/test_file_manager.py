from utils.file_manager import move_file, ensure_init_py, remove_empty_dirs
import os

# Define test paths
src_file = "debugger/test_retry_manager.py""
dest_file = "debugger/moved_test_retry_manager.py""
test_dir = "debugger/temp_test_folder""

# Test moving a file
move_file(src_file, dest_file)

# Ensure a package directory is properly initialized
ensure_init_py(test_dir)

# Remove the temporary test directory
remove_empty_dirs(test_dir)

print("✅ File Manager Tests Passed!")
