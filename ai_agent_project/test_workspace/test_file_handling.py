import os
import time
from ai_refactor_agent import get_python_files, backup_file, restore_backup

def test_file_handling():
    test_file = "dummy_test.py"

    # Cleanup before test
    if os.path.exists(test_file):
        os.remove(test_file)

    # Create test file in the root directory
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("print('Test file')")

    time.sleep(1)  # Allow system time to register file
    
    # Get detected files
    python_files = get_python_files()
    print(f"\n🔍 Detected Python files: {python_files}")  # Debugging output
    
    # Assert based on full paths
    assert any(os.path.basename(f) == test_file for f in python_files), (
        f"❌ Test file '{test_file}' not detected. Files found: {python_files}"
    )
    
    print("✅ Test file detection passed!")

if __name__ == "__main__":
    test_file_handling()
