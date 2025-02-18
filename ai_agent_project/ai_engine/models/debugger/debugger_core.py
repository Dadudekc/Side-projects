import logging
from ai_engine.models.debugger.test_runner import TestRunner
from ai_engine.models.debugger.error_parser import ErrorParser
from ai_engine.models.debugger.auto_fix_manager import AutoFixManager
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager
from ai_engine.models.debugger.rollback_manager import RollbackManager
from ai_engine.models.debugger.debug_agent_auto_fixer import DebugAgentAutoFixer

logger = logging.getLogger("DebugAgent")

class DebugAgent:
    """
    🚀 AI-driven debugging agent that detects, fixes, and verifies code issues automatically.
    """

    def __init__(self):
        self.test_runner = TestRunner()
        self.error_parser = ErrorParser()
        self.auto_fixer = AutoFixManager()
        self.patch_tracker = PatchTrackingManager()
        self.rollback_manager = RollbackManager()
        self.pre_debug_fixer = DebugAgentAutoFixer()  # Runs fixes before debugging

    def debug(self):
        """Runs the debugging workflow: Detect errors → Fix issues → Re-run tests."""
        logger.info("🚀 Running DebugAgent...")

        # Run all pre-debugging fixes before checking for errors
        self.pre_debug_fixer.auto_fix_before_debugging()

        # Run initial tests
        test_output = self.test_runner.run_tests_simple()
        failures = self.error_parser.parse_test_failures(test_output)

        if not failures:
            logger.info("✅ No issues found! Exiting DebugAgent.")
            return

        logger.info(f"⚠️ {len(failures)} test failures detected. Attempting fixes...")

        # Apply automatic fixes
        for failure in failures:
            success = self.auto_fixer.apply_fix(failure)
            if success:
                logger.info(f"✅ Fix applied for {failure['file']}")
            else:
                logger.warning(f"❌ Failed to fix {failure['file']} - Adding to rollback queue.")
                self.rollback_manager.backup_file(failure["file"])

        # Re-run tests to verify fixes
        self.verify_fixes()

    def verify_fixes(self):
        """Re-runs tests to validate fixes."""
        logger.info("🔄 Re-running tests after applying fixes...")
        test_output = self.test_runner.run_tests_simple()
        failures = self.error_parser.parse_test_failures(test_output)

        if not failures:
            logger.info("✅ All issues resolved!")
            return

        logger.warning(f"⚠️ {len(failures)} tests still failing. Applying rollbacks...")

        # Rollback failed fixes
        for failure in failures:
            self.rollback_manager.restore_backup(failure["file"])

if __name__ == "__main__":
    agent = DebugAgent()
    agent.debug()
