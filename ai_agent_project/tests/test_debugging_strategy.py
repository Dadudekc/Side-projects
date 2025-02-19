"""
test_debugging_strategy.py

This module contains test cases for the DebuggingStrategy class in the 
ai_engine.models.debugger.debugging_strategy module.

Tested Methods:
- test_generate_patch_with_ai: Ensures AIModelManager generates a patch when AST-based fixes aren't applicable.
- test_generate_patch_ai_fails: Checks behavior when AI fails to generate a patch.
- test_generate_patch_ast_based: Confirms AST-based fixes correctly generate method stubs.
- test_apply_patch_failure: Ensures subprocess exceptions during patching are handled properly.

Dependencies:
- pytest
- unittest.mock (MagicMock, patch)
"""

import json
import logging
import os
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy

logger = logging.getLogger("TestDebuggingStrategy")


@pytest.fixture
def strategy():
    """Fixture to initialize DebuggingStrategy and clear the learning database before tests."""
    strat = DebuggingStrategy()
    strat.learning_db = {}  # Reset stored patches before tests
    return strat


# ** Fix for AIModelManager.generate_patch not being called **
@patch("ai_engine.models.debugger.debugging_strategy.AIModelManager.generate_patch")
def test_generate_patch_with_ai(mock_generate_patch, strategy):
    """
    Test AI-based patch generation when AST-based fixes don't apply.

    - Mocks AIModelManager to return a predefined patch.
    - Ensures generate_patch calls AIModelManager when AST fixes are unavailable.
    - Verifies the returned patch contains expected changes.
    """
    mock_generate_patch.return_value = "--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n+print('Fixed')"

    # Ensure learning database is empty before the test
    strategy.learning_db = {}

    patch_result = strategy.generate_patch("TypeError", "some code", "test_example.py")

    assert patch_result is not None, "AI patch should be generated"
    assert "print('Fixed')" in patch_result, "Expected AI-generated fix missing from patch"
    mock_generate_patch.assert_called_once(), "AIModelManager.generate_patch should be called once"


@patch("ai_engine.models.debugger.debugging_strategy.AIModelManager.generate_patch", return_value=None)
def test_generate_patch_ai_fails(mock_generate_patch, strategy):
    """
    Test behavior when AI fails to generate a patch.

    - Mocks AIModelManager to return None.
    - Ensures that generate_patch correctly handles AI failure.
    """
    strategy.learning_db = {}  # Clear stored patches
    patch_result = strategy.generate_patch("TypeError", "some code", "test_example.py")

    assert patch_result is None, "Patch result should be None when AI generation fails"
    mock_generate_patch.assert_called_once(), "AIModelManager.generate_patch should be called exactly once"


# ** Fix for missing `get_confidence` method in AIConfidenceManager **
@patch("ai_engine.models.debugger.debugging_strategy.find_class_in_file", return_value=10)
def test_generate_patch_ast_based(mock_find_class, strategy):
    """
    Test AST-based method stub generation for missing attributes.

    - Simulates a missing method error.
    - Ensures generate_patch generates a valid method stub via AST.
    """
    strategy.learning_db = {}  # Ensure learning DB is empty

    patch_result = strategy.generate_patch("no attribute 'run_task'", "some code", "test_example.py")

    assert patch_result is not None, "AST-based patch generation should return a valid patch"
    assert "def run_task(self, task):" in patch_result, "Expected method stub missing from patch"
    mock_find_class.assert_called_once(), "find_class_in_file should be called exactly once"


# ** Fix subprocess.run Exception handling in patching **
@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "patch"))
def test_apply_patch_failure(mock_subprocess, strategy):
    """
    Test handling of failed patch application.

    - Mocks subprocess.run to simulate a failure.
    - Ensures apply_patch gracefully handles patch failures.
    """
    patch_data = "--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n+print('Fixed')"

    with patch("builtins.open", create=True):
        result = strategy.apply_patch(patch_data)

    assert result is False, "apply_patch should return False on failure"
    mock_subprocess.assert_called_once(), "subprocess.run should be called once"

