"""
tests/test_ai_rollback_analysis.py

Pytest-based tests for AIRollbackAnalysis.
"""
import json
import os
import pytest
from unittest.mock import patch, MagicMock

from agents.core.utilities.ai_rollback_analysis import (
    AIRollbackAnalysis,
    FAILED_PATCHES_FILE,
    REFINED_PATCHES_FILE,
    HUMAN_REVIEW_FILE,
    AI_DECISIONS_LOG,
    PATCH_HISTORY_FILE,
)


@pytest.fixture
def cleanup_files():
    """Removes test-related JSON files after each test."""
    yield
    for file_path in [
        FAILED_PATCHES_FILE,
        REFINED_PATCHES_FILE,
        HUMAN_REVIEW_FILE,
        AI_DECISIONS_LOG,
        PATCH_HISTORY_FILE,
    ]:
        if os.path.exists(file_path):
            os.remove(file_path)


def test_track_patch_history(cleanup_files):
    """Test that track_patch_history stores patch data correctly."""
    # Instantiate normally (no mocking needed here).
    rollback_analysis = AIRollbackAnalysis()

    rollback_analysis.track_patch_history("error123", "sample patch", "Failed")
    # Confirm data written to patch_history file
    with open(PATCH_HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "error123" in data
    assert len(data["error123"]) == 1
    assert data["error123"][0]["patch"] == "sample patch"
    assert data["error123"][0]["status"] == "Failed"


@patch.object(AIRollbackAnalysis, "_save_patch_data")  # Prevent file writes
@patch("agents.core.utilities.ai_rollback_analysis.PatchTrackingManager")
@patch("agents.core.utilities.ai_rollback_analysis.AIClient")
def test_analyze_failed_patches(mock_ai_client, mock_patch_manager, mock_save, cleanup_files):
    """
    Test that analyze_failed_patches classifies patches correctly
    based on AIClient evaluations.
    """
    # Set up mocks before instantiating AIRollbackAnalysis
    mock_manager_instance = mock_patch_manager.return_value
    mock_manager_instance.get_failed_patches.return_value = ["patch1", "patch2", "patch3"]

    mock_ai_instance = mock_ai_client.return_value
    mock_ai_instance.evaluate_patch_with_reason.side_effect = [
        {"score": 80, "reason": "Looks refinable."},  # refinable
        {"score": 30, "reason": "Totally off."},      # bad
        {"score": 60, "reason": "Uncertain fix."},    # uncertain
    ]

    # Now create the instance so it uses the mocked classes
    ra = AIRollbackAnalysis()

    refinable, bad, uncertain = ra.analyze_failed_patches("errorXYZ")
    assert refinable == ["patch1"]
    assert bad == ["patch2"]
    assert uncertain == ["patch3"]


@patch.object(AIRollbackAnalysis, "_save_patch_data")
@patch("agents.core.utilities.ai_rollback_analysis.PatchTrackingManager")
@patch("agents.core.utilities.ai_rollback_analysis.AIClient")
def test_refine_patches_success(mock_ai_client, mock_patch_manager, mock_save, cleanup_files):
    """
    Test that refine_patches successfully refines patches with a high score
    and moves uncertain patches to human review.
    """
    mock_patch_manager.return_value.get_failed_patches.return_value = ["patch1", "patch2"]

    mock_ai = mock_ai_client.return_value
    # patch1 is refinable, patch2 is uncertain
    mock_ai.evaluate_patch_with_reason.side_effect = [
        {"score": 80, "reason": "Good."},
        {"score": 60, "reason": "Uncertain."},
    ]
    mock_ai.refine_patch.side_effect = ["patch1-refined", ""]

    ra = AIRollbackAnalysis()
    result = ra.refine_patches("errorXYZ")
    assert result is True

    # patch1 => refined_patches
    assert "errorXYZ" in ra.refined_patches
    assert ra.refined_patches["errorXYZ"] == ["patch1-refined"]

    # patch2 => human_review
    assert "errorXYZ" in ra.human_review
    assert ra.human_review["errorXYZ"] == ["patch2"]


@patch.object(AIRollbackAnalysis, "_save_patch_data")
@patch("agents.core.utilities.ai_rollback_analysis.PatchTrackingManager")
@patch("agents.core.utilities.ai_rollback_analysis.AIClient")
def test_refine_patches_none(mock_ai_client, mock_patch_manager, mock_save, cleanup_files):
    """Test that refine_patches returns False if no patches are refinable."""
    mock_patch_manager.return_value.get_failed_patches.return_value = ["patchA"]
    mock_ai = mock_ai_client.return_value
    # Score is too low, so it's "bad"
    mock_ai.evaluate_patch_with_reason.return_value = {
        "score": 30,
        "reason": "Bad patch."
    }

    ra = AIRollbackAnalysis()
    result = ra.refine_patches("errorXYZ")
    assert result is False
    # No refined patches
    assert "errorXYZ" not in ra.refined_patches


@patch.object(AIRollbackAnalysis, "refine_patches", return_value=True)
def test_process_failed_patches_success(mock_refine, cleanup_files):
    """Test process_failed_patches returns True if refinement was done."""
    ra = AIRollbackAnalysis()
    out = ra.process_failed_patches("error123")
    assert out is True


@patch.object(AIRollbackAnalysis, "refine_patches", return_value=False)
def test_process_failed_patches_failure(mock_refine, cleanup_files):
    """Test process_failed_patches returns False if no refinements occurred."""
    ra = AIRollbackAnalysis()
    out = ra.process_failed_patches("error456")
    assert out is False
