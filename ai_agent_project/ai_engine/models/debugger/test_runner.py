"""

Module for running tests with two different modes. It includes a logger "TestRunner" and a class TestRunner which implements these test modes: 

1. Simple Mode - Runs pytest in simple mode and returns the output.
2. Advanced Mode - Runs pytest with JSON report enabled and extracts failures.

Classes:
    TestRunner: Provides method for running tests in simple and advance mode.

Methods:
    run_tests_simple() -> str: 
        This method will execute the pytest in simple mode with some
"""

import subprocess
import logging
import os
import json
from typing import List, Dict

logger = logging.getLogger("TestRunner")

class TestRunner:
    """
    Handles running tests in simple and advanced mode.
    """

    def run_tests_simple(self) -> str:
        """Runs pytest in simple mode and returns output."""
        try:
            result = subprocess.run(["pytest", "tests", "--maxfail=5", "--tb=short", "-q"],
                                    capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return ""

    def run_tests_advanced(self) -> List[Dict[str, str]]:
        """Runs pytest with JSON report enabled and extracts failures."""
        report_file = "report.json"
        if os.path.exists(report_file):
            os.remove(report_file)

        subprocess.run(["pytest", "tests", "--json-report", f"--json-report-file={report_file}"], capture_output=True)

        if not os.path.exists(report_file):
            logger.error("JSON report file not found.")
            return []

        with open(report_file, "r", encoding="utf-8") as f:
            report_data = json.load(f)

        return report_data.get("tests", [])
