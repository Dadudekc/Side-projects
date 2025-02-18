"""

This module is designed to perform multiple tests on the 'DebugAgentAutoFixer' and 'PatchTrackingManager' classes. 

Tests include:

(1) auto_fixer: Fixture to provide a DebugAgentAutoFixer instance for the tests.
(2) fix_function: Fixture that runs after each test to ensure a clean test environment by removing test artifacts.
(3) test_ensure_modules_exist: Test if auto_fixer can create required modules if they don't exist.
(4
"""

import json
import os
import shutil

import pytest

from ai_engine.models.debugger.debug_agent_auto_fixer import DebugAgentAutoFixer
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

# Project Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AGENTS_CORE_PATH = os.path.join(PROJECT_ROOT, "..", "agents", "core")
TESTS_PATH = os.path.join(PROJECT_ROOT, "..", "tests")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "..", "rollback_backups")

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
    "AutoFixManager",
]


@pytest.fixture
def auto_fixer():
    """Fixture to provide a DebugAgentAutoFixer instance."""
    return DebugAgentAutoFixer()


@pytest.fixture(autouse=True)
def fix_function():
    """Ensures clean test runs by removing test artifacts."""
    yield
    for module in REQUIRED_MODULES:
        module_path = os.path.join(AGENTS_CORE_PATH, f"{module}.py")
        if os.path.exists(module_path):
            os.remove(module_path)

    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)


# 🟢 Test: Ensure Missing Modules Are Created
def test_ensure_modules_exist(auto_fixer):
    """Test if missing required modules are created."""
    auto_fixer.ensure_modules_exist()

    for module in REQUIRED_MODULES:
        module_path = os.path.join(AGENTS_CORE_PATH, f"{module}.py")
        assert os.path.exists(module_path), f"❌ {module} was not created!"


# 🟢 Test: Fix Import Issues in Test Files
def test_fix_test_imports(auto_fixer):
    """Test if auto_fixer can correct import issues in test files."""
    test_file_path = os.path.join(TESTS_PATH, "test_dummy.py")

    # Create a dummy test file with broken imports
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("from agents.core.DebuggerCore import DebuggerCore\n")
        file.write("from agents.core.DebuggerCLI import DebuggerCLI\n")

    auto_fixer.fix_test_imports()

    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert "import DebuggerCore" in content, "❌ DebuggerCore import not fixed!"
    assert "import DebuggerCLI" in content, "❌ DebuggerCLI import not fixed!"

    os.remove(test_file_path)


# 🟢 Test: Detect and Fix Unterminated Strings
def test_fix_unterminated_strings(auto_fixer):
    """Test if unterminated strings are fixed properly."""
    test_file_path = os.path.join(TESTS_PATH, "test_unterminated.py")

    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write('print("Hello World\n')  # Unterminated string

    auto_fixer.fix_unterminated_strings()

    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert content.endswith('")\n'), "❌ Unterminated string was not fixed!"
    os.remove(test_file_path)


# 🟢 Test: Detect Syntax Errors
def test_check_syntax_errors(auto_fixer):
    """Test if syntax errors are detected correctly."""
    test_file_path = os.path.join(TESTS_PATH, "test_syntax_error.py")

    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("def bad_syntax(\n")  # Missing closing parenthesis

    with pytest.raises(SyntaxError):
        auto_fixer.check_syntax_errors()

    os.remove(test_file_path)


# 🟢 Test: Backup and Restore Functionality
def test_backup_and_restore(auto_fixer):
    """Test if file backup and restore operations work properly."""
    test_file_path = os.path.join(TESTS_PATH, "test_backup.py")

    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("original content")

    auto_fixer.backup_file(test_file_path)

    # Overwrite the file
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("modified content")

    auto_fixer.restore_backup(test_file_path)

    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert content == "original content", "❌ Backup restoration failed!"
    os.remove(test_file_path)


# 🟢 Test: Re-Attempt Failed Patches Before AI
def test_re_attempt_failed_patches(auto_fixer):
    """Test if auto_fixer can retry failed patches before AI intervention."""
    patch_tracker = PatchTrackingManager()
    error_signature = "test_error_signature"
    file_path = os.path.join(TESTS_PATH, "test_patch.py")

    # Create a dummy failed patch
    failed_patch = "--- test_patch.py\n+++ test_patch.py\n- old_code\n+ fixed_code"

    # Record it as a failed patch
    patch_tracker.record_failed_patch(error_signature, failed_patch)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("old_code")

    success = auto_fixer.re_attempt_failed_patches(error_signature, file_path)
    assert success, "❌ Failed patch reattempt was unsuccessful!"

    os.remove(file_path)
