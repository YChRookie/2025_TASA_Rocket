# gui.py


# pylint: disable=no-name-in-module, C0103
from PySide6.QtWidgets import (
    QMainWindow,
    QPlainTextEdit,
    QWidget,
    QToolBar,
    QTabWidget,
    QVBoxLayout,
    QGridLayout,
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot, QTimer, QThread  # type: ignore
from view.widget.MplWidget import MplWidget
from view.widget.MapWidget import MapWidget
from view.widget.VtkWidget import VtkWidget

from controller.database_manager import DatabaseManager
from controller.serial_manager import SerialManager
from controller.data_fetcher import DataFetcher


class MainWindow(QMainWindow):
    def __init__(self, database_manager: DatabaseManager) -> None:
        super().__init__()

        # 初始化時鐘
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update)

        # 初始化資料庫管理器
        self.__db_mgr = database_manager
        self.__db_mgr.messageSignal.connect(self.__terminal.appendPlainText)
        self.__db_mgr.errorSignal.connect(self.__terminal.appendPlainText)

        # 初始化序列埠管理器
        self.__ser_mgr = SerialManager(
            self.__db_mgr, port="/dev/...", baudrate=115200, timeout=0.1, pack_length=11
        )
        self.__ser_mgr.messageSignal.connect(self.__terminal.appendPlainText)
        self.__ser_mgr.errorSignal.connect(self.__terminal.appendPlainText)
        self.ser_thread = QThread()
        self.__ser_mgr.moveToThread(self.ser_thread)
        self.ser_thread.started.connect(self.__ser_mgr.run)

        # 初始化資料流
        self.__db_fetcher = DataFetcher(self.__db_mgr)
        self.fetcher_thread = QThread()
        self.__db_fetcher.moveToThread(self.fetcher_thread)
        self.fetcher_thread.started.connect(self.__db_fetcher.start)

    def setupUI(self):
        # 初始化工具列
        startButton = QAction(text="開始", parent=self)
        stopButton = QAction(text="停止", parent=self)
        restartSensorButton = QAction(text="重啟感測器", parent=self)

        startButton.triggered.connect(self.start)
        stopButton.triggered.connect(self.stop)
        restartSensorButton.triggered.connect(self.restart)

        self.__toolBar = QToolBar(parent=self)
        self.addToolBar(self.__toolBar)
        self.__toolBar.addAction(startButton)
        self.__toolBar.addAction(stopButton)
        self.__toolBar.addAction(restartSensorButton)

        self.__vtWidget = MPLWidget()
        self.__htWidget = MPLWidget()
        self.__mapWidget = MapWidget()
        self.__vtkWidget = VTKWidget()
        self.__monitor = QTabWidget()
        self.__monitor_layout = QGridLayout()
        self.__monitor_layout.addWidget(self.__vtWidget, 0, 0)
        self.__monitor_layout.addWidget(self.__htWidget, 0, 1)
        self.__monitor_layout.addWidget(self.__mapWidget, 1, 0)
        self.__monitor_layout.addWidget(self.__vtkWidget, 1, 1)

        self.__terminal = QPlainTextEdit()
        self.__terminal.setReadOnly(True)

        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
        self.mainLayout.addWidget(self.__monitor)
        self.mainLayout.addWidget(self.__terminal)

    @Slot(str)
    def log_error(self, message: str):
        self.__terminal.appendPlainText(message)

    @Slot()
    def start(self):
        self.__ser_mgr.start()
        self.__ser_mgr.run()
        self.__db_fetcher.start()

    @Slot()
    def stop(self):
        pass

    @Slot()
    def restart(self):
        self.__ser_mgr.write(b"restart")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    win = MainWindow()
    win.show()
    app.exec()
