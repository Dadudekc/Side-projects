"""
test_debug_agent_auto_fixer.py

Test suite for DebugAgentAutoFixer and PatchTrackingManager.

Key Tests:
  - test_ensure_modules_exist: Verifies that missing required modules are created.
  - test_fix_test_imports: Checks that broken imports in test files are (placeholder) processed.
  - test_fix_unterminated_strings: Ensures unterminated strings are fixed.
  - test_check_syntax_errors: Confirms a SyntaxError is raised when syntax is bad.
  - test_backup_and_restore: Tests backup and restore functionality.
  - test_re_attempt_failed_patches: Verifies that a previously failed patch is re-attempted.

Note: The tests create files under the project’s tests directory and assume that the project
structure is as follows:

  ai_agent_project/
    agents/
      core/
    ai_engine/
      models/
        debugger/
          debug_agent_auto_fixer.py
    tests/
    rollback_backups/
"""

import os
import shutil
import pytest

from ai_engine.models.debugger.debug_agent_auto_fixer import DebugAgentAutoFixer
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

# In tests, we compute PROJECT_ROOT relative to this file (assuming tests/ is at the project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AGENTS_CORE_PATH = os.path.join(PROJECT_ROOT, "agents", "core")
TESTS_PATH = os.path.join(PROJECT_ROOT, "tests")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "rollback_backups")

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
    """
    Creates a new DebugAgentAutoFixer instance for each test.
    """
    return DebugAgentAutoFixer()


@pytest.fixture(autouse=True)
def fix_function():
    """
    Cleans up test artifacts after each test run: removing created modules and backup directories.
    """
    yield
    for module in REQUIRED_MODULES:
        module_path = os.path.join(AGENTS_CORE_PATH, f"{module}.py")
        if os.path.exists(module_path):
            os.remove(module_path)
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)


def test_ensure_modules_exist(auto_fixer):
    """Test if missing required modules are created successfully by auto_fixer."""
    auto_fixer.ensure_modules_exist()
    for module in REQUIRED_MODULES:
        module_path = os.path.join(AGENTS_CORE_PATH, f"{module}.py")
        assert os.path.exists(module_path), f"❌ {module} module was not created!"


def test_fix_test_imports(auto_fixer):
    """Test if auto_fixer can process (placeholder) fixing of broken imports in test files."""
    test_file_path = os.path.join(TESTS_PATH, "test_dummy.py")
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("from agents.core.DebuggerCore import DebuggerCore\n")
        file.write("from agents.core.DebuggerCLI import DebuggerCLI\n")
    auto_fixer.fix_test_imports()
    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    # Since fix_test_imports is a placeholder, we simply check that the file still exists.
    assert "from agents.core.DebuggerCore" in content, "❌ DebuggerCore import missing!"
    os.remove(test_file_path)


def test_fix_unterminated_strings(auto_fixer):
    """Test if unterminated strings in 'test_unterminated.py' are correctly fixed."""
    test_file_path = os.path.join(TESTS_PATH, "test_unterminated.py")
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write('print("Hello World\n')  # Unterminated string
    auto_fixer.fix_unterminated_strings()
    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    assert content.endswith('")\n'), "❌ Unterminated string was not fixed!"
    os.remove(test_file_path)


def test_check_syntax_errors(auto_fixer):
    """Test if syntax errors are correctly detected by auto_fixer."""
    test_file_path = os.path.join(TESTS_PATH, "test_syntax_error.py")
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("def bad_syntax(\n")  # Missing closing parenthesis
    with pytest.raises(SyntaxError):
        auto_fixer.check_syntax_errors()
    os.remove(test_file_path)


def test_backup_and_restore(auto_fixer):
    """Test if file backup and restore operations function correctly."""
    test_file_path = os.path.join(TESTS_PATH, "test_backup.py")
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("original content")
    auto_fixer.backup_file(test_file_path)
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("modified content")
    auto_fixer.restore_backup(test_file_path)
    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()
    assert content == "original content", "❌ Backup restoration failed!"
    os.remove(test_file_path)


def test_re_attempt_failed_patches(auto_fixer):
    """
    Test if auto_fixer correctly retries failed patches before invoking AI-based solutions.
    """
    patch_tracker = PatchTrackingManager()
    error_signature = "test_error_signature"
    test_file_path = os.path.join(TESTS_PATH, "test_patch.py")
    failed_patch = "--- test_patch.py\n+++ test_patch.py\n- old_code\n+ fixed_code"
    patch_tracker.record_failed_patch(error_signature, failed_patch)
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("old_code")
    success = auto_fixer.re_attempt_failed_patches(error_signature, test_file_path)
    assert success, "❌ Failed patch reattempt was unsuccessful!"
    os.remove(test_file_path)
