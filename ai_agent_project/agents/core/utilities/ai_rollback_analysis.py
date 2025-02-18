"""
agents/core/utilities/ai_rollback_analysis.py

AI-powered rollback analysis that:
1. Tracks patch history per error signature.
2. Uses AI to determine if a patch is fundamentally incorrect or refinable.
3. Sends human-reviewed patches back to AI to improve learning.
4. Provides an interactive PyQt5 dashboard for patch analysis.
"""

import json
import logging
import os
from typing import Dict, List, Tuple

import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox
)

from agents.core.utilities.ai_client import AIClient
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

logger = logging.getLogger("AIRollbackAnalysis")
logger.setLevel(logging.DEBUG)

FAILED_PATCHES_FILE = "failed_patches.json"
REFINED_PATCHES_FILE = "refined_patches.json"
HUMAN_REVIEW_FILE = "human_review.json"
AI_DECISIONS_LOG = "ai_decisions.json"
PATCH_HISTORY_FILE = "patch_history.json"
BAD_PATCH_THRESHOLD = 3  # Number of failures before marking a patch as "bad"


class AIRollbackAnalysis:
    """
    AI-powered rollback analysis that:
      1) Tracks patch history per error signature.
      2) Uses AI to determine if a patch is fundamentally incorrect or refinable.
      3) Sends human-reviewed patches back to AI to improve learning.
      4) Provides an interactive PyQt5 dashboard for patch analysis (optional).
    """

    def __init__(self):
        # External dependencies:
        self.patch_tracker = PatchTrackingManager()
        self.ai_client = AIClient()

        # Load local JSON data for patch tracking, refined patches, etc.
        self.failed_patches = self._load_patch_data(FAILED_PATCHES_FILE)
        self.refined_patches = self._load_patch_data(REFINED_PATCHES_FILE)
        self.human_review = self._load_patch_data(HUMAN_REVIEW_FILE)
        self.ai_decisions = self._load_patch_data(AI_DECISIONS_LOG)
        self.patch_history = self._load_patch_data(PATCH_HISTORY_FILE)

    def _load_patch_data(self, file_path: str) -> Dict[str, List[Dict[str, str]]]:
        """Loads patch tracking data from a JSON file, or returns an empty dict on error."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load {file_path}: {e}")
        return {}

    def _save_patch_data(self, file_path: str, data: Dict[str, List[Dict[str, str]]]):
        """Saves patch tracking data to a JSON file, logging errors if they occur."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Failed to save {file_path}: {e}")

    def track_patch_history(self, error_signature: str, patch: str, status: str):
        """
        Logs each patch attempt with its result (e.g., "Failed", "Refined", etc.).

        :param error_signature: A unique key identifying the error/failure scenario.
        :param patch: The patch content or diff.
        :param status: The status of the patch (e.g., "Failed", "Refined").
        """
        self.patch_history.setdefault(error_signature, []).append({
            "patch": patch,
            "status": status
        })
        self._save_patch_data(PATCH_HISTORY_FILE, self.patch_history)

    def analyze_failed_patches(self, error_signature: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Uses AI to classify patches into three categories:
          - refinable (score > 75)
          - bad (score < 50)
          - uncertain (everything else)

        Returns a tuple: (refinable_patches, bad_patches, uncertain_patches).
        """
        failed_patches = self.patch_tracker.get_failed_patches(error_signature)
        if not failed_patches:
            logger.info(f"🔍 No failed patches found for {error_signature}.")
            return [], [], []

        refinable_patches, bad_patches, uncertain_patches = [], [], []

        for patch in failed_patches:
            analysis = self.ai_client.evaluate_patch_with_reason(patch)
            patch_score = analysis["score"]
            decision_reason = analysis["reason"]

            # Record AI decisions
            self.ai_decisions.setdefault(error_signature, []).append({
                "patch": patch,
                "score": patch_score,
                "reason": decision_reason
            })
            self._save_patch_data(AI_DECISIONS_LOG, self.ai_decisions)

            if patch_score > 75:
                refinable_patches.append(patch)
            elif patch_score < 50:
                bad_patches.append(patch)
            else:
                uncertain_patches.append(patch)

        return refinable_patches, bad_patches, uncertain_patches

    def refine_patches(self, error_signature: str) -> bool:
        """
        Attempts to refine near-correct patches. Returns True if at least one patch is refined;
        otherwise returns False.
        """
        refinable_patches, bad_patches, uncertain_patches = self.analyze_failed_patches(error_signature)

        # Uncertain patches go to human review
        if uncertain_patches:
            self.human_review.setdefault(error_signature, []).extend(uncertain_patches)
            self._save_patch_data(HUMAN_REVIEW_FILE, self.human_review)

        if not refinable_patches:
            return False

        successful_refinement = False
        for patch in refinable_patches:
            refined_patch = self.ai_client.refine_patch(patch)
            if refined_patch:
                self.refined_patches.setdefault(error_signature, []).append(refined_patch)
                self._save_patch_data(REFINED_PATCHES_FILE, self.refined_patches)
                successful_refinement = True

        return successful_refinement

    def process_failed_patches(self, error_signature: str) -> bool:
        """
        Main function to analyze, refine, and reattempt failed patches.
        Returns True if refinement succeeded, False otherwise.
        """
        return self.refine_patches(error_signature)


### 🖥️ PyQt5 Dashboard for Patch Analysis
class PatchAnalysisDashboard(QMainWindow):
    def __init__(self, rollback_analysis: AIRollbackAnalysis):
        super().__init__()
        self.rollback_analysis = rollback_analysis
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Patch Analysis Dashboard")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(["All", "Failed Patches", "Refined Patches", "Human Review"])
        self.filter_dropdown.currentTextChanged.connect(self.update_table)
        layout.addWidget(self.filter_dropdown)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Error Signature", "Patch", "Status"])
        layout.addWidget(self.table_widget)

        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.update_table)
        layout.addWidget(self.refresh_button)

        self.central_widget.setLayout(layout)
        self.update_table()

    def update_table(self):
        filter_option = self.filter_dropdown.currentText()
        data = []

        if filter_option == "All":
            for error_sig, patches in self.rollback_analysis.patch_history.items():
                for entry in patches:
                    data.append((error_sig, entry["patch"], entry["status"]))

        elif filter_option == "Failed Patches":
            for error_sig, patch_list in self.rollback_analysis.failed_patches.items():
                for patch in patch_list:
                    data.append((error_sig, patch, "Failed"))

        elif filter_option == "Refined Patches":
            for error_sig, patch_list in self.rollback_analysis.refined_patches.items():
                for patch in patch_list:
                    data.append((error_sig, patch, "Refined"))

        elif filter_option == "Human Review":
            for error_sig, patch_list in self.rollback_analysis.human_review.items():
                for patch in patch_list:
                    data.append((error_sig, patch, "Needs Review"))

        self.table_widget.setRowCount(len(data))
        for row_idx, (error_sig, patch, status) in enumerate(data):
            self.table_widget.setItem(row_idx, 0, QTableWidgetItem(error_sig))
            self.table_widget.setItem(row_idx, 1, QTableWidgetItem(patch))
            self.table_widget.setItem(row_idx, 2, QTableWidgetItem(status))


if __name__ == "__main__":
    rollback_analysis = AIRollbackAnalysis()
    app = QApplication([])
    dashboard = PatchAnalysisDashboard(rollback_analysis)
    dashboard.show()
    app.exec_()
