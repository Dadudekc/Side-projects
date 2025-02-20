"""
Unit tests for the AIModelManager class.

This suite covers:
- Persistence: saving and loading the model
- Patch generation using AI model selection and confidence scoring,
  including error handling
- Debugging prompt formatting
- Error signature computation
"""

import os
import sys
import logging
import pytest
from unittest.mock import patch, MagicMock

# Ensure the correct path is added for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ai_engine.models.ai_model_manager import AIModelManager
from ai_engine.confidence_manager import AIConfidenceManager


# =======================
# Pytest Fixture
# =======================
@pytest.fixture
def ai_model_manager():
    """Fixture to initialize an instance of AIModelManager for tests."""
    return AIModelManager()


# =======================
# Persistence Tests
# =======================
def test_save_model(ai_model_manager):
    """Test that the model can be saved via file write."""
    with patch("builtins.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.write = MagicMock()
        ai_model_manager.save_model("test_model")
        mock_open.assert_called_once()


def test_load_model(ai_model_manager):
    """Test that the model is loaded correctly from file."""
    with patch("builtins.open", create=True) as mock_open:
        # Simulate an empty JSON file
        mock_open.return_value.__enter__.return_value.read.return_value = "{}"
        result = ai_model_manager.load_model("test_model")
        assert result == {}


# =======================
# Patch Generation Tests
# =======================
@patch.object(AIConfidenceManager, "get_best_high_confidence_patch", return_value=None)
@patch.object(AIConfidenceManager, "assign_confidence_score", return_value=(0.8, "AI predicts success"))
@patch.object(AIModelManager, "_generate_with_model")
def test_generate_patch(mock_generate_with_model, mock_assign_confidence, mock_get_best_patch, ai_model_manager):
    """
    Test patch generation with model prioritization and confidence tracking.
    Simulate a scenario where the first model returns a valid patch.
    """
    # Simulate first model returns a valid patch; subsequent calls return None.
    mock_generate_with_model.side_effect = ["diff --git patch", None, None]
    patch_result = ai_model_manager.generate_patch("SyntaxError: invalid syntax",
                                                   "print('Hello World'",
                                                   "test_script.py")
    assert patch_result is not None
    assert "diff --git" in patch_result


@patch("ai_engine.models.ai_model_manager.AIConfidenceManager.assign_confidence_score", return_value=(0.8, "Confidence updated"))
@patch("ai_engine.models.ai_model_manager.AIConfidenceManager.store_patch")
@patch.object(AIModelManager, "_generate_with_model", return_value="Mocked Patch")
def test_generate_patch_success(mock_generate, mock_store, mock_assign, ai_model_manager):
    """
    Test successful patch generation using AI model selection and confidence scoring.
    """
    patch = ai_model_manager.generate_patch("SyntaxError", "def foo():", "test_foo.py")
    assert patch == "Mocked Patch"
    mock_generate.assert_called()
    mock_assign.assert_called()
    mock_store.assert_called()


@patch.object(AIModelManager, "_generate_with_model", return_value=None)
def test_generate_patch_failure(mock_generate, ai_model_manager, caplog):
    """
    Test the behavior when no AI model generates a valid patch.
    """
    with caplog.at_level(logging.ERROR):
        patch = ai_model_manager.generate_patch("RuntimeError", "x = 5 / 0", "test_div.py")
    assert patch is None
    assert "❌ All AI models failed to generate a useful patch." in caplog.text


# =======================
# Debugging Prompt & Error Signature Tests
# =======================
def test_format_prompt(ai_model_manager):
    """
    Test that the debugging prompt is formatted correctly with error message,
    file name, and code context.
    """
    prompt = ai_model_manager._format_prompt("IndexError", "list[5]", "test_list.py")
    assert "Error Message: IndexError" in prompt
    assert "Test File: test_list.py" in prompt
    assert "Code Context:\nlist[5]" in prompt


def test_compute_error_signature(ai_model_manager):
    """
    Test that the error signature (SHA-256 hash) is computed deterministically and uniquely.
    """
    sig1 = ai_model_manager._compute_error_signature("IndexError", "list[5]")
    sig2 = ai_model_manager._compute_error_signature("IndexError", "list[5]")
    sig3 = ai_model_manager._compute_error_signature("KeyError", "dict['missing']")
    assert sig1 == sig2  # Same error yields same hash
    assert sig1 != sig3  # Different errors yield different hashes
