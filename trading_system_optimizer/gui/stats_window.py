"""Placeholder for future statistics GUI."""
from PyQt5 import QtWidgets


class StatsWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stats")
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("Stats will appear here")
        layout.addWidget(label)
