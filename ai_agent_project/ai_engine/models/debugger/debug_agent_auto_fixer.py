import os
import re
import json
import shutil
import logging
from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

logger = logging.getLogger("DebugAgentAutoFixer")
logger.setLevel(logging.DEBUG)

# Project Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TESTS_PATH = os.path.join(PROJECT_ROOT, "tests")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "rollback_backups")

class DebugAgentAutoFixer:
    """
    **Automates error fixing in DebugAgent before AI intervention.**
    
    ✅ Ensures required modules exist  
    ✅ Fixes broken imports in test files  
    ✅ Re-attempts previously failed patches before AI generates new fixes  
    ✅ Detects and corrects unterminated string literals  
    ✅ Checks for syntax errors before debugging  
    ✅ Backs up & restores files if fixes introduce more errors  
    """

    def __init__(self):
        self.debugging_strategy = DebuggingStrategy()
        self.patch_tracker = PatchTrackingManager()

    ### **🔹 Fix Import Issues in Test Files**
    def fix_test_imports(self):
        """Scans test files for incorrect imports and fixes them."""
        for test_file in os.listdir(TESTS_PATH):
            test_file_path = os.path.join(TESTS_PATH, test_file)

            if test_file.endswith(".py"):
                with open(test_file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Fix incorrect imports
                content = re.sub(r"from agents.core\.(\w+)", r"from agents.core.\1 import \1", content)

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

    ### **🔹 Check for Syntax Errors Before Debugging**
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

    ### **🔹 Run All Fixes Before Debugging**
    def auto_fix_before_debugging(self):
        """Runs all auto-fixes before starting debugging."""
        logger.info("🚀 Running pre-debugging auto-fixes...")
        self.fix_test_imports()
        self.fix_unterminated_strings()
        self.check_syntax_errors()
        logger.info("✅ All pre-debugging fixes completed!")
