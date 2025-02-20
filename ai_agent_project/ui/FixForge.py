import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt

# ----- Imports for Project Setup & Patch Management -----
from ai_engine.models.debugger.advanced_init_setup import run_project_setup
from ai_engine.models.debugger.patch_manager import PatchManager
from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy

# Dummy DebuggingStrategy for Apply Fix Tab.
class DummyDebuggingStrategy(DebuggingStrategy):
    def generate_patch(self, error: str, file: str) -> str:
        return f"Patch for {error} in {file}"

    def apply_patch(self, patch: str) -> bool:
        # Simulate successful patch application.
        return True

# Global PatchManager using the dummy strategy.
patch_manager = PatchManager(debug_strategy=DummyDebuggingStrategy())

# ----- Imports for Debugging Orchestrator -----
from agents.core.utilities.debugging_orchestrator import DebuggingOrchestrator

# -------------------- Tab: Project Setup --------------------
class ProjectSetupTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # Project Root input.
        root_layout = QHBoxLayout()
        root_label = QLabel("Project Root (optional):")
        self.root_input = QLineEdit()
        root_layout.addWidget(root_label)
        root_layout.addWidget(self.root_input)
        layout.addLayout(root_layout)

        # Setup button.
        self.setup_button = QPushButton("Run Project Setup")
        self.setup_button.clicked.connect(self.run_setup)
        layout.addWidget(self.setup_button)

        # Help text.
        help_text = QLabel("Enter the project root directory (or leave blank to use current directory), then click 'Run Project Setup' to generate __init__.py files and analyze the project.")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        self.setLayout(layout)

    def run_setup(self):
        project_root = self.root_input.text().strip() or os.getcwd()
        try:
            run_project_setup(project_root)
            QMessageBox.information(self, "Success", f"Project setup complete for {project_root}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error during setup:\n{str(e)}")

# -------------------- Tab: Apply Fix --------------------
class ApplyFixTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # Error input.
        error_layout = QHBoxLayout()
        error_label = QLabel("Error:")
        self.error_input = QLineEdit()
        error_layout.addWidget(error_label)
        error_layout.addWidget(self.error_input)
        layout.addLayout(error_layout)

        # File input.
        file_layout = QHBoxLayout()
        file_label = QLabel("File:")
        self.file_input = QLineEdit()
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input)
        layout.addLayout(file_layout)

        # Apply fix button.
        self.apply_button = QPushButton("Apply Fix")
        self.apply_button.clicked.connect(self.apply_fix)
        layout.addWidget(self.apply_button)

        # Help text.
        help_text = QLabel("Enter the error message and the file name where the error occurred, then click 'Apply Fix' to generate and apply a patch.")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        self.setLayout(layout)

    def apply_fix(self):
        error = self.error_input.text().strip()
        file = self.file_input.text().strip()
        if not error or not file:
            QMessageBox.warning(self, "Warning", "Please enter both error and file values.")
            return

        failure = {"error": error, "file": file}
        success = patch_manager.apply_fix(failure)
        if success:
            QMessageBox.information(self, "Success", "Patch applied successfully!")
        else:
            QMessageBox.warning(self, "Failure", "Failed to apply patch.")

