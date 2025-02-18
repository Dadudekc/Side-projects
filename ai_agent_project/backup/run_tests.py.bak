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
