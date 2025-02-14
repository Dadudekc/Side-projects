#!/usr/bin/env python
"""
Unified debugger_core.py

This module provides a unified debugging system with two modes:

• Simple Mode:
  - Runs tests with plain pytest output.
  - Parses failures.
  - Uses ApplyFix to attempt automatic fixes.
  - Logs attempts via DebuggerLogger.
  - Retries fixes and rolls back if necessary.

• Advanced Mode:
  - Runs tests using pytest-json-report.
  - Archives JSON reports.
  - Extracts detailed failure info (including code context).
  - Uses a DebuggingStrategy to generate and apply patches.
  - Maintains a learning DB (JSON file) of error signatures.
  - Re-runs tests to validate fixes.
  
Usage:
    # For simple mode:
    debugger = DebuggerCore()
    debugger.debug(max_retries=3)
    
    # For advanced mode:
    from debugging_strategy import DebuggingStrategy
    strategy = DebuggingStrategy()  # Your implementation here
    debugger = DebuggerCore(debug_strategy=strategy)
    debugger.debug()
"""

import os
import sys
import json
import logging
import subprocess
import shutil
import re
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

from debugger_logger import DebuggerLogger
from apply_fix import ApplyFix  # The patching system
from debugging_strategy import DebuggingStrategy

# Configure module-level logger
logger = logging.getLogger("DebuggerCore")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    # Add console handler if not already present
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class DebuggerCore:
    """
    Unified debugging system supporting two modes:
    
    • Simple mode: Uses ApplyFix and plain pytest output.
    • Advanced mode: Uses DebuggingStrategy, pytest-json-report,
      and a learning database.
    """

    LEARNING_DB_FILE = "learning_db.json"
    REPORT_ARCHIVE_DIR = "reports_archive"
    MAX_ATTEMPTS = 3

    def __init__(self, debug_strategy: Optional[DebuggingStrategy] = None):
        """
        If debug_strategy is provided, advanced mode is used.
        Otherwise, the simple mode (ApplyFix) is used.
        """
        self.debug_strategy = debug_strategy
        if debug_strategy is None:
            self.mode = "simple"
            self.apply_fix = ApplyFix()
        else:
            self.mode = "advanced"
        self.debugger_logger = DebuggerLogger()

    # ===== Simple Mode Methods =====
    def run_tests_simple(self) -> str:
        """
        Runs tests using pytest (simple mode) and returns the output.
        """
        logger.info("🚀 Running pytest to identify errors (simple mode).")
        try:
            result = subprocess.run(
                ["pytest", "tests", "--maxfail=5", "--tb=short", "-q"],
                capture_output=True,
                text=True
            )
            logger.debug(f"📝 Pytest output:\n{result.stdout}")
            return result.stdout
        except Exception as e:
            logger.error(f"❌ Failed to run tests: {e}")
            return ""

    def parse_test_failures_simple(self, test_output: str) -> List[Dict[str, str]]:
        """
        Parses pytest output to extract test failures (simple mode).
        """
        logger.info("🔍 Parsing test failures from pytest output (simple mode)...")
        failures = []
        for line in test_output.splitlines():
            if "FAILED" in line:
                parts = line.split(" - ")
                if len(parts) >= 2:
                    failures.append({
                        "file": parts[0].strip(),
                        "error": parts[1].strip()
                    })
        logger.info(f"⚠️ Found {len(failures)} failing tests.")
        return failures

    def _debug_simple(self, max_retries: int = 3):
        """
        Main simple debugging loop.
        """
        logger.info(f"🔄 Starting simple debugging loop (max retries: {max_retries})")
        modified_files = []

        for attempt in range(1, max_retries + 1):
            test_output = self.run_tests_simple()
            failures = self.parse_test_failures_simple(test_output)

            if not failures:
                logger.info("✅ All tests passed! Debugging complete.")
                return {"status": "success", "message": "All tests passed!"}

            for failure in failures:
                file_name = failure["file"]
                error_message = failure["error"]

                logger.info(f"🔧 Attempting fix for {file_name} - Error: {error_message}")

                fix_success = self.apply_fix.apply_fix(error_message, file_name, test_output)

                # Log the debugging attempt
                self.debugger_logger.log_attempt(failure, "Generated Patch", fix_success)

                if fix_success:
                    modified_files.append(file_name)
                    logger.info(f"✅ Fix applied successfully to {file_name}")
                else:
                    logger.warning(f"❌ Failed to fix {file_name}. Rolling back changes.")
                    self.rollback_changes(modified_files)
                    return {"status": "error", "message": f"Could not fix {file_name} automatically."}

        logger.error("🛑 Max retries reached. Debugging unsuccessful.")
        return {"status": "error", "message": "Max retries reached. Debugging failed."}

    # ===== Advanced Mode Methods =====
    def run_tests_advanced(self) -> List[Dict[str, Any]]:
        """
        Runs tests using pytest-json-report and returns a list of error dicts.
        Each error dict contains:
          - test_filename
          - error_message
          - code_context
        """
        errors = []
        report_file = "report.json"

        # Remove old report if it exists
        if os.path.exists(report_file):
            os.remove(report_file)

        try:
            result = subprocess.run(
                [
                    "pytest",
                    "tests",
                    "--json-report",
                    f"--json-report-file={report_file}",
                    "--disable-warnings",
                    "--maxfail=1"
                ],
                capture_output=True,
                text=True
            )
            logger.debug("Pytest output:\n%s", result.stdout)
            logger.debug("Pytest errors:\n%s", result.stderr)
        except Exception as e:
            logger.error("Error running tests: %s", e)
            return errors

        if not os.path.exists(report_file):
            logger.error("JSON report file not found. Ensure pytest-json-report is installed.")
            return errors

        try:
            with open(report_file, "r", encoding="utf-8") as f:
                report_data = json.load(f)
        except Exception as e:
            logger.error("Failed to load JSON report: %s", e)
            return errors

        # Archive the report before parsing further
        self.archive_report(report_file)

        tests_data = report_data.get("tests", [])
        for t in tests_data:
            if t.get("outcome") == "failed":
                nodeid = t.get("nodeid", "")
                crash_data = t.get("call", {}).get("crash", {})
                error_message = crash_data.get("message")
                if not error_message:
                    error_message = str(t.get("longrepr", "No error message."))
                location = t.get("location", [])

                code_context = "No code context available"
                if location and len(location) >= 2:
                    try:
                        error_file = location[0]
                        error_line = int(location[1])
                        with open(error_file, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            start = max(error_line - 3, 0)
                            end = min(error_line + 2, len(lines))
                            code_context = "".join(lines[start:end])
                    except Exception as ex:
                        code_context = f"Could not read code context: {ex}"

                errors.append({
                    "test_filename": nodeid.split("::")[0],
                    "error_message": error_message,
                    "code_context": code_context
                })

        return errors

    def archive_report(self, report_file="report.json"):
        """
        Archives the JSON report to a timestamped file.
        """
        if not os.path.exists(self.REPORT_ARCHIVE_DIR):
            os.makedirs(self.REPORT_ARCHIVE_DIR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_name = os.path.join(self.REPORT_ARCHIVE_DIR, f"report_{timestamp}.json")
        try:
            shutil.move(report_file, archived_name)
            logger.info("Archived JSON report to %s", archived_name)
        except Exception as e:
            logger.error("Failed to archive JSON report: %s", e)

    def load_learning_db(self) -> Dict[str, Any]:
        """
        Loads the learning database from a JSON file.
        """
        if os.path.exists(self.LEARNING_DB_FILE):
            try:
                with open(self.LEARNING_DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error("Failed to load learning DB: %s", e)
                return {}
        return {}

    def save_learning_db(self, db: Dict[str, Any]):
        """
        Saves the learning database to a JSON file.
        """
        try:
            with open(self.LEARNING_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4)
        except Exception as e:
            logger.error("Failed to save learning DB: %s", e)

    def compute_error_signature(self, error_message: str, code_context: str) -> str:
        """
        Computes a unique error signature based on the error message and code context.
        """
        h = hashlib.sha256()
        h.update(error_message.encode('utf-8'))
        h.update(code_context.encode('utf-8'))
        return h.hexdigest()

    def apply_patch_to_file(self, patch: str) -> bool:
        """
        Applies the patch using the provided DebuggingStrategy.
        """
        if self.debug_strategy:
            return self.debug_strategy.apply_patch(patch)
        return False

    def re_run_tests(self) -> bool:
        """
        Re-runs tests after applying a patch to verify if the fix resolved the issue.
        """
        result = subprocess.run(
            ["pytest", "tests", "--maxfail=1", "--disable-warnings"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("Tests passed after applying patch.")
            return True
        else:
            logger.error("Tests failed after patching:\n%s", result.stdout)
            return False

    def _debug_advanced(self):
        """
        Advanced debugging cycle using DebuggingStrategy and a learning DB.
        """
        logger.info("Starting advanced debugging cycle...")

        errors = self.run_tests_advanced()
        if not errors:
            logger.info("No errors detected. Exiting cycle.")
            return

        learning_db = self.load_learning_db()

        for err in errors:
            error_sig = self.compute_error_signature(err["error_message"], err["code_context"])
            logger.info("Error signature: %s", error_sig)

            attempts = learning_db.get(error_sig, {}).get("attempts", 0)
            if attempts > self.MAX_ATTEMPTS:
                logger.error("Error signature %s exceeded max attempts. Manual review required.", error_sig)
                learning_db.setdefault(error_sig, {})["needs_manual_review"] = True
                self.save_learning_db(learning_db)
                continue

            existing_patch = learning_db.get(error_sig, {}).get("patch")
            if existing_patch:
                logger.info("Using existing patch from learning DB for signature %s", error_sig)
                patch = existing_patch
                attempts += 1
            else:
                patch = self.debug_strategy.generate_patch(
                    err["error_message"],
                    err["code_context"],
                    err["test_filename"]
                )
                attempts = 1

            if not patch:
                logger.error("No patch generated for error: %s", err["error_message"])
                continue

            success = self.debug_strategy.apply_patch(patch)
            learning_db[error_sig] = {
                "patch": patch,
                "attempts": attempts,
                "success": success
            }
            self.save_learning_db(learning_db)

            if success:
                if self.re_run_tests():
                    logger.info("Patch for signature %s was successful!", error_sig)
                    learning_db[error_sig]["success"] = True
                    learning_db[error_sig]["attempts"] = 0
                    self.save_learning_db(learning_db)
                else:
                    logger.error("Patch did not resolve issues for signature %s. Rolling back is not yet implemented.", error_sig)
                    learning_db[error_sig]["success"] = False
                    self.save_learning_db(learning_db)
            else:
                logger.error("Failed to apply patch for signature %s. Marking as fail.", error_sig)
                learning_db[error_sig]["success"] = False
                self.save_learning_db(learning_db)

        logger.info("Advanced debugging cycle finished.")

    # ===== Common Methods =====
    def rollback_changes(self, modified_files: List[str]):
        """
        Rolls back changes to avoid breaking the project.
        """
        if not modified_files:
            logger.info("No files modified, nothing to rollback.")
            return

        for file in modified_files:
            backup_path = f"{file}.backup"
            if os.path.exists(backup_path):
                shutil.copy(backup_path, file)
                logger.info(f"🔄 Rolled back {file} from backup.")

    def show_logs(self):
        """
        Prints all logs stored by DebuggerLogger.
        """
        logs = self.debugger_logger.get_logs()
        for log_entry in logs:
            logger.info(f"📝 Log Entry: {log_entry}")

    def debug(self, max_retries: int = 3):
        """
        Main debugging loop that selects the mode based on initialization.
        """
        if self.mode == "simple":
            return self._debug_simple(max_retries)
        elif self.mode == "advanced":
            return self._debug_advanced()
        else:
            logger.error("Unknown debugging mode.")
            return {"status": "error", "message": "Unknown debugging mode."}


# For testing the module independently, you might add:
if __name__ == "__main__":
    # To run in simple mode:
    debugger = DebuggerCore()
    debugger.debug(max_retries=3)

    # To run in advanced mode (requires a valid DebuggingStrategy implementation):
    # from debugging_strategy import DebuggingStrategy
    # strategy = DebuggingStrategy()  # Replace with your concrete implementation
    # debugger = DebuggerCore(debug_strategy=strategy)
    # debugger.debug()
