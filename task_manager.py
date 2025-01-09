import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QDialog, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QTextEdit, QFileDialog, QLabel, QProgressBar, QHeaderView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QBrush


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phase 1 Task Manager")
        self.setGeometry(100, 100, 1200, 700)
        self.tasks = []
        self.init_ui()
        self.load_tasks()  # Load tasks from JSON on startup

    def init_ui(self):
        # Main widget and layout
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        # Search and Filter Layout
        self.filter_layout = QHBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search tasks...")
        self.filter_category = QComboBox(self)
        self.filter_category.addItem("All Categories")
        self.filter_priority = QComboBox(self)
        self.filter_priority.addItem("All Priorities")
        self.filter_status = QComboBox(self)
        self.filter_status.addItem("All Statuses")
        self.filter_button = QPushButton("Filter")

        self.filter_layout.addWidget(QLabel("Search:"))
        self.filter_layout.addWidget(self.search_bar)
        self.filter_layout.addWidget(QLabel("Category:"))
        self.filter_layout.addWidget(self.filter_category)
        self.filter_layout.addWidget(QLabel("Priority:"))
        self.filter_layout.addWidget(self.filter_priority)
        self.filter_layout.addWidget(QLabel("Status:"))
        self.filter_layout.addWidget(self.filter_status)
        self.filter_layout.addWidget(self.filter_button)

        self.layout.addLayout(self.filter_layout)

        # Table for tasks
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Task Name", "Category", "Priority", "Status", 
            "Progress (%)", "Dependencies", "Deliverables", 
            "Validation Steps", "Notes", "Progress Bar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # Buttons for task actions
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.edit_button = QPushButton("Edit Task")
        self.delete_button = QPushButton("Delete Task")
        self.save_button = QPushButton("Save Tasks")
        self.load_button = QPushButton("Load Tasks")
        self.export_button = QPushButton("Export to CSV")
        self.clear_button = QPushButton("Clear All Tasks")

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.export_button)
        self.button_layout.addWidget(self.clear_button)

        self.layout.addLayout(self.button_layout)
        self.setCentralWidget(self.main_widget)

        # Connect buttons to actions
        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.save_button.clicked.connect(self.save_tasks)
        self.load_button.clicked.connect(self.load_tasks)
        self.export_button.clicked.connect(self.export_tasks)
        self.clear_button.clicked.connect(self.clear_tasks)
        self.filter_button.clicked.connect(self.apply_filters)
        self.search_bar.textChanged.connect(self.apply_filters)

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec_():
            task = dialog.get_task_data()
            self.tasks.append(task)
            self.update_filters(task)
            self.insert_task_into_table(task)
            self.save_tasks_auto()

    def edit_task(self):
        row = self.table.currentRow()
        if row < 0:
            return
        task = self.tasks[row]
        dialog = TaskDialog(self, task)
        if dialog.exec_():
            updated_task = dialog.get_task_data()
            self.tasks[row] = updated_task
            self.update_filters(updated_task)
            self.update_table_row(row, updated_task)
            self.save_tasks_auto()

    def delete_task(self):
        row = self.table.currentRow()
        if row >= 0:
            del self.tasks[row]
            self.table.removeRow(row)
            self.save_tasks_auto()

    def clear_tasks(self):
        confirmation = YesNoDialog("Are you sure you want to delete all tasks?")
        if confirmation.exec_() == QDialog.Accepted:
            self.tasks.clear()
            self.table.setRowCount(0)
            self.filter_category.clear()
            self.filter_category.addItem("All Categories")
            self.filter_priority.clear()
            self.filter_priority.addItem("All Priorities")
            self.filter_status.clear()
            self.filter_status.addItem("All Statuses")
            self.save_tasks_auto()

    def save_tasks(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Tasks", "", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=4)

    def save_tasks_auto(self):
        with open("tasks.json", "w", encoding="utf-8") as file:
            json.dump(self.tasks, file, indent=4)

    def load_tasks(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Tasks", "", "JSON Files (*.json)")
        if path:
            with open(path, "r", encoding="utf-8") as file:
                self.tasks = json.load(file)
                self.refresh_table()
                self.populate_filters()
    
    def export_tasks(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Tasks to CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                headers = [self.table.horizontalHeaderItem(col).text() for col in range(self.table.columnCount())]
                writer.writerow(headers[:-1])  # Exclude Progress Bar
                for task in self.tasks:
                    writer.writerow([
                        task["Task Name"], task["Category"], task["Priority"], task["Status"],
                        task["Progress (%)"], task["Dependencies"], task["Deliverables"],
                        task["Validation Steps"], task["Notes"]
                    ])

    def refresh_table(self):
        self.table.setRowCount(0)
        for task in self.tasks:
            self.update_filters(task)
            self.insert_task_into_table(task)

    def insert_task_into_table(self, task):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        for col, key in enumerate([
            "Task Name", "Category", "Priority", "Status", 
            "Progress (%)", "Dependencies", "Deliverables", 
            "Validation Steps", "Notes"
        ]):
            item = QTableWidgetItem(task[key])
            if key == "Priority":
                color = self.get_priority_color(task[key])
                item.setBackground(QBrush(color))
            self.table.setItem(row_position, col, item)
        # Add Progress Bar
        progress = QProgressBar()
        progress.setValue(int(task["Progress (%)"]))
        progress.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row_position, 9, progress)

    def update_table_row(self, row, task):
        for col, key in enumerate([
            "Task Name", "Category", "Priority", "Status", 
            "Progress (%)", "Dependencies", "Deliverables", 
            "Validation Steps", "Notes"
        ]):
            item = QTableWidgetItem(task[key])
            if key == "Priority":
                color = self.get_priority_color(task[key])
                item.setBackground(QBrush(color))
            self.table.setItem(row, col, item)
        # Update Progress Bar
        progress = QProgressBar()
        progress.setValue(int(task["Progress (%)"]))
        progress.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, 9, progress)

    def get_priority_color(self, priority):
        if priority == "High":
            return QColor(255, 102, 102)  # Light Red
        elif priority == "Medium":
            return QColor(255, 178, 102)  # Light Orange
        elif priority == "Low":
            return QColor(153, 255, 153)  # Light Green
        else:
            return QColor(255, 255, 255)  # White

    def update_filters(self, task):
        if task["Category"] not in [self.filter_category.itemText(i) for i in range(self.filter_category.count())]:
            self.filter_category.addItem(task["Category"])
        if task["Priority"] not in [self.filter_priority.itemText(i) for i in range(self.filter_priority.count())]:
            self.filter_priority.addItem(task["Priority"])
        if task["Status"] not in [self.filter_status.itemText(i) for i in range(self.filter_status.count())]:
            self.filter_status.addItem(task["Status"])

    def populate_filters(self):
        categories = set(task["Category"] for task in self.tasks)
        priorities = set(task["Priority"] for task in self.tasks)
        statuses = set(task["Status"] for task in self.tasks)

        self.filter_category.clear()
        self.filter_category.addItem("All Categories")
        for category in sorted(categories):
            self.filter_category.addItem(category)

        self.filter_priority.clear()
        self.filter_priority.addItem("All Priorities")
        for priority in sorted(priorities):
            self.filter_priority.addItem(priority)

        self.filter_status.clear()
        self.filter_status.addItem("All Statuses")
        for status in sorted(statuses):
            self.filter_status.addItem(status)

    def apply_filters(self):
        search_text = self.search_bar.text().lower()
        category_filter = self.filter_category.currentText()
        priority_filter = self.filter_priority.currentText()
        status_filter = self.filter_status.currentText()

        self.table.setRowCount(0)
        for task in self.tasks:
            if search_text and search_text not in task["Task Name"].lower() and search_text not in task["Notes"].lower():
                continue
            if category_filter != "All Categories" and task["Category"] != category_filter:
                continue
            if priority_filter != "All Priorities" and task["Priority"] != priority_filter:
                continue
            if status_filter != "All Statuses" and task["Status"] != status_filter:
                continue
            self.insert_task_into_table(task)

    def refresh_filters(self):
        self.filter_category.clear()
        self.filter_category.addItem("All Categories")
        categories = sorted(set(task["Category"] for task in self.tasks))
        self.filter_category.addItems(categories)

        self.filter_priority.clear()
        self.filter_priority.addItem("All Priorities")
        priorities = sorted(set(task["Priority"] for task in self.tasks))
        self.filter_priority.addItems(priorities)

        self.filter_status.clear()
        self.filter_status.addItem("All Statuses")
        statuses = sorted(set(task["Status"] for task in self.tasks))
        self.filter_status.addItems(statuses)


class TaskDialog(QDialog):
    def __init__(self, parent, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("Task Details")
        self.setMinimumWidth(400)
        self.layout = QFormLayout(self)

        self.task_name = QLineEdit(self)
        self.category = QLineEdit(self)
        self.priority = QComboBox(self)
        self.priority.addItems(["High", "Medium", "Low"])
        self.status = QComboBox(self)
        self.status.addItems(["To Do", "In Progress", "Review", "Completed"])
        self.progress = QSpinBox(self)
        self.progress.setRange(0, 100)
        self.dependencies = QLineEdit(self)
        self.deliverables = QLineEdit(self)
        self.validation_steps = QTextEdit(self)
        self.notes = QTextEdit(self)

        self.layout.addRow("Task Name:", self.task_name)
        self.layout.addRow("Category:", self.category)
        self.layout.addRow("Priority:", self.priority)
        self.layout.addRow("Status:", self.status)
        self.layout.addRow("Progress (%):", self.progress)
        self.layout.addRow("Dependencies:", self.dependencies)
        self.layout.addRow("Deliverables:", self.deliverables)
        self.layout.addRow("Validation Steps:", self.validation_steps)
        self.layout.addRow("Notes:", self.notes)

        self.buttons = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.buttons.addWidget(self.ok_button)
        self.buttons.addWidget(self.cancel_button)
        self.layout.addRow(self.buttons)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        if task_data:
            self.set_task_data(task_data)

    def set_task_data(self, task_data):
        self.task_name.setText(task_data["Task Name"])
        self.category.setText(task_data["Category"])
        self.priority.setCurrentText(task_data["Priority"])
        self.status.setCurrentText(task_data["Status"])
        self.progress.setValue(int(task_data["Progress (%)"]) if task_data["Progress (%)"].isdigit() else 0)
        self.dependencies.setText(task_data["Dependencies"])
        self.deliverables.setText(task_data["Deliverables"])
        self.validation_steps.setText(task_data["Validation Steps"])
        self.notes.setText(task_data["Notes"])

    def get_task_data(self):
        return {
            "Task Name": self.task_name.text(),
            "Category": self.category.text(),
            "Priority": self.priority.currentText(),
            "Status": self.status.currentText(),
            "Progress (%)": str(self.progress.value()),
            "Dependencies": self.dependencies.text(),
            "Deliverables": self.deliverables.text(),
            "Validation Steps": self.validation_steps.toPlainText(),
            "Notes": self.notes.toPlainText(),
        }


class YesNoDialog(QDialog):
    def __init__(self, message):
        super().__init__()
        self.setWindowTitle("Confirmation")
        self.layout = QVBoxLayout(self)

        self.message = QLabel(message, self)
        self.layout.addWidget(self.message)

        self.buttons = QHBoxLayout()
        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")
        self.buttons.addWidget(self.yes_button)
        self.buttons.addWidget(self.no_button)
        self.layout.addLayout(self.buttons)

        self.yes_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
