import pytest

def pytest_report_teststatus(report, config):
    if report.when == "call" and report.outcome == "passed":
        print(f"✅ PASSED: {report.nodeid}")
