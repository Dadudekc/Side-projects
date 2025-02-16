import os
import logging
import json
import sys
import subprocess

# Importing core components from the existing debugging system
from ai_engine.models.debugger.debugger_core import DebuggerCore
from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy
from ai_engine.models.debugger.rollback_manager import RollbackManager
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager
from ai_engine.models.debugger.debugger_logger import DebuggerLogger
from ai_engine.models.debugger.debugger_reporter import DebuggerReporter
from ai_engine.models.debugger.project_context_analyzer import ProjectContextAnalyzer
from ai_engine.models.debugger.auto_fixer import AutoFixer
from ai_engine.models.debugger.error_parser import ErrorParser
from tests.run_tests import run_tests


class DebugAgent:
    def __init__(self, max_retries=3, enable_ai_fixes=True):
        """
        Initializes DebugAgent with key components.
        """
        self.logger = DebuggerLogger()
        self.context_analyzer = ProjectContextAnalyzer()
        self.error_parser = ErrorParser()
        self.auto_fixer = AutoFixer()
        self.debugger = DebuggerCore()
        self.strategy = DebuggingStrategy()
        self.rollback_manager = RollbackManager()
        self.patch_tracker = PatchTrackingManager()
        self.reporter = DebuggerReporter()
        self.max_retries = max_retries
        self.enable_ai_fixes = enable_ai_fixes
        self.failed_tests = []

    def run_debug_cycle(self):
        """
        Runs a full debugging cycle:
        1. Executes tests.
        2. Analyzes failures.
        3. Applies fixes.
        4. Validates with re-testing.
        5. Logs and reports results.
        """
        self.logger.log("Starting DebugAgent session...", level=logging.INFO)

        # Step 1: Run Tests
        self.failed_tests = run_tests()
        if not self.failed_tests:
            self.logger.log("All tests passed. No debugging needed.", level=logging.INFO)
            return

        for attempt in range(self.max_retries):
            self.logger.log(f"Debugging attempt {attempt + 1}/{self.max_retries}...", level=logging.INFO)
            
            # Step 2: Parse Errors
            error_details = self.error_parser.analyze_errors(self.failed_tests)

            # Step 3: Generate Fixes
            fixes_applied = self.apply_fixes(error_details)

            if fixes_applied:
                # Step 4: Re-run Tests
                self.failed_tests = run_tests()
                if not self.failed_tests:
                    self.logger.log("All fixes were successful!", level=logging.INFO)
                    break
                else:
                    self.logger.log(f"Remaining failures: {len(self.failed_tests)}", level=logging.WARNING)

            # Step 5: Rollback if needed
            self.rollback_manager.rollback_failed_fixes()
        
        # Step 6: Generate Debugging Report
        self.reporter.generate_report(self.failed_tests)
        self.logger.log("Debugging session completed.", level=logging.INFO)

    def apply_fixes(self, error_details):
        """
        Applies automated fixes to identified issues.
        Returns True if any fixes were successfully applied.
        """
        fixes_applied = False
        for error in error_details:
            if self.enable_ai_fixes:
                fix = self.strategy.generate_fix(error)
            else:
                fix = self.auto_fixer.attempt_fix(error)

            if fix:
                self.patch_tracker.record_fix(error, fix)
                fixes_applied = True
        
        return fixes_applied


if __name__ == "__main__":
    agent = DebugAgent()
    agent.run_debug_cycle()