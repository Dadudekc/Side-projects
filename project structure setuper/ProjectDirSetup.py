import sys
import os
import json
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QFileDialog, QListWidget, QMessageBox, QAction, QMenuBar

def create_project_structure(base_path, structure):
    try:
        for dir_path in structure:
            path = os.path.join(base_path, dir_path)
            os.makedirs(path, exist_ok=True)
        return True, "Directory structure created successfully!"
    except Exception as e:
        return False, "Failed to create directory structure: " + str(e)

class ProjectDirSetup(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Project Directory Setup")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu('File')
        
        save_action = QAction('Save Setup', self)
        save_action.triggered.connect(self.save_setup)
        load_action = QAction('Load Setup', self)
        load_action.triggered.connect(self.load_setup)
        
        file_menu.addAction(save_action)
        file_menu.addAction(load_action)
        layout.addWidget(self.menu_bar)

        self.base_path_label = QLabel('Base Path:', self)
        layout.addWidget(self.base_path_label)
        
        self.base_path_entry = QLineEdit(self)
        layout.addWidget(self.base_path_entry)
        
        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_base_path)
        layout.addWidget(self.browse_button)

        self.directories_list = QListWidget(self)
        layout.addWidget(self.directories_list)
        
        self.add_dir_button = QPushButton('Add Directory', self)
        self.add_dir_button.clicked.connect(self.add_directory)
        layout.addWidget(self.add_dir_button)

        self.create_button = QPushButton('Create Structure', self)
        self.create_button.clicked.connect(self.create_structure)
        layout.addWidget(self.create_button)
        
        self.setLayout(layout)

    def browse_base_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.base_path_entry.setText(path)

    def add_directory(self):
        dir_path, _ = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            relative_path = os.path.relpath(dir_path, self.base_path_entry.text())
            self.directories_list.addItem(relative_path)

    def create_structure(self):
        base_path = self.base_path_entry.text()
        directories = [self.directories_list.item(i).text() for i in range(self.directories_list.count())]
        success, message = create_project_structure(base_path, directories)
        self.show_message(message, success)

    def show_message(self, message, success):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Result")
        msg_box.setText(message)
        if success:
            msg_box.setIcon(QMessageBox.Information)
        else:
            msg_box.setIcon(QMessageBox.Critical)
        msg_box.exec_()

    def save_setup(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json)")
        if file_name:
            structure = [self.directories_list.item(i).text() for i in range(self.directories_list.count())]
            data = {'base_path': self.base_path_entry.text(), 'directories': structure}
            with open(file_name, 'w') as file:
                json.dump(data, file)

    def load_setup(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r') as file:
                data = json.load(file)
                self.base_path_entry.setText(data['base_path'])
                self.directories_list.clear()
                for dir_path in data['directories']:
                    self.directories_list.addItem(dir_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProjectDirSetup()
    ex.show()
    sys.exit(app.exec_())
