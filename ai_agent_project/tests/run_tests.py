"""

Executes pytest testing framework using subprocess library. The short traceback is collected for failed test cases. 

This function captures the output, scans each line for failures and appends the failures to a list. This list of failures is then returned.

Returns:
    list: A list of failed test cases.

"""

import subprocess


def run_tests():
    """
    Runs pytest and collects failed test cases.
    """
    result = subprocess.run(["pytest", "--tb=short"], capture_output=True, text=True)
    failures = []
    for line in result.stdout.split("\n"):
        if "FAILED" in line and "::" in line:
            failures.append(line)
    return failures
