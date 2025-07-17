# gui.py


# pylint: disable=no-name-in-module, C0103
from PySide6.QtWidgets import (
    QMainWindow,
    QPlainTextEdit,
    QToolBar,
    QTabWidget,
    QVBoxLayout,
    QGridLayout,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import (
    Slot,  # type: ignore
    QTimer,
    QThread
)
from widget.mplWidget import mplWidget
from widget.mapWidget import mapWidget
from widget.vtkWidget import vtkWidget

from controller.database_manager import DatabaseManager
from controller.serial_manager import SerialManager


class MainWindow(QMainWindow):

    def __init__(self, database_manager: DatabaseManager) -> None:
        super().__init__()

        # 初始化 timer(QTimer)
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update)

        stopButton = QAction(text="停止", parent=self)
        startButton = QAction(text="開始", parent=self)
        restartSensorButton = QAction(text="重啟感測器", parent=self)

        startButton.triggered.connect(self.start)
        stopButton.triggered.connect(self.stop)
        restartSensorButton.triggered.connect(self.restart)

        # 初始化 toolbar(ToolBar)
        self.__toolBar = QToolBar(parent=self)
        self.addToolBar(self.__toolBar)
        self.__toolBar.addAction(startButton)
        self.__toolBar.addAction(stopButton)
        self.__toolBar.addAction(restartSensorButton)

        # 初始化 monitor(QTabWidget)
        self.__vtWidget = mplWidget()
        self.__htWidget = mplWidget()
        self.__mapWidget = mapWidget()
        self.__vtkWidget = vtkWidget()
        self.__monitor = QTabWidget()
        self.__monitor_layout = QGridLayout()
        self.__monitor_layout.addWidget(self.__vtWidget, 0, 0)
        self.__monitor_layout.addWidget(self.__htWidget, 0, 1)
        self.__monitor_layout.addWidget(self.__mapWidget, 1, 0)
        self.__monitor_layout.addWidget(self.__vtkWidget, 1, 1)

        # 初始化 terminal(QPlainTextEdit)
        self.__terminal = QPlainTextEdit()

        # 套用 layout(QVBoxLayout)
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.__monitor)
        self.__layout.addWidget(self.__terminal)
        self.setLayout(self.__layout)

        # 初始化 db_mgr(DatabaseManager)
        self.__db_mgr = database_manager
        self.__db_mgr.messageSignal.connect(self.__terminal.appendPlainText)
        self.__db_mgr.errorSignal.connect(self.__terminal.appendPlainText)

        # 初始化 ser_mgr(SerialManager)
        self.__ser_mgr = SerialManager(
            self.__db_mgr, port="/dev/...", baudrate=115200, timeout=0.1, pack_length=11
        )
        self.__ser_mgr.messageSignal.connect(self.__terminal.appendPlainText)
        self.__ser_mgr.errorSignal.connect(self.__terminal.appendPlainText)

    @Slot(str)
    def log_error(self, message: str):
        self.__terminal.appendPlainText(message)

    @Slot()
    def start(self):
        pass

    @Slot()
    def stop(self):
        pass

    @Slot()
    def restart(self):
        pass

    @Slot()
    def update(self):
        elapsed_time = self.__db_mgr.get_elapsed_time()
        speed = self.__db_mgr.get_speed()
        altitude = self.__db_mgr.get_altitude()
        xyz_angle = self.__db_mgr.get_xyz_angle()

        self.__vtWidget.update(speed, altitude)
        self.__htWidget.update(elapsed_time, altitude)
        self.__vtkWidget.update(*xyz_angle)
