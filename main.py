from PySide6.QtWidgets import QApplication, QPlainTextEdit
from database.dbmgr import DatabaseManager

# from serial_receiver import _

app = QApplication()
ter = QPlainTextEdit()
dbmgr = DatabaseManager(ter)