# -------------------- Tab: Debugging Orchestrator --------------------
class DebuggingOrchestratorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.orchestrator = DebuggingOrchestrator()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # Section for starting a debugging session.
        layout.addWidget(QLabel("Start Debugging Session"))
        session_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task description")
        self.error_input = QLineEdit()
        self.error_input.setPlaceholderText("Enter error log")
        session_layout.addWidget(self.task_input)
        session_layout.addWidget(self.error_input)
        layout.addLayout(session_layout)
        self.start_session_btn = QPushButton("Start Session")
        self.start_session_btn.clicked.connect(self.start_session)
        layout.addWidget(self.start_session_btn)

        # Section for documenting resolution steps.
        layout.addWidget(QLabel("Document Resolution Steps"))
        self.resolution_text = QTextEdit()
        self.resolution_text.setPlaceholderText("Enter resolution steps here...")
        layout.addWidget(self.resolution_text)
        self.resolve_btn = QPushButton("Document Resolution")
        self.resolve_btn.clicked.connect(self.document_resolution)
        layout.addWidget(self.resolve_btn)

        # Section for summarizing the session.
        layout.addWidget(QLabel("Summarize Session"))
        self.summary_task_input = QLineEdit()
        self.summary_task_input.setPlaceholderText("Enter task description to summarize")
        layout.addWidget(self.summary_task_input)
        self.summarize_btn = QPushButton("Summarize Session")
        self.summarize_btn.clicked.connect(self.summarize_session)
        layout.addWidget(self.summarize_btn)

        # Section for performing scheduled backup.
        self.backup_btn = QPushButton("Perform Scheduled Backup")
        self.backup_btn.clicked.connect(self.perform_backup)
        layout.addWidget(self.backup_btn)

        # Help text.
        help_text = QLabel("Use this tab to control a debugging session. "
                           "You can start a session by providing a task description and error log, "
                           "document the steps you took to resolve the issue, summarize the session, "
                           "or perform a backup of your debugging data.")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        self.setLayout(layout)

    def start_session(self):
        task_description = self.task_input.text().strip()
        error_log = self.error_input.text().strip()
        if not task_description or not error_log:
            QMessageBox.warning(self, "Warning", "Please enter both task description and error log.")
            return
        try:
            self.orchestrator.start_debugging_session(task_description, error_log)
            QMessageBox.information(self, "Success", "Debugging session started successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start session:\n{str(e)}")

    def document_resolution(self):
        resolution_steps = self.resolution_text.toPlainText().strip()
        if not resolution_steps:
            QMessageBox.warning(self, "Warning", "Please enter resolution steps.")
            return
        try:
            self.orchestrator.resolve_and_document(resolution_steps)
            QMessageBox.information(self, "Success", "Resolution steps documented successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to document resolution:\n{str(e)}")

    def summarize_session(self):
        task_description = self.summary_task_input.text().strip()
        if not task_description:
            QMessageBox.warning(self, "Warning", "Please enter a task description for summarization.")
            return
        try:
            self.orchestrator.summarize_session(task_description)
            QMessageBox.information(self, "Success", "Session summarized successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to summarize session:\n{str(e)}")

    def perform_backup(self):
        try:
            self.orchestrator.perform_scheduled_backup()
            QMessageBox.information(self, "Success", "Scheduled backup completed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Backup failed:\n{str(e)}")

# -------------------- Tab: Project Context --------------------
class ProjectContextTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.json_data = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Search/filter layout.
        filter_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search modules...")
        self.search_input.textChanged.connect(self.filter_tree)
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_input)
        layout.addLayout(filter_layout)
        
        # Button to load a JSON context file.
        self.load_button = QPushButton("Load Context JSON")
        self.load_button.clicked.connect(self.load_json)
        layout.addWidget(self.load_button)

        # A text edit to display the JSON in a tree view.
        from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Module", "Purpose", "Dependencies"])
        layout.addWidget(self.tree)

        # Help text.
        help_text = QLabel("Load the JSON file generated by your project analysis to view modules, dependencies, and purpose. Use the search bar to filter modules.")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        self.setLayout(layout)

    def load_json(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Context JSON", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.json_data = json.load(f)
                self.populate_tree()
                QMessageBox.information(self, "Success", "JSON context loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load JSON:\n{str(e)}")

    def populate_tree(self):
        self.tree.clear()
        modules = self.json_data.get("modules", {})
        tree_dict = {}
        for module_path, data in modules.items():
            parts = module_path.split("/")  # adjust if needed
            current = tree_dict
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = data

        def add_items(parent_item, dictionary):
            for key, value in dictionary.items():
                if isinstance(value, dict) and "dependencies" in value:
                    purpose = value.get("purpose", "No docstring found.")
                    deps = ", ".join(value.get("dependencies", []))
                    item = QTreeWidgetItem([key, purpose, deps])
                    parent_item.addChild(item)
                else:
                    item = QTreeWidgetItem([key])
                    parent_item.addChild(item)
                    add_items(item, value)

        for key, value in tree_dict.items():
            item = QTreeWidgetItem([key])
            self.tree.addTopLevelItem(item)
            add_items(item, value)
        self.tree.expandAll()

    def filter_tree(self):
        search_text = self.search_input.text().lower()
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            self.filter_item(root.child(i), search_text)

    def filter_item(self, item, search_text):
        match = search_text in item.text(0).lower() or search_text in item.text(1).lower()
        child_match = False
        for i in range(item.childCount()):
            child_visible = self.filter_item(item.child(i), search_text)
            child_match = child_match or child_visible
        visible = match or child_match or not search_text
        item.setHidden(not visible)
        return visible

# -------------------- Main Window --------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Agent MVP")
        self.init_ui()
    
    def init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(ProjectSetupTab(), "Project Setup")
        tabs.addTab(ApplyFixTab(), "Apply Fix")
        tabs.addTab(DebuggingOrchestratorTab(), "Debug Orchestrator")
        tabs.addTab(ProjectContextTab(), "Project Context")
        self.setCentralWidget(tabs)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
