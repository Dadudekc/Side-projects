import os
import re
import json
import shutil
import logging
from typing import List, Dict, Optional
from debugging_strategy import DebuggingStrategy
from patch_tracking_manager import PatchTrackingManager

logger = logging.getLogger("DebugAgentAutoFixer")
logger.setLevel(logging.DEBUG)

# Project Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AGENTS_CORE_PATH = os.path.join(PROJECT_ROOT, "agents", "core")
TESTS_PATH = os.path.join(PROJECT_ROOT, "tests")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "rollback_backups")

# Required Modules
REQUIRED_MODULES = [
    "AIConfidenceManager",
    "AIPatchOptimizer",
    "AIPatchRetryManager",
    "AIPatchReviewManager",
    "AIRollbackAnalysis",
    "AutoFixer",
    "DebuggerCLI",
    "DebuggerCore",
    "debugger_reporter",
    "debugger_runner",
    "debugging_strategy",
    "TestRetryManager"
]


class DebugAgentAutoFixer:
    """
    **Automates error fixing in DebugAgent before AI intervention.**
    
    Features:
    ✅ **Ensures required modules exist**  
    ✅ **Fixes broken imports in test files**  
    ✅ **Reattempts previously failed patches before AI generates new fixes**  
    ✅ **Detects and corrects unterminated string literals**  
    ✅ **Checks for syntax errors before debugging**  
    ✅ **Backs up & restores files if fixes introduce more errors**
    """

    def __init__(self):
        self.debugging_strategy = DebuggingStrategy()
        self.patch_tracker = PatchTrackingManager()

    ### **🔹 Ensure Required Modules Exist**
    def ensure_modules_exist(self):
        """Creates missing module files to prevent import errors."""
        for module in REQUIRED_MODULES:
            module_path = os.path.join(AGENTS_CORE_PATH, f"{module}.py")
            if not os.path.exists(module_path):
                with open(module_path, "w", encoding="utf-8") as file:
                    file.write(f'''# Placeholder for {module}
class {module}:
    def __init__(self):
        pass
''')
                logger.info(f"✅ Created missing module: {module_path}")

    ### **🔹 Fix Import Issues in Test Files**
    def fix_test_imports(self):
        """Scans test files for incorrect imports and fixes them."""
        for test_file in os.listdir(TESTS_PATH):
            test_file_path = os.path.join(TESTS_PATH, test_file)

            if test_file.endswith(".py"):
                with open(test_file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Fix incorrect imports
                for module in REQUIRED_MODULES:
                    content = content.replace(f"from agents.core.{module}", f"from agents.core.{module} import {module}")

                with open(test_file_path, "w", encoding="utf-8") as file:
                    file.write(content)

                logger.info(f"✅ Fixed imports in {test_file}")

    ### **🔹 Detect and Fix Unterminated Strings**
    def fix_unterminated_strings(self):
        """Finds and fixes unterminated string literals in test files."""
        for test_file in os.listdir(TESTS_PATH):
            test_file_path = os.path.join(TESTS_PATH, test_file)
            if test_file.endswith(".py"):
                with open(test_file_path, "r", encoding="utf-8") as file:
                    content = file.readlines()

                fixed_lines = []
                for line in content:
                    if line.count('"') % 2 != 0 or line.count("'") % 2 != 0:
                        line += '"'  # Close the unterminated string
                    fixed_lines.append(line)

                with open(test_file_path, "w", encoding="utf-8") as file:
                    file.writelines(fixed_lines)

                logger.info(f"✅ Fixed unterminated strings in {test_file}")

    ### **🔹 Detect Syntax Errors Before Debugging**
    def check_syntax_errors(self):
        """Detects and logs syntax errors in test files before running tests."""
        for test_file in os.listdir(TESTS_PATH):
            test_file_path = os.path.join(TESTS_PATH, test_file)
            if test_file.endswith(".py"):
                try:
                    with open(test_file_path, "r", encoding="utf-8") as file:
                        compile(file.read(), test_file_path, 'exec')
                except SyntaxError as e:
                    logger.error(f"❌ Syntax Error in {test_file}: {e}")

    ### **🔹 Re-Attempt Failed Patches Before AI**
    def re_attempt_failed_patches(self, error_signature: str, file_path: str) -> bool:
        """Retries previously failed patches before AI generates new ones."""
        failed_patches = self.patch_tracker.get_failed_patches(error_signature)
        if not failed_patches:
            logger.info(f"🚫 No failed patches available for {error_signature}. Moving to AI fix.")
            return False

        for patch in failed_patches:
            logger.info(f"🔄 Retrying failed patch for {file_path}")
            self.backup_file(file_path)

            if self.debugging_strategy.apply_patch(patch):
                logger.info(f"✅ Patch successfully applied for {error_signature}")
                self.patch_tracker.record_successful_patch(error_signature, patch)
                return True  # Stop if a patch works
            
            self.restore_backup(file_path)  # Rollback if patch fails

        return False

    ### **🔹 Backup & Rollback Mechanism**
    def backup_file(self, file_path: str):
        """Creates a backup before applying patches."""
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
        if not os.path.exists(backup_path):
            shutil.copy(file_path, backup_path)
            logger.info(f"📁 Backed up {file_path} -> {backup_path}")

    def restore_backup(self, file_path: str):
        """Restores a file from backup in case of rollback."""
        backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
        if os.path.exists(backup_path):
            shutil.copy(backup_path, file_path)
            logger.warning(f"🔄 Rolled back {file_path} from backup.")

    ### **🔹 Run All Fixes Before Debugging**
    def auto_fix_before_debugging(self):
        """Runs all auto-fixes before starting debugging."""
        logger.info("🚀 Running pre-debugging auto-fixes...")
        self.ensure_modules_exist()
        self.fix_test_imports()
        self.fix_unterminated_strings()
        self.check_syntax_errors()
        logger.info("✅ All pre-debugging fixes completed!")

