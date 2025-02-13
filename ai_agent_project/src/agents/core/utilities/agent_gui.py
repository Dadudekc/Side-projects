# agent_gui.py

# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\agents\core\utilities\agent_gui.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# Implements a PyQt5 graphical user interface (GUI) for managing tasks,
# viewing logs, and interacting with the AgentBase-derived agent.
#
# -------------------------------------------------------------------

import sys
import threading
import time
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QListWidget, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, QTimer
from agent_base import TaskState, Task, ResolutionHistory, UserDecisionCache, AgentBase

class AgentGUI(QMainWindow):
    def __init__(self, agent: SampleAgent):
        super().__init__()
        self.agent = agent
        self.setWindowTitle("AI Debugger Assistant - Task Manager")
        self.setGeometry(100, 100, 1000, 700)
        self.init_ui()

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left panel: Task Management
        task_panel = QVBoxLayout()

        # Add Task Section
        add_task_label = QLabel("Add New Task")
        add_task_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        task_panel.addWidget(add_task_label)

        self.task_type_input = QComboBox()
        self.task_type_input.addItems(["simple_task", "trigger_error", "plugin_task"])
        task_panel.addWidget(QLabel("Task Type:"))
        task_panel.addWidget(self.task_type_input)

        self.plugin_name_input = QLineEdit()
        self.plugin_name_input.setPlaceholderText("Plugin Name (for plugin_task)")
        task_panel.addWidget(QLabel("Plugin Name:"))
        task_panel.addWidget(self.plugin_name_input)

        self.plugin_data_input = QLineEdit()
        self.plugin_data_input.setPlaceholderText("Plugin Data (JSON format)")
        task_panel.addWidget(QLabel("Plugin Data:"))
        task_panel.addWidget(self.plugin_data_input)

        add_task_button = QPushButton("Add Task")
        add_task_button.clicked.connect(self.add_task)
        task_panel.addWidget(add_task_button)

        # Task List Section
        task_list_label = QLabel("Scheduled Tasks")
        task_list_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        task_panel.addWidget(task_list_label)

        self.task_list = QListWidget()
        task_panel.addWidget(self.task_list)

        refresh_tasks_button = QPushButton("Refresh Tasks")
        refresh_tasks_button.clicked.connect(self.refresh_tasks)
        task_panel.addWidget(refresh_tasks_button)

        # Delete Task Section
        delete_task_button = QPushButton("Delete Selected Task")
        delete_task_button.clicked.connect(self.delete_task)
        task_panel.addWidget(delete_task_button)

        main_layout.addLayout(task_panel, 2)

        # Right panel: Logs and Resolutions
        logs_resolutions_panel = QVBoxLayout()

        # Logs Viewer
        logs_label = QLabel("Agent Logs")
        logs_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        logs_resolutions_panel.addWidget(logs_label)

        self.logs_viewer = QTextEdit()
        self.logs_viewer.setReadOnly(True)
        logs_resolutions_panel.addWidget(self.logs_viewer)

        # Resolution History
        resolution_label = QLabel("Resolution History")
        resolution_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        logs_resolutions_panel.addWidget(resolution_label)

        self.resolution_viewer = QTextEdit()
        self.resolution_viewer.setReadOnly(True)
        logs_resolutions_panel.addWidget(self.resolution_viewer)

        refresh_logs_button = QPushButton("Refresh Logs")
        refresh_logs_button.clicked.connect(self.refresh_logs)
        logs_resolutions_panel.addWidget(refresh_logs_button)

        refresh_resolutions_button = QPushButton("Refresh Resolutions")
        refresh_resolutions_button.clicked.connect(self.refresh_resolutions)
        logs_resolutions_panel.addWidget(refresh_resolutions_button)

        main_layout.addLayout(logs_resolutions_panel, 3)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Set up timers for auto-refresh
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_logs)
        self.log_timer.start(5000)  # Refresh every 5 seconds

        self.resolution_timer = QTimer()
        self.resolution_timer.timeout.connect(self.update_resolutions)
        self.resolution_timer.start(10000)  # Refresh every 10 seconds

    def add_task(self):
        task_type = self.task_type_input.currentText()
        plugin_name = self.plugin_name_input.text().strip()
        plugin_data_text = self.plugin_data_input.text().strip()

        task_data = {"type": task_type}

        if task_type == "plugin_task":
            if not plugin_name:
                QMessageBox.warning(self, "Input Error", "Plugin Name is required for plugin_task.")
                return
            task_data["plugin_name"] = plugin_name
            if plugin_data_text:
                try:
                    plugin_data = json.loads(plugin_data_text)
                    task_data["plugin_data"] = plugin_data
                except json.JSONDecodeError:
                    QMessageBox.warning(self, "Input Error", "Plugin Data must be in valid JSON format.")
                    return

        # Schedule the task
        try:
            self.agent.schedule_task(
                cron_expression="*/1 * * * *",  # Example: Every minute
                task_callable=self.agent.handle_task_with_error_handling,
                task_data=task_data,
                task_id=f"{task_type}_{int(time.time())}"
            )
            QMessageBox.information(self, "Success", f"Task '{task_type}' added successfully.")
            self.refresh_tasks()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add task: {str(e)}")

    def refresh_tasks(self):
        self.task_list.clear()
        jobs = self.agent.scheduler.get_jobs()
        for job in jobs:
            task_id = job.id
            next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "N/A"
            task_info = f"ID: {task_id} | Next Run: {next_run} | Callable: {job.func.__name__}"
            self.task_list.addItem(task_info)

    def delete_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a task to delete.")
            return
        for item in selected_items:
            task_info = item.text()
            task_id = task_info.split("|")[0].split(":")[1].strip()
            try:
                self.agent.remove_scheduled_task(task_id)
                QMessageBox.information(self, "Success", f"Task '{task_id}' removed successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to remove task '{task_id}': {str(e)}")
        self.refresh_tasks()

    def refresh_logs(self):
        self.update_logs()

    def update_logs(self):
        try:
            with open(f"{self.agent.name}.log", "r") as log_file:
                logs = log_file.read()
                self.logs_viewer.setText(logs)
        except FileNotFoundError:
            self.logs_viewer.setText("Log file not found.")

    def refresh_resolutions(self):
        self.update_resolutions()

    def update_resolutions(self):
        session = self.agent.Session()
        resolutions = session.query(self.agent.ResolutionHistory).order_by(self.agent.ResolutionHistory.timestamp.desc()).all()
        session.close()
        resolution_text = ""
        for res in resolutions:
            resolution_text += f"[{res.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] Error: {res.error_message}\n"
            if res.ai_suggestion:
                resolution_text += f"AI Suggestion: {res.ai_suggestion}\n"
            if res.user_decision:
                resolution_text += f"User Decision: {res.user_decision}\n"
            resolution_text += "-" * 50 + "\n"
        self.resolution_viewer.setText(resolution_text)

def main():
    # Instantiate the SampleAgent
    agent = SampleAgent(
        name="SampleAgent",
        description="A test agent with plugin support and AI self-healing capabilities.",
        plugin_dir="plugins",  # Ensure this directory exists and contains plugin modules
        log_to_file=True
    )

    # Start the PyQt5 application
    app = QApplication(sys.argv)
    gui = AgentGUI(agent)
    gui.show()

    # Start the agent's scheduler in a separate thread to prevent blocking the GUI
    def run_scheduler():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            agent.shutdown()

    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
