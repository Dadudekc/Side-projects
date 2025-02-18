"""

This module defines a Graphical User Interface (GUI) for an AI Debugging System. The GUI built with PyQt5 features a 
debugger dashboard that reports on debugging metrics. It provides patch success rate, import error tracking, debugging 
report visualization, and also supports the Undo function for fixes.

Classes:
    DebuggerDashboard: Class representing the main GUI for the AI Debugging System. The interface provides a real-time
    summary of debugging activities as well as the ability to address import issues
"""

import sys
import json
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QMessageBox, QComboBox
)
from PyQt5.QtCore import QTimer

# File paths
SUCCESS_PATCHES_FILE = "successful_patches.json"
FAILED_PATCHES_FILE = "failed_patches.json"
IMPORT_ERROR_LOG = "import_errors.json"
AI_LEARNING_DB = "learning_db.json"
PROJECT_STRUCTURE_FILE = "project_structure.json"
UNDO_FIXES_FILE = "undo_fixes.json"
SOURCE_FILES_DIR = "./"  # Root directory for source files

class DebuggerDashboard(QMainWindow):
    """PyQt5 GUI for AI Debugging System with Git Auto-Commit, Fix Reports, and Undo Feature"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Debugger Dashboard")
        self.setGeometry(100, 100, 1100, 750)

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Title
        self.title_label = QLabel("📊 AI Debugger Dashboard")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Import Error Tracking
        self.import_errors_label = QLabel("⚠️ Import Errors (Click to Fix or Undo)")
        self.layout.addWidget(self.import_errors_label)
        self.import_errors_table = QTableWidget()
        self.import_errors_table.setColumnCount(4)
        self.import_errors_table.setHorizontalHeaderLabels(["Module", "Suggested Fixes", "Attempts", "Action"])
        self.import_errors_table.cellClicked.connect(self.handle_import_fix)
        self.layout.addWidget(self.import_errors_table)

        # Undo Fixes Section
        self.undo_fix_label = QLabel("⏪ Undo Previous Fixes")
        self.layout.addWidget(self.undo_fix_label)
        self.undo_fix_selector = QComboBox()
        self.layout.addWidget(self.undo_fix_selector)
        self.undo_fix_button = QPushButton("🔄 Undo Selected Fix")
        self.undo_fix_button.clicked.connect(self.undo_selected_fix)
        self.layout.addWidget(self.undo_fix_button)

        # Patch Success Rate
        self.success_rate_label = QLabel("✅ Patch Success Rate")
        self.layout.addWidget(self.success_rate_label)
        self.success_rate_bar = QProgressBar()
        self.layout.addWidget(self.success_rate_bar)

        # Debugging Report Viewer
        self.report_label = QLabel("📋 Debugging Report Summary")
        self.layout.addWidget(self.report_label)
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.layout.addWidget(self.report_text)

        # Refresh Button
        self.refresh_button = QPushButton("🔄 Refresh Data")
        self.refresh_button.clicked.connect(self.update_dashboard)
        self.layout.addWidget(self.refresh_button)

        # Auto-refresh every 10 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(10000)  # Refresh every 10 seconds

        self.update_dashboard()

    def load_json(self, file_path):
        """Helper to safely load JSON files."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")
        return {}

    def save_json(self, file_path, data):
        """Helper to safely save JSON files."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"❌ Error saving {file_path}: {e}")

    def update_dashboard(self):
        """Fetches latest data and updates the UI."""
        import_errors = self.load_json(IMPORT_ERROR_LOG)
        undo_fixes = self.load_json(UNDO_FIXES_FILE)

        self.import_errors_table.setRowCount(len(import_errors))
        self.undo_fix_selector.clear()

        for row, (module, info) in enumerate(import_errors.items()):
            suggested_fixes = info.get("suggested_fixes", [])
            self.import_errors_table.setItem(row, 0, QTableWidgetItem(module))
            self.import_errors_table.setItem(row, 1, QTableWidgetItem(", ".join(suggested_fixes)))
            self.import_errors_table.setItem(row, 2, QTableWidgetItem(str(info.get("attempts", 0))))
            self.import_errors_table.setItem(row, 3, QTableWidgetItem("⚡ Auto-Fix"))

        for file in undo_fixes.keys():
            self.undo_fix_selector.addItem(file)

        success_patches = self.load_json(SUCCESS_PATCHES_FILE)
        failed_patches = self.load_json(FAILED_PATCHES_FILE)
        total_patches = len(success_patches) + len(failed_patches)
        success_rate = (len(success_patches) / total_patches * 100) if total_patches > 0 else 0
        self.success_rate_bar.setValue(int(success_rate))

        self.report_text.setText(json.dumps(self.load_json(AI_LEARNING_DB), indent=4))

    def handle_import_fix(self, row, column):
        """Automatically fixes import errors when clicking the table."""
        if column != 3:
            return

        module = self.import_errors_table.item(row, 0).text()
        suggested_fixes = self.import_errors_table.item(row, 1).text().split(", ")

        response = QMessageBox.question(
            self, "Fix Import Issue",
            f"Would you like to apply this fix?\n\n{suggested_fixes[0]}",
            QMessageBox.Yes | QMessageBox.No
        )

        if response == QMessageBox.Yes:
            self.apply_import_fix(module, suggested_fixes[0])

    def apply_import_fix(self, module, suggested_fix):
        """Applies an import fix directly to source files and commits to Git."""
        import_errors = self.load_json(IMPORT_ERROR_LOG)

        if module in import_errors:
            file_path = import_errors[module].get("source_file")
            if file_path and os.path.exists(file_path):
                self.modify_source_file(file_path, module, suggested_fix)
                import_errors[module]["fixed"] = import_errors[module].get("fixed", 0) + 1

                # Auto-commit the change
                self.commit_to_git(file_path, f"Fixed import: {module}")

        self.save_json(IMPORT_ERROR_LOG, import_errors)
        self.update_dashboard()

    def modify_source_file(self, file_path, module, suggested_fix):
        """Modifies the actual Python file to apply the import fix."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            original_content = "".join(lines)

            for i, line in enumerate(lines):
                if f"import {module}" in line or f"from {module}" in line:
                    lines[i] = f"{suggested_fix}\n"
                    break
            else:
                lines.insert(0, f"{suggested_fix}\n")

            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            # Save original content for undo
            undo_fixes = self.load_json(UNDO_FIXES_FILE)
            undo_fixes[file_path] = original_content
            self.save_json(UNDO_FIXES_FILE, undo_fixes)

            QMessageBox.information(self, "Import Fix Applied", f"Fixed: {module} in {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to modify {file_path}: {e}")

    def commit_to_git(self, file_path, message):
        """Commits the applied fix to Git."""
        try:
            subprocess.run(["git", "add", file_path], check=True)
            subprocess.run(["git", "commit", "-m", message], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Git commit failed: {e}")

    def undo_selected_fix(self):
        """Restores the original version of a file before the fix."""
        undo_fixes = self.load_json(UNDO_FIXES_FILE)
        file_path = self.undo_fix_selector.currentText()

        if file_path in undo_fixes:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(undo_fixes[file_path])

            del undo_fixes[file_path]
            self.save_json(UNDO_FIXES_FILE, undo_fixes)
            self.update_dashboard()
