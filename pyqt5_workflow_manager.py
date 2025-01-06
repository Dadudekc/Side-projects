import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QTextEdit,
    QLineEdit, QFormLayout, QDialog, QComboBox, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QWidget, QSplitter, QInputDialog, QToolBar
)
from PyQt5.QtCore import Qt

class JSONTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels(["Key", "Value"])
        self.setColumnWidth(0, 250)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

    def load_json(self, data):
        self.clear()
        self.add_items(self.invisibleRootItem(), data)

    def add_items(self, parent, value):
        if isinstance(value, dict):
            for key, val in value.items():
                item = QTreeWidgetItem(parent, [str(key)])
                if isinstance(val, (dict, list)):
                    self.add_items(item, val)
                else:
                    item.setText(1, str(val))
        elif isinstance(value, list):
            for index, val in enumerate(value):
                item = QTreeWidgetItem(parent, [f"[{index}]"])
                if isinstance(val, (dict, list)):
                    self.add_items(item, val)
                else:
                    item.setText(1, str(val))
        else:
            parent.setText(1, str(value))

    def get_json(self):
        root = self.invisibleRootItem()
        return self.build_json(root)

    def build_json(self, parent):
        result = {}
        for i in range(parent.childCount()):
            child = parent.child(i)
            key = child.text(0)
            if key.startswith('[') and key.endswith(']'):
                # It's a list
                index = int(key.strip('[]'))
                if not isinstance(result, list):
                    result = []
                value = self.get_value(child)
                # Ensure the list is large enough
                while len(result) <= index:
                    result.append(None)
                result[index] = value
            else:
                result[key] = self.get_value(child)
        return result

    def get_value(self, item):
        if item.childCount() > 0:
            # Determine if it's a list or dict
            first_child_key = item.child(0).text(0)
            if first_child_key.startswith('[') and first_child_key.endswith(']'):
                # It's a list
                return self.build_json(item)
            else:
                # It's a dict
                return self.build_json(item)
        else:
            return item.text(1)

    def open_context_menu(self, position):
        item = self.itemAt(position)
        if item:
            menu = QMessageBox()
            edit_action = QAction("Edit", self)
            delete_action = QAction("Delete", self)
            add_child_action = QAction("Add Child", self)
            menu = self.createStandardContextMenu()
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            menu.addAction(add_child_action)
            action = menu.exec_(self.viewport().mapToGlobal(position))
            if action == edit_action:
                self.edit_item(item)
            elif action == delete_action:
                self.delete_item(item)
            elif action == add_child_action:
                self.add_child(item)

    def edit_item(self, item):
        key, ok = QInputDialog.getText(self, "Edit Key", "Key:", text=item.text(0))
        if ok:
            item.setText(0, key)
        value, ok = QInputDialog.getText(self, "Edit Value", "Value:", text=item.text(1))
        if ok:
            item.setText(1, value)

    def delete_item(self, item):
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)

    def add_child(self, parent_item):
        key, ok = QInputDialog.getText(self, "Add Child", "Key:")
        if not ok or not key:
            return
        value, ok = QInputDialog.getText(self, "Add Child", "Value:")
        if not ok:
            return
        child = QTreeWidgetItem(parent_item, [key, value])
        parent_item.setExpanded(True)

class WorkflowManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic PyQt5 Workflow Manager")
        self.resize(1200, 800)
        self.projects = []
        self.current_project = None
        self.current_file = None

        self.init_ui()

    def init_ui(self):
        # Create Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        load_action = QAction("Load JSON", self)
        load_action.triggered.connect(self.load_json_files)
        toolbar.addAction(load_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_json)
        toolbar.addAction(save_action)

        export_action = QAction("Export Summary", self)
        export_action.triggered.connect(self.export_summary)
        toolbar.addAction(export_action)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()

        # Project List
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.display_project)
        main_layout.addWidget(self.project_list, 2)

        # JSON Viewer
        self.json_viewer = JSONTreeWidget()
        main_layout.addWidget(self.json_viewer, 5)

        # Buttons
        button_layout = QVBoxLayout()
        add_project_btn = QPushButton("Add Project")
        add_project_btn.clicked.connect(self.add_project)
        edit_project_btn = QPushButton("Edit Project")
        edit_project_btn.clicked.connect(self.edit_project)
        delete_project_btn = QPushButton("Delete Project")
        delete_project_btn.clicked.connect(self.delete_project)
        button_layout.addWidget(add_project_btn)
        button_layout.addWidget(edit_project_btn)
        button_layout.addWidget(delete_project_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout, 1)

        central_widget.setLayout(main_layout)

    def load_json_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Load JSON Files", "", "JSON Files (*.json)", options=options)
        if files:
            for file in files:
                self.load_project(file)
            self.refresh_project_list()

    def load_project(self, filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                project_name = data.get("name") or data.get("project") or os.path.basename(filepath)
                self.projects.append({"name": project_name, "data": data, "filepath": filepath})
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load {filepath}: {e}")

    def refresh_project_list(self):
        self.project_list.clear()
        for project in self.projects:
            self.project_list.addItem(project["name"])

    def display_project(self, item):
        index = self.project_list.row(item)
        project = self.projects[index]
        self.current_project = project["data"]
        self.current_file = project["filepath"]
        self.json_viewer.load_json(self.current_project)

    def add_project(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getSaveFileName(self, "Save New JSON Project", "", "JSON Files (*.json)", options=options)
        if file:
            empty_project = {}
            try:
                with open(file, 'w') as f:
                    json.dump(empty_project, f, indent=4)
                self.projects.append({"name": "Unnamed Project", "data": empty_project, "filepath": file})
                self.refresh_project_list()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to create {file}: {e}")

    def edit_project(self):
        if not self.current_project:
            QMessageBox.warning(self, "No Selection", "Please select a project to edit.")
            return
        # Editing is done directly in the JSONTreeWidget
        QMessageBox.information(self, "Edit Project", "Edit the project directly in the JSON Viewer. Click 'Save' to apply changes.")

    def delete_project(self):
        if not self.current_project:
            QMessageBox.warning(self, "No Selection", "Please select a project to delete.")
            return
        reply = QMessageBox.question(self, 'Delete Project',
                                     f"Are you sure you want to delete the project '{self.current_project.get('name', 'Unnamed Project')}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            index = self.project_list.currentRow()
            del self.projects[index]
            self.current_project = None
            self.current_file = None
            self.json_viewer.clear()
            self.refresh_project_list()

    def save_json(self):
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please select a project to save.")
            return
        updated_data = self.json_viewer.get_json()
        self.current_project.clear()
        self.current_project.update(updated_data)
        try:
            with open(self.current_file, 'w') as f:
                json.dump(self.current_project, f, indent=4)
            QMessageBox.information(self, "Success", f"Project '{self.current_project.get('name', 'Unnamed Project')}' saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save {self.current_file}: {e}")

    def export_summary(self):
        if not self.current_project:
            QMessageBox.warning(self, "No Project", "Please select a project to export.")
            return
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Export Summary", "", "JSON Files (*.json);;CSV Files (*.csv)", options=options)
        if filename:
            try:
                summary = self.generate_summary(self.current_project)
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(summary, f, indent=4)
                elif filename.endswith('.csv'):
                    with open(filename, 'w') as f:
                        for key, value in summary.items():
                            if isinstance(value, list):
                                value = "; ".join(map(str, value))
                            elif isinstance(value, dict):
                                value = json.dumps(value)
                            f.write(f"{key},{value}\n")
                QMessageBox.information(self, "Success", f"Summary exported to {filename}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export summary: {e}")

    def generate_summary(self, data):
        # Customize the summary generation as needed.
        # For simplicity, we'll return the top-level keys and their types.
        summary = {}
        for key, value in data.items():
            if isinstance(value, dict):
                summary[key] = "Object"
            elif isinstance(value, list):
                summary[key] = f"List of {len(value)} items"
            else:
                summary[key] = type(value).__name__
        return summary

def main():
    app = QApplication(sys.argv)
    window = WorkflowManagerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
