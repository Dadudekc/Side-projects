"""Simple PyQt5 form for logging trades."""
from PyQt5 import QtWidgets

from ..journal.trade_entry import TradeEntry
from ..journal import journal_manager


class LoggerWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trade Logger")
        layout = QtWidgets.QFormLayout(self)

        self.ticker_input = QtWidgets.QLineEdit()
        self.entry_input = QtWidgets.QLineEdit()
        self.exit_input = QtWidgets.QLineEdit()
        self.notes_input = QtWidgets.QTextEdit()
        submit = QtWidgets.QPushButton("Log Trade")

        layout.addRow("Ticker", self.ticker_input)
        layout.addRow("Entry", self.entry_input)
        layout.addRow("Exit", self.exit_input)
        layout.addRow("Notes", self.notes_input)
        layout.addRow(submit)

        submit.clicked.connect(self.log_trade)

    def log_trade(self):
        ticker = self.ticker_input.text()
        try:
            entry = float(self.entry_input.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Invalid", "Entry price must be a number")
            return
        exit_price = self.exit_input.text()
        exit_val = float(exit_price) if exit_price else None
        notes = self.notes_input.toPlainText()
        entry_obj = TradeEntry(ticker=ticker, entry=entry, exit=exit_val, notes=notes)
        journal_manager.append_entry(entry_obj)
        QtWidgets.QMessageBox.information(self, "Saved", "Trade logged successfully!")
        self.ticker_input.clear()
        self.entry_input.clear()
        self.exit_input.clear()
        self.notes_input.clear()


def run_logger():
    app = QtWidgets.QApplication([])
    win = LoggerWindow()
    win.show()
    app.exec()
