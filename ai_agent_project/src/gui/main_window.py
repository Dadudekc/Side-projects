import sys
import asyncio
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QLabel
from reasoner_controller import ReasonerController
from task_manager import TaskManager

class TaskThread(QThread):
    """
    Runs the task in a separate thread and emits a signal upon completion.
    """
    task_complete = pyqtSignal(str)

    def __init__(self, task, manager):
        super().__init__()
        self.task = task
        self.manager = manager

    def run(self):
        """
        Runs the async task and emits the result when complete.
        """
        # Run the async function synchronously from the QThread context
        result = asyncio.run(self.manager.run_task_async(self.task))
        self.task_complete.emit(result)

class MainWindow(QMainWindow):
    """
    Main window for interacting with the ChainOfThoughtReasoner.
    Provides UI elements for task input, displaying results, and initiating reasoning processes.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Debugging Assistant")
        self.setGeometry(200, 200, 600, 400)
        
        # Initialize controller and task manager
        self.controller = ReasonerController()
        self.task_manager = TaskManager()

        # UI Elements
        self.task_input = QTextEdit(self)
        self.task_input.setPlaceholderText("Enter task for reasoning...")

        self.run_button = QPushButton("Run Task", self)
        self.run_button.clicked.connect(self.run_task)

        self.result_display = QLabel("Result will appear here...", self)
        self.result_display.setWordWrap(True)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.task_input)
        layout.addWidget(self.run_button)
        layout.addWidget(self.result_display)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_task(self):
        """
        Initiates the reasoning process by passing the task input to TaskManager asynchronously.
        """
        task = self.task_input.toPlainText()
        
        # Create and start the TaskThread with the async task manager
        self.task_thread = TaskThread(task, self.task_manager)
        self.task_thread.task_complete.connect(self.display_result)
        self.task_thread.start()

    def display_result(self, result):
        """
        Displays the result from TaskManager in the GUI.
        """
        self.result_display.setText(result)

def run_application():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_application()


_|