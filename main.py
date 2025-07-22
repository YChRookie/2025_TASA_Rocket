# pylint: disable=E0611
import sys
from PySide6.QtWidgets import QApplication
from database.database_manager import DatabaseManager
from view.gui import Window

db_mgr = DatabaseManager()

app = QApplication()
win = Window(db_mgr)
win.show()

sys.exit(app.exec())
