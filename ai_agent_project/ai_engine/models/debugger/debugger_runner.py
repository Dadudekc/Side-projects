import logging
import subprocess
import os
from ai_engine.models.debugger.error_parser import ErrorParser
from ai_engine.models.debugger.auto_fixer import AutoFixer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DebuggerRunner:
    """
    Coordinates running tests, parsing failures, applying fixes, and retrying until success.
    """

    def __init__(self):
        self.parser = ErrorParser()
        self.fixer = AutoFixer()

    def run_tests(self) -> str:
        """
        Runs all tests using pytest and returns the combined output.
        """
        logger.info("🚀 Running pytest to execute tests...")
        try:
            result = subprocess.run(
                ["pytest", "tests", "--maxfail=5", "--tb=short", "-q"],
                capture_output=True, text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return f"Error: {e}"

    def retry_tests(self, max_retries: int = 3) -> bool:
        """
        Retries tests up to max_retries, applying fixes as needed.
        """
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Attempt {attempt} of {max_retries}")
            output = self.run_tests()
            failures = self.parser.parse_test_failures(output)
            if not failures:
                logger.info("✅ All tests passed!")
                return True
            logger.info(f"📉 {len(failures)} tests failed. Attempting to fix...")
            any_fixed = False
            for failure in failures:
                if self.fixer.apply_fix(failure):
                    any_fixed = True
                    logger.info(f"✅ Fix applied for {failure['file']}")
                else:
                    logger.error(f"❌ Could not fix {failure['file']}")
            if not any_fixed:
                logger.error("No fixes were applied in this round.")
                return False
        logger.error("Max retries reached; tests still failing.")
        return False

if __name__ == "__main__":
    runner = DebuggerRunner()
    success = runner.retry_tests()
    if success:
        logger.info("All tests passed after automated debugging!")
    else:
        logger.error("Automated debugging failed to resolve all issues.")
