# modules/gui.py

import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QLabel, QApplication
)
from modules import analyzer_core, db_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Project Analyzer")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        # Initialize the SQLite database connection
        self.conn = db_manager.get_connection()
        db_manager.initialize_db(self.conn)
    
    def initUI(self):
        # Set up the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Directory selection layout
        dir_layout = QHBoxLayout()
        self.dir_line_edit = QLineEdit()
        self.dir_line_edit.setPlaceholderText("Select a directory to analyze...")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.dir_line_edit)
        dir_layout.addWidget(browse_button)
        main_layout.addLayout(dir_layout)
        
        # Analyze button
        analyze_button = QPushButton("Analyze Project")
        analyze_button.clicked.connect(self.start_analysis)
        main_layout.addWidget(analyze_button)
        
        # Status label for messages
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)
        
        # Table widget to display analysis results
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["File", "Path", "Analyzed At", "Description"])
        main_layout.addWidget(self.table)
    
    def browse_directory(self):
        """
        Opens a dialog to select a directory and sets the chosen path in the text field.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_line_edit.setText(directory)
    
    def start_analysis(self):
        """
        Starts the analysis by scanning the selected directory, populates the table,
        and saves the results into the SQLite database.
        """
        directory = self.dir_line_edit.text().strip()
        if not directory or not os.path.isdir(directory):
            QMessageBox.warning(self, "Error", "Please select a valid directory.")
            return
        
        self.status_label.setText("Analyzing...")
        QApplication.processEvents()  # Update the GUI immediately
        
        # Perform the analysis using the core module
        summary = analyzer_core.scan_project(directory)
        
        # Populate the table with analysis results
        self.populate_table(summary)
        
        # Save results to the SQLite database
        db_manager.insert_project_summary(self.conn, summary)
        
        self.status_label.setText("Analysis complete. Results saved to SQLite database.")
    
    def populate_table(self, summary):
        """
        Populates the QTableWidget with analysis results.
        """
        files = summary.get("files", [])
        self.table.setRowCount(len(files))
        
        for row, file_detail in enumerate(files):
            file_item = QTableWidgetItem(file_detail.get("file", ""))
            path_item = QTableWidgetItem(file_detail.get("path", ""))
            analyzed_item = QTableWidgetItem(file_detail.get("analyzed_at", ""))
            desc_item = QTableWidgetItem(file_detail.get("description", ""))
            
            self.table.setItem(row, 0, file_item)
            self.table.setItem(row, 1, path_item)
            self.table.setItem(row, 2, analyzed_item)
            self.table.setItem(row, 3, desc_item)

# For standalone testing, you can run this module directly.
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
