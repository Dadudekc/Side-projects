import json
import os
from datetime import datetime
from unittest.mock import patch
import pytest

from ai_engine.models.debugger.patch_tracking_manager import (
    PatchTrackingManager,
    FAILED_PATCHES_FILE,
    SUCCESSFUL_PATCHES_FILE,
    IMPORT_FIXES_FILE,
    AI_FEEDBACK_FILE,
    AI_PERFORMANCE_FILE,
)

# Test Data
ERROR_SIGNATURE = "error123"
PATCH_1 = "--- old_code.py\n+++ new_code.py\n- old\n+ new"
PATCH_2 = "--- old_code.py\n+++ new_code.py\n- error\n+ fixed"
IMPORT_MODULE = "numpy"
AI_FEEDBACK = "AI improved patch by refining logic."
QUALITY_SCORE = 85


@pytest.fixture
def patch_manager():
    """Fixture to initialize PatchTrackingManager and clear JSON files before tests."""
    manager = PatchTrackingManager()

    # Reset test files before each run
    for file in [
        FAILED_PATCHES_FILE,
        SUCCESSFUL_PATCHES_FILE,
        IMPORT_FIXES_FILE,
        AI_FEEDBACK_FILE,
        AI_PERFORMANCE_FILE,
    ]:
        if os.path.exists(file):
            os.remove(file)

    return manager


def test_record_failed_patch(patch_manager):
    """Ensures failed patches are recorded correctly."""
    patch_manager.record_failed_patch(ERROR_SIGNATURE, PATCH_1)

    failed_patches = patch_manager.get_failed_patches(ERROR_SIGNATURE)
    assert failed_patches == [PATCH_1]

    # Verify it persists in the file
    with open(FAILED_PATCHES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data[ERROR_SIGNATURE] == [PATCH_1]

    print("✅ Test passed: Failed patch recorded correctly.")


def test_record_successful_patch(patch_manager):
    """Ensures successful patches are logged correctly."""
    patch_manager.record_successful_patch(ERROR_SIGNATURE, PATCH_2)

    successful_patches = patch_manager.get_successful_patches(ERROR_SIGNATURE)
    assert successful_patches == [PATCH_2]

    with open(SUCCESSFUL_PATCHES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data[ERROR_SIGNATURE] == [PATCH_2]

    print("✅ Test passed: Successful patch recorded correctly.")


def test_record_import_fix(patch_manager):
    """Ensures import fixes are tracked separately."""
    patch_manager.record_import_fix(IMPORT_MODULE, True)
    patch_manager.record_import_fix(IMPORT_MODULE, False)

    with open(IMPORT_FIXES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data[IMPORT_MODULE]["fixed"] == 1
    assert data[IMPORT_MODULE]["failed"] == 1

    print("✅ Test passed: Import fix tracking works correctly.")


def test_record_ai_feedback(patch_manager):
    """Ensures AI feedback and quality scores are stored properly."""
    patch_manager.record_ai_feedback(ERROR_SIGNATURE, AI_FEEDBACK, QUALITY_SCORE)

    with open(AI_FEEDBACK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data[ERROR_SIGNATURE]["feedback"] == AI_FEEDBACK
    assert data[ERROR_SIGNATURE]["quality_score"] == QUALITY_SCORE

    print("✅ Test passed: AI feedback stored correctly.")


@patch("ai_engine.models.debugger.patch_tracking_manager.datetime")
def test_track_ai_performance(mock_datetime, patch_manager):
    """Ensures AI debugging performance analytics are tracked correctly."""
    mock_datetime.now.return_value.strftime.return_value = "2025-02-14"

    patch_manager.record_import_fix("pandas", True)
    patch_manager.record_import_fix("pandas", False)
    patch_manager.record_import_fix("requests", True)

    patch_manager.track_ai_performance()

    with open(AI_PERFORMANCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    today_stats = data["2025-02-14"]
    assert today_stats["total_fixes"] == 3
    assert today_stats["success_rate"] == 66.67  # (2 successes / 3 total) * 100

    print("✅ Test passed: AI performance tracking updates correctly.")


def test_undo_last_fix(patch_manager):
    """Ensures last applied fix can be rolled back."""
    patch_manager.record_successful_patch(ERROR_SIGNATURE, PATCH_1)
    patch_manager.record_successful_patch(ERROR_SIGNATURE, PATCH_2)

    last_patch = patch_manager.undo_last_fix(ERROR_SIGNATURE)

    assert last_patch == PATCH_2
    remaining_patches = patch_manager.get_successful_patches(ERROR_SIGNATURE)
    assert remaining_patches == [PATCH_1]

    print("✅ Test passed: Undo last fix works correctly.")
