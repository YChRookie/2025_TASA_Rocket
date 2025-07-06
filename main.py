from PySide6.QtWidgets import QApplication
from database.db import DataBaseInterface
from serial_receiver import SerialReceiver
from gui.gui import Visualization
from threading import Thread, Lock
# from server.server import *

database_controller = DataBaseInterface()
serial_receiver = SerialReceiver(database_controller, 'COM7', 115200)

app = QApplication()
win = Visualization(serial_receiver, database_controller)
win.show()
app.exec()
