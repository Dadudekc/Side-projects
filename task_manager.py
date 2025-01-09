import sys
import csv
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QDialog, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QTextEdit, QFileDialog, QLabel, QProgressBar, QHeaderView,
    QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Improved Task Manager")
        self.setGeometry(100, 100, 1300, 700)

        self.tasks = []
        self.init_ui()
        self.load_tasks()  # Auto-load tasks on startup if tasks.json exists

    def init_ui(self):
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        # -- Search & Filter Controls --
        self.filter_layout = QHBoxLayout()
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search tasks...")

        self.filter_category = QComboBox(self)
        self.filter_category.addItem("All Categories")

        self.filter_priority = QComboBox(self)
        self.filter_priority.addItem("All Priorities")

        self.filter_status = QComboBox(self)
        self.filter_status.addItem("All Statuses")

        # Optional Date Range filter to see tasks due within range
        self.from_date = QDateEdit(self)
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setDate(QDate.currentDate().addMonths(-1))  # default: 1 month prior

        self.to_date = QDateEdit(self)
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setDate(QDate.currentDate().addYears(1))  # default: 1 year ahead

        self.filter_button = QPushButton("Apply Filters")

        # Arrange filters
        self.filter_layout.addWidget(QLabel("Search:"))
        self.filter_layout.addWidget(self.search_bar)
        self.filter_layout.addWidget(QLabel("Category:"))
        self.filter_layout.addWidget(self.filter_category)
        self.filter_layout.addWidget(QLabel("Priority:"))
        self.filter_layout.addWidget(self.filter_priority)
        self.filter_layout.addWidget(QLabel("Status:"))
        self.filter_layout.addWidget(self.filter_status)
        self.filter_layout.addWidget(QLabel("Due From:"))
        self.filter_layout.addWidget(self.from_date)
        self.filter_layout.addWidget(QLabel("To:"))
        self.filter_layout.addWidget(self.to_date)
        self.filter_layout.addWidget(self.filter_button)

        self.layout.addLayout(self.filter_layout)

        # -- Table Setup --
        self.table = QTableWidget()
        self.table.setColumnCount(13)
        self.table.setHorizontalHeaderLabels([
            "Task Name", "Category", "Priority", "Status",
            "Progress (%)", "Owner", "Due Date", "Tag",
            "Dependencies", "Deliverables", "Validation Steps",
            "Notes", "Progress Bar"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        # -- Button Row --
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Task")
        self.edit_button = QPushButton("Edit Task")
        self.delete_button = QPushButton("Delete Task")
        self.save_button = QPushButton("Save to JSON")
        self.load_button = QPushButton("Load from JSON")
        self.export_button = QPushButton("Export to CSV")
        self.clear_button = QPushButton("Clear All Tasks")
        self.stats_button = QPushButton("View Stats")

        # Add buttons to layout
        for b in [
            self.add_button, self.edit_button, self.delete_button,
            self.save_button, self.load_button, self.export_button,
            self.clear_button, self.stats_button
        ]:
            self.button_layout.addWidget(b)

        self.layout.addLayout(self.button_layout)
        self.setCentralWidget(self.main_widget)

        # -- Button Signals --
        self.add_button.clicked.connect(self.add_task)
        self.edit_button.clicked.connect(self.edit_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.save_button.clicked.connect(self.save_tasks)
        self.load_button.clicked.connect(self.load_tasks)
        self.export_button.clicked.connect(self.export_tasks)
        self.clear_button.clicked.connect(self.clear_tasks)
        self.filter_button.clicked.connect(self.apply_filters)
        self.search_bar.textChanged.connect(self.apply_filters)
        self.stats_button.clicked.connect(self.view_stats)

    def add_task(self):
        dialog = TaskDialog(self)
        if dialog.exec_():
            new_task = dialog.get_task_data()
            self.tasks.append(new_task)
            self.update_filters(new_task)
            self.insert_task_into_table(new_task)
            self.save_tasks_auto()

    def edit_task(self):
        row = self.table.currentRow()
        if row < 0:
            return
        current_data = self.tasks[row]
        dialog = TaskDialog(self, current_data)
        if dialog.exec_():
            updated_task = dialog.get_task_data()
            self.tasks[row] = updated_task
            self.update_table_row(row, updated_task)
            self.update_filters(updated_task)
            self.save_tasks_auto()

    def delete_task(self):
        row = self.table.currentRow()
        if row >= 0:
            del self.tasks[row]
            self.table.removeRow(row)
            self.save_tasks_auto()

    def clear_tasks(self):
        confirm = YesNoDialog("Are you sure you want to delete all tasks?")
        if confirm.exec_() == QDialog.Accepted:
            self.tasks.clear()
            self.table.setRowCount(0)
            self.reset_filters()
            self.save_tasks_auto()

    def save_tasks(self):
        """Manually pick a JSON file to save tasks."""
        path, _ = QFileDialog.getSaveFileName(self, "Save Tasks", "", "JSON Files (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=4)

    def load_tasks(self):
        """Manually pick a JSON file to load tasks."""
        path, _ = QFileDialog.getOpenFileName(self, "Load Tasks", "", "JSON Files (*.json)")
        if path:
            with open(path, "r", encoding="utf-8") as file:
                self.tasks = json.load(file)
            self.refresh_table()
            self.populate_filters()

    def save_tasks_auto(self):
        """Auto-save to a default tasks.json whenever a change is made."""
        try:
            with open("tasks.json", "w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=4)
        except Exception as e:
            print("Auto-save failed:", e)

    def export_tasks(self):
        """Exports tasks to CSV."""
        path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers[:-1])  # Exclude the progress bar column
                for t in self.tasks:
                    row_data = [
                        t["Task Name"], t["Category"], t["Priority"], t["Status"], t["Progress (%)"],
                        t["Owner"], t["Due Date"], t["Tag"],
                        t["Dependencies"], t["Deliverables"],
                        t["Validation Steps"], t["Notes"]
                    ]
                    writer.writerow(row_data)

    def refresh_table(self):
        """Reloads the table with current tasks."""
        self.table.setRowCount(0)
        for t in self.tasks:
            self.insert_task_into_table(t)

    def insert_task_into_table(self, task_data):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Fill normal cells
        keys = [
            "Task Name", "Category", "Priority", "Status",
            "Progress (%)", "Owner", "Due Date", "Tag",
            "Dependencies", "Deliverables", "Validation Steps", "Notes"
        ]
        for col, key in enumerate(keys):
            item = QTableWidgetItem(task_data[key])

            # Highlight priority cell
            if key == "Priority":
                color = self.get_priority_color(task_data[key])
                item.setBackground(QBrush(color))

            # Highlight overdue tasks
            if key == "Due Date" and self.is_overdue(task_data[key], task_data["Status"]):
                item.setBackground(QBrush(QColor(255, 150, 150)))  # red-ish

            self.table.setItem(row_position, col, item)

        # Add progress bar
        progress_bar = QProgressBar()
        progress_val = int(task_data["Progress (%)"]) if task_data["Progress (%)"].isdigit() else 0
        progress_bar.setValue(progress_val)
        progress_bar.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row_position, 12, progress_bar)

    def update_table_row(self, row, updated_task):
        """Update existing row with new task data."""
        keys = [
            "Task Name", "Category", "Priority", "Status",
            "Progress (%)", "Owner", "Due Date", "Tag",
            "Dependencies", "Deliverables", "Validation Steps", "Notes"
        ]
        for col, key in enumerate(keys):
            item = QTableWidgetItem(updated_task[key])

            # Update cell coloring
            if key == "Priority":
                color = self.get_priority_color(updated_task[key])
                item.setBackground(QBrush(color))
            if key == "Due Date" and self.is_overdue(updated_task[key], updated_task["Status"]):
                item.setBackground(QBrush(QColor(255, 150, 150)))

            self.table.setItem(row, col, item)

        # Update progress bar
        progress_bar = QProgressBar()
        progress_val = int(updated_task["Progress (%)"]) if updated_task["Progress (%)"].isdigit() else 0
        progress_bar.setValue(progress_val)
        progress_bar.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, 12, progress_bar)

    def apply_filters(self):
        """Filters tasks by text, category, priority, status, and due date range."""
        search_text = self.search_bar.text().lower()
        cat_filter = self.filter_category.currentText()
        pri_filter = self.filter_priority.currentText()
        stat_filter = self.filter_status.currentText()
        from_dt = self.from_date.date().toPyDate()
        to_dt = self.to_date.date().toPyDate()

        self.table.setRowCount(0)
        for task in self.tasks:
            # Search match on Task Name or Notes
            if search_text:
                if search_text not in task["Task Name"].lower() and search_text not in task["Notes"].lower():
                    continue
            # Category filter
            if cat_filter != "All Categories" and task["Category"] != cat_filter:
                continue
            # Priority filter
            if pri_filter != "All Priorities" and task["Priority"] != pri_filter:
                continue
            # Status filter
            if stat_filter != "All Statuses" and task["Status"] != stat_filter:
                continue
            # Date range filter (only apply if user has set a from/to date)
            task_due_date = self.parse_date(task["Due Date"])
            if task_due_date is not None:
                if task_due_date < from_dt or task_due_date > to_dt:
                    continue

            # If all conditions are satisfied, add row
            self.insert_task_into_table(task)

    def parse_date(self, date_str):
        """Converts date string to a Python datetime.date object, or None on failure."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def is_overdue(self, due_date_str, status):
        """Check if a task is overdue (due date < today and not completed)."""
        due_date = self.parse_date(due_date_str)
        if not due_date or status.lower() == "completed":
            return False
        return due_date < datetime.now().date()

    def get_priority_color(self, priority):
        """Return a soft background color by priority level."""
        if priority == "High":
            return QColor(255, 102, 102)   # Light Red
        elif priority == "Medium":
            return QColor(255, 178, 102)  # Light Orange
        elif priority == "Low":
            return QColor(153, 255, 153)  # Light Green
        else:
            return QColor(255, 255, 255)  # White

    def update_filters(self, task):
        """Dynamically add new filter options if they appear in tasks."""
        if task["Category"] not in [self.filter_category.itemText(i) for i in range(self.filter_category.count())]:
            self.filter_category.addItem(task["Category"])
        if task["Priority"] not in [self.filter_priority.itemText(i) for i in range(self.filter_priority.count())]:
            self.filter_priority.addItem(task["Priority"])
        if task["Status"] not in [self.filter_status.itemText(i) for i in range(self.filter_status.count())]:
            self.filter_status.addItem(task["Status"])

    def populate_filters(self):
        """Refresh filter combo boxes for Category, Priority, and Status."""
        categories = set(t["Category"] for t in self.tasks)
        priorities = set(t["Priority"] for t in self.tasks)
        statuses = set(t["Status"] for t in self.tasks)

        # Category
        self.filter_category.clear()
        self.filter_category.addItem("All Categories")
        for c in sorted(categories):
            self.filter_category.addItem(c)

        # Priority
        self.filter_priority.clear()
        self.filter_priority.addItem("All Priorities")
        for p in sorted(priorities):
            self.filter_priority.addItem(p)

        # Status
        self.filter_status.clear()
        self.filter_status.addItem("All Statuses")
        for s in sorted(statuses):
            self.filter_status.addItem(s)

    def reset_filters(self):
        """Clears all filter values to default."""
        self.filter_category.clear()
        self.filter_category.addItem("All Categories")
        self.filter_priority.clear()
        self.filter_priority.addItem("All Priorities")
        self.filter_status.clear()
        self.filter_status.addItem("All Statuses")

    def view_stats(self):
        """Displays basic statistics: total tasks, completion rate, overdue tasks."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["Status"].lower() == "completed")
        overdue = sum(1 for t in self.tasks if self.is_overdue(t["Due Date"], t["Status"]))

        msg = (
            f"<b>Total Tasks:</b> {total}<br>"
            f"<b>Completed:</b> {completed} ({(completed/total)*100 if total else 0:.1f}%)<br>"
            f"<b>Overdue:</b> {overdue}"
        )

        dialog = StatsDialog("Task Stats", msg, self)
        dialog.exec_()


class TaskDialog(QDialog):
    def __init__(self, parent, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("Task Details")
        self.setMinimumWidth(400)
        self.layout = QFormLayout(self)

        # Widget definitions
        self.task_name = QLineEdit(self)
        self.category = QLineEdit(self)
        self.priority = QComboBox(self)
        self.priority.addItems(["High", "Medium", "Low"])
        self.status = QComboBox(self)
        self.status.addItems(["To Do", "In Progress", "Review", "Completed"])

        self.progress = QSpinBox(self)
        self.progress.setRange(0, 100)

        self.owner = QLineEdit(self)
        self.due_date = QLineEdit(self)
        self.due_date.setPlaceholderText("YYYY-MM-DD")

        self.tag = QLineEdit(self)
        self.dependencies = QLineEdit(self)
        self.deliverables = QLineEdit(self)
        self.validation_steps = QTextEdit(self)
        self.notes = QTextEdit(self)

        # Layout fields
        self.layout.addRow("Task Name:", self.task_name)
        self.layout.addRow("Category:", self.category)
        self.layout.addRow("Priority:", self.priority)
        self.layout.addRow("Status:", self.status)
        self.layout.addRow("Progress (%):", self.progress)
        self.layout.addRow("Owner:", self.owner)
        self.layout.addRow("Due Date:", self.due_date)
        self.layout.addRow("Tag:", self.tag)
        self.layout.addRow("Dependencies:", self.dependencies)
        self.layout.addRow("Deliverables:", self.deliverables)
        self.layout.addRow("Validation Steps:", self.validation_steps)
        self.layout.addRow("Notes:", self.notes)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addRow(self.button_layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        if task_data:
            self.set_task_data(task_data)

    def set_task_data(self, t):
        self.task_name.setText(t["Task Name"])
        self.category.setText(t["Category"])
        self.priority.setCurrentText(t["Priority"])
        self.status.setCurrentText(t["Status"])
        self.progress.setValue(int(t["Progress (%)"]) if t["Progress (%)"].isdigit() else 0)
        self.owner.setText(t["Owner"])
        self.due_date.setText(t["Due Date"])
        self.tag.setText(t["Tag"])
        self.dependencies.setText(t["Dependencies"])
        self.deliverables.setText(t["Deliverables"])
        self.validation_steps.setText(t["Validation Steps"])
        self.notes.setText(t["Notes"])

    def get_task_data(self):
        return {
            "Task Name": self.task_name.text(),
            "Category": self.category.text(),
            "Priority": self.priority.currentText(),
            "Status": self.status.currentText(),
            "Progress (%)": str(self.progress.value()),
            "Owner": self.owner.text(),
            "Due Date": self.due_date.text(),
            "Tag": self.tag.text(),
            "Dependencies": self.dependencies.text(),
            "Deliverables": self.deliverables.text(),
            "Validation Steps": self.validation_steps.toPlainText(),
            "Notes": self.notes.toPlainText(),
        }


class YesNoDialog(QDialog):
    """Simple confirm dialog."""
    def __init__(self, message):
        super().__init__()
        self.setWindowTitle("Confirmation")
        layout = QVBoxLayout(self)

        self.message_label = QLabel(message, self)
        layout.addWidget(self.message_label)

        btn_layout = QHBoxLayout()
        self.yes_button = QPushButton("Yes")
        self.no_button = QPushButton("No")
        btn_layout.addWidget(self.yes_button)
        btn_layout.addWidget(self.no_button)

        layout.addLayout(btn_layout)
        self.yes_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)


class StatsDialog(QDialog):
    """Simple info dialog for stats overview."""
    def __init__(self, title, html_msg, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setTextFormat(Qt.RichText)
        self.label.setText(html_msg)
        layout.addWidget(self.label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
