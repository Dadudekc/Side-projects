"""

This module contains test methods for the DebuggingStrategy class in the ai_engine.models.debugger.debugging_strategy module.

Test methods:
- test_generate_patch_with_ai: A test to ensure that the generate_patch function successfully generates a patch when AST-based fixes are not applicable.
- test_generate_patch_ai_fails: A test to check the behavior of generate_patch when the AI fails to create a patch.
- test_generate_patch_ast_based: A test to confirm that the generate_patch function generates the appropriate
"""

import json
import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy

logger = logging.getLogger("TestDebuggingStrategy")


@pytest.fixture
def strategy():
    """Fixture to initialize DebuggingStrategy and clear cache before tests."""
    strat = DebuggingStrategy()
    strat.learning_db = {}  # Clear stored patches
    return strat


# ** Fix for AIModelManager.generate_patch never being called **
@patch("ai_engine.models.debugger.debugging_strategy.AIModelManager.generate_patch")
def test_generate_patch_with_ai(mock_generate_patch, strategy):
    """Test AI patch generation when AST-based fixes don't apply."""
    mock_generate_patch.return_value = "--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n+print('Fixed')"

    # Ensure cache is cleared before test
    strategy.learning_db = {}  

    patch_result = strategy.generate_patch("TypeError", "some code", "test_example.py")

    assert patch_result is not None
    assert "print('Fixed')" in patch_result
    mock_generate_patch.assert_called_once()  # Fix: Ensure it's really called


@patch("ai_engine.models.debugger.debugging_strategy.AIModelManager.generate_patch", return_value=None)
def test_generate_patch_ai_fails(mock_generate_patch, strategy):
    """Test when AI fails to generate a patch."""
    strategy.learning_db = {}  # Fix: Ensure stored patches are cleared
    patch_result = strategy.generate_patch("TypeError", "some code", "test_example.py")

    assert patch_result is None  # Fix: AI should fail as expected
    mock_generate_patch.assert_called_once()


# ** Fix for AIConfidenceManager missing `get_confidence` method **
@patch("ai_engine.models.debugger.debugging_strategy.find_class_in_file", return_value=10)
def test_generate_patch_ast_based(mock_find_class, strategy):
    """Test AST-based missing method stub generation."""
    strategy.learning_db = {}  

    patch_result = strategy.generate_patch("no attribute 'run_task'", "some code", "test_example.py")

    assert patch_result is not None
    assert "def run_task(self, task):" in patch_result
    mock_find_class.assert_called_once()


# ** Fix subprocess.run Exception handling in patching **
@patch("subprocess.run", side_effect=Exception("Patch failed"))
def test_apply_patch_failure(mock_subprocess, strategy):
    """Test handling of failed patch application."""
    patch_data = "--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n+print('Fixed')"

    with patch("builtins.open", create=True):
        result = strategy.apply_patch(patch_data)

    assert result is False  # Fix: Ensure function handles failure gracefully
    mock_subprocess.assert_called_once()
