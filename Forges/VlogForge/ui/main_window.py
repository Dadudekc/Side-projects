import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QListWidget, QMessageBox, QLineEdit, QDateEdit, QHBoxLayout
from PyQt5.QtCore import QDate, QTimer
from datetime import datetime
from ui.content_calendar import ContentCalendar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VlogForge Dashboard")
        self.setGeometry(100, 100, 600, 500)

        self.calendar = ContentCalendar()

        # Main Layout
        layout = QVBoxLayout()

        # Widgets
        self.reminder_label = QLabel("Reminders:")
        self.reminder_list = QListWidget()

        self.missed_label = QLabel("Missed Events:")
        self.missed_list = QListWidget()

        self.add_event_label = QLabel("Add New Event:")
        self.event_title_input = QLineEdit()
        self.event_title_input.setPlaceholderText("Event Title")
        self.event_date_input = QDateEdit()
        self.event_date_input.setDate(QDate.currentDate())

        self.add_event_button = QPushButton("Add Event")
        self.add_event_button.clicked.connect(self.add_event)

        self.refresh_button = QPushButton("Refresh Dashboard")
        self.refresh_button.clicked.connect(self.refresh_dashboard)

        # Add widgets to layout
        layout.addWidget(self.reminder_label)
        layout.addWidget(self.reminder_list)
        layout.addWidget(self.missed_label)
        layout.addWidget(self.missed_list)

        # Add Event Section
        add_event_layout = QHBoxLayout()
        add_event_layout.addWidget(self.event_title_input)
        add_event_layout.addWidget(self.event_date_input)
        add_event_layout.addWidget(self.add_event_button)
        layout.addLayout(add_event_layout)

        layout.addWidget(self.refresh_button)

        # Main Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initial Dashboard Load
        self.refresh_dashboard()

        # Auto-refresh reminders every hour
        timer = QTimer(self)
        timer.timeout.connect(self.refresh_dashboard)
        timer.start(3600000)  # 1 hour

    def refresh_dashboard(self):
        self.reminder_list.clear()
        self.missed_list.clear()

        # Load reminders
        reminders = self.calendar.get_reminders()
        for reminder in reminders:
            self.reminder_list.addItem(f"{reminder['title']} - Due on {reminder['scheduled_date']}")

        # Load missed events
        self.calendar.check_missed_events()  # Update missed events
        missed_events = [event for event in self.calendar.get_scheduled_content() if event['status'] == 'Missed']
        for event in missed_events:
            self.missed_list.addItem(f"{event['title']} - Missed on {event['scheduled_date']}")

        # Confirmation Message
        QMessageBox.information(self, "Dashboard Refreshed", "Dashboard data has been updated successfully.")

    def add_event(self):
        title = self.event_title_input.text()
        date = self.event_date_input.date().toString("yyyy-MM-dd")

        if title:
            self.calendar.add_to_calendar(title, date)
            QMessageBox.information(self, "Event Added", f"Event '{title}' scheduled for {date} has been added.")
            self.refresh_dashboard()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a valid event title.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
