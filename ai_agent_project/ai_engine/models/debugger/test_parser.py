import logging
from typing import List, Dict

logger = logging.getLogger("TestParser")


class TestParser:
    """
    Parses test failures from pytest output.
    """

    def parse_simple_failures(self, test_output: str) -> List[Dict[str, str]]:
        """Extracts failure details from simple pytest output."""
        failures = []
        for line in test_output.splitlines():
            if "FAILED" in line:
                parts = line.split(" - ")
                if len(parts) >= 2:
                    failures.append({"file": parts[0].strip(), "error": parts[1].strip()})
        return failures
