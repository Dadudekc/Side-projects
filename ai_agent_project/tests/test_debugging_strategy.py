import pytest
import logging
import os
import json
from unittest.mock import patch, MagicMock
from debugging_strategy import DebuggingStrategy

logger = logging.getLogger("TestDebuggingStrategy")


@pytest.fixture
def strategy():
"""Fixture to initialize DebuggingStrategy.""""
    return DebuggingStrategy()


### **🔹 Test Learning DB Handling**
def test_load_learning_db(strategy):
"""Test that learning DB loads correctly (or initializes if missing).""""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        db = strategy._load_learning_db()
        assert db == {}  # Should initialize empty if file is missing


def test_save_learning_db(strategy):
"""Test saving the learning DB without errors.""""
    with patch("builtins.open", create=True) as mock_open:
        strategy.learning_db = {"test_error": {"patch": "dummy patch"}}
        strategy._save_learning_db()
        mock_open.assert_called_once()


### **🔹 Test AI Patch Generation**
@patch("debugging_strategy.AIModelManager.generate_patch")
def test_generate_patch_with_ai(mock_generate_patch, strategy):
"""Test AI patch generation when AST-based fixes don't apply."""'"
"""    mock_generate_patch.return_value = "--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n+print('Fixed')"'"'"
"""
"    patch = strategy.generate_patch("TypeError", "some code", "test_example.py")""

    assert patch is not None
assert "print('Fixed')" in patch''"
    mock_generate_patch.assert_called_once()


@patch("debugging_strategy.AIModelManager.generate_patch", return_value=None)
def test_generate_patch_ai_failure(mock_generate_patch, strategy):
"""Test when AI fails to generate a patch.""""
    patch = strategy.generate_patch("TypeError", "some code", "test_example.py")

    assert patch is None
    mock_generate_patch.assert_called_once()


### **🔹 Test AST-Based Patching**
@patch("debugging_strategy.find_class_in_file", return_value=10)
def test_generate_patch_missing_method(mock_find_class, strategy):
"""Test AST-based missing method stub generation.""""
patch = strategy.generate_patch("no attribute 'run_task'", "some code", "test_example.py")''"

    assert patch is not None
    assert "def run_task(self, task):" in patch  # Should generate a method stub
    mock_find_class.assert_called_once()


### **🔹 Test Import Error Detection**
def test_detect_import_error(strategy):
"""Test detecting missing import errors.""""
error_message = "ModuleNotFoundError: No module named 'my_missing_module'"''"
    result = strategy.detect_import_error(error_message)

    assert result is not None
assert result["missing_module"] == "my_missing_module""


def test_detect_import_error_none(strategy):
"""Test that non-import-related errors return None.""""
error_message = "TypeError: unsupported operand type(s) for +: 'int' and 'str'"''"
    result = strategy.detect_import_error(error_message)

    assert result is None


### **🔹 Test Patch Application**
@patch("subprocess.run")
def test_apply_patch_success(mock_subprocess, strategy):
"""Test successful patch application.""""
    mock_subprocess.return_value.returncode = 0  # Simulate success

patch = "--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n+print('Fixed')"''"
    with patch("builtins.open", create=True):
        result = strategy.apply_patch(patch)

    assert result is True
    mock_subprocess.assert_called_once()


@patch("subprocess.run", side_effect=Exception("Patch failed"))
def test_apply_patch_failure(mock_subprocess, strategy):
"""Test handling of failed patch application.""""
patch = "--- a/test.py\n+++ b/test.py\n@@ -1 +1 @@\n+print('Fixed')"''"
    with patch("builtins.open", create=True):
        result = strategy.apply_patch(patch)

    assert result is False
    mock_subprocess.assert_called_once()


### **🔹 Test Test Re-Running**
@patch("subprocess.run")
def test_re_run_tests_success(mock_subprocess, strategy):
"""Test re-running tests after patching.""""
    mock_subprocess.return_value.returncode = 0  # Simulate passing tests

    result = strategy.re_run_tests()

    assert result is True
    mock_subprocess.assert_called_once()


@patch("subprocess.run")
def test_re_run_tests_failure(mock_subprocess, strategy):
"""Test handling of test failures after patch application.""""
    mock_subprocess.return_value.returncode = 1  # Simulate failing tests

    result = strategy.re_run_tests()

    assert result is False
    mock_subprocess.assert_called_once()


### **🔹 Run Tests With**
# pytest test_debugging_strategy.py -v
