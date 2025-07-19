# ~/gui.py


# pylint: disable=E0611, C0103, W0201, C0114, C0115, C0116,
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

from database.database_manager import DatabaseManager
from services.serial_manager import SerialManager
from services.data_fetcher import DataFetcher


class MainWindow(QMainWindow):
    def __init__(self, database_manager: DatabaseManager) -> None:
        super().__init__()

        # 初始化時鐘
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update)

        # 初始化資料庫管理器
        self.__db_thread = QThread()
        self.__db_mgr = database_manager
        self.__db_mgr.messageSignal.connect(self.__terminal.appendPlainText)
        self.__db_mgr.errorSignal.connect(self.__terminal.appendPlainText)
        self.__db_mgr.moveToThread(self.__db_thread)

        # 初始化序列埠管理器
        self.__ser_thread = QThread()
        self.__ser_mgr = SerialManager(
            self.__db_mgr, port="/dev/...", baudrate=115200, timeout=0.1, pack_length=11
        )
        self.__ser_mgr.messageSignal.connect(self.__terminal.appendPlainText)
        self.__ser_mgr.errorSignal.connect(self.__terminal.appendPlainText)
        self.__ser_mgr.moveToThread(self.__ser_thread)
        
        # 初始化資料獲取器
        self.__fethcer_thread = QThread()
        self.__fetcher = DataFetcher(self.__db_mgr)
        self.__fetcher.moveToThread(self.__fethcer_thread)

    def setupUI(self):
        # 新增 QToolBar
        self.__toolBar = QToolBar(parent=self)
        self.addToolBar(self.__toolBar)
        # 初始化 QAction
        startButton = QAction(text="開始", parent=self)
        stopButton = QAction(text="停止", parent=self)
        restartSensorButton = QAction(text="重啟感測器", parent=self)
        # QAction 連接 Slot
        startButton.triggered.connect(self.start)
        stopButton.triggered.connect(self.stop)
        restartSensorButton.triggered.connect(self.restart)
        # QToolbar 新增 QAction
        self.__toolBar.addAction(startButton)
        self.__toolBar.addAction(stopButton)
        self.__toolBar.addAction(restartSensorButton)

        # 初始化監控區
        self.__monitor = QTabWidget()
        self.__monitor_layout = QGridLayout()

        self.__vtWidget = MplWidget()
        self.__vtWidget.setTitle("Velocity")
        self.__htWidget = MplWidget()
        self.__htWidget.setTitle("Altitude")
        self.__htWidget.setLabels("Time", "Altitude")
        self.__vtkWidget = VtkWidget(
            "/media/ubuntu/Data/WorkSpace/Program/2025_TASA_Rocket_refactor/sources/model.stl"
        )
        self.__mapWidget = MapWidget()

        # 設置
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

    @Slot(str):

    
    @Slot()
    def start(self):
        self.__ser_mgr.start()
        self.__ser_mgr.run()
        self.__db_fetcher.start()

    @Slot()
    def stop(self):
        self.__ser_mgr.stop()

    @Slot()
    def restart(self):
        pass
        # self.__ser_mgr.write(b"restart")
