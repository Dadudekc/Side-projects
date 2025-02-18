import os
import subprocess
import re

def find_tests_directory(start_path="."):
    """
    Recursively searches for the 'tests' directory starting from the given path.
    Returns the absolute path if found, otherwise None.
    """
    for root, dirs, _ in os.walk(start_path):
        if "tests" in dirs:
            return os.path.join(root, "tests")  # Return full path to tests directory
    return None

def extract_passing_tests():
    """
    Runs pytest in the found 'tests/' directory and extracts passing test names.
    """
    tests_dir = find_tests_directory(os.getcwd())
    
    if not tests_dir:
        print("❌ No 'tests' directory found.")
        return []

    # Run pytest in the found tests directory
    result = subprocess.run(["pytest", tests_dir, "-q", "--tb=no"], capture_output=True, text=True)
    
    # Extract only lines with 'PASSED'
    passed_tests = [line for line in result.stdout.split("\n") if "PASSED" in line]

    # Extract test names using regex
    test_names = [re.search(r"tests/(\S+)", line).group(1) for line in passed_tests if re.search(r"tests/(\S+)", line)]

    return test_names

# Save passing tests to a file
passing_tests = extract_passing_tests()
if passing_tests:
    with open("passing_tests.txt", "w") as f:
        f.write("\n".join(passing_tests))
    print(f"✅ Passing tests saved: {len(passing_tests)}")
else:
    print("⚠️ No passing tests found.")
