# ~/gui.py


# pylint: disable=E0611, C0114, C0103
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
from PySide6.QtCore import Slot, QThread
from view.widget.MplWidget import VtWidget, HtWidget
from view.widget.MapWidget import MapWidget
from view.widget.VtkWidget import VtkWidget

from database.database_manager import DatabaseManager
from services.serial_manager import SerialManager
from services.data_fetcher import DataFetcher


class Window(QMainWindow):
    def __init__(self, database_manager: DatabaseManager) -> None:
        super().__init__()

        self.setupUI()

        # 引用資料庫管理器實例
        self.db_mgr = database_manager

        # 初始化序列埠管理器
        self.serialThread = QThread()
        self.serialManager = SerialManager(
            self.db_mgr,
            port="/dev/ttyUSB0",
            baudrate=115200,
            timeout=0.1,
            pack_length=11,
        )
        self.serialManager.messageSignal.connect(self.loggingWidget.appendPlainText)
        self.serialManager.errorSignal.connect(self.loggingWidget.appendPlainText)
        self.serialManager.moveToThread(self.serialThread)
        self.serialThread.started.connect(self.serialManager.start_serial_communication)

        # 初始化資料獲取器
        self.dataFetcherThread = QThread()
        self.dataFetcher = DataFetcher(self.db_mgr)
        self.dataFetcher.dataReady.connect(self.updateWidget)
        self.dataFetcher.messageSignal.connect(self.loggingWidget.appendPlainText)
        self.dataFetcher.errorSignal.connect(self.loggingWidget.appendPlainText)
        self.dataFetcher.moveToThread(self.dataFetcherThread)
        self.dataFetcherThread.started.connect(self.dataFetcher.start_fetching)

    def setupUI(self):
        """初始化UI"""

        # 新增 QToolBar
        self.toolBar = QToolBar(parent=self)
        self.addToolBar(self.toolBar)
        # 初始化 QAction
        startButton = QAction(text="開始", parent=self.toolBar)
        startButton.triggered.connect(self.start)
        stopButton = QAction(text="停止", parent=self.toolBar)
        stopButton.triggered.connect(self.stop)
        # 設置 QAction
        self.toolBar.addAction(startButton)
        self.toolBar.addAction(stopButton)

        self.vtPlot = VtWidget()
        self.vtPlot.set_title("Velocity")
        self.htPlot = HtWidget()
        self.htPlot.set_title("Altitude")
        self.modelOrientation = QWidget()
        self.map = MapWidget()

        # 設置 DashBoard
        self.dashBoard = QWidget()
        self.dashBoardLayout = QGridLayout()
        self.dashBoard.setLayout(self.dashBoardLayout)
        self.dashBoardLayout.addWidget(self.vtPlot, 0, 0)
        self.dashBoardLayout.addWidget(self.htPlot, 0, 1)
        self.dashBoardLayout.addWidget(self.modelOrientation, 1, 0)
        self.dashBoardLayout.addWidget(self.map, 1, 1)

        # 設置 TabWidget
        self.tab = QTabWidget(parent=self)
        self.tab.addTab(self.dashBoard, "DashBoard")
        self.tab.addTab(self.vtPlot, "Velocity")
        self.tab.addTab(self.htPlot, "Altitude")
        self.tab.addTab(self.modelOrientation, "Orientation")
        self.tab.addTab(self.map, "Location")

        # 設置 Logging 元件
        self.loggingWidget = QPlainTextEdit()
        self.loggingWidget.setReadOnly(True)

        # 設置 CentralWidget
        self.bottomWidget = QWidget()
        self.bottomLayout = QVBoxLayout()
        self.bottomWidget.setLayout(self.bottomLayout)
        self.setCentralWidget(self.bottomWidget)

        self.bottomLayout.addWidget(self.tab, 3)  # Chart 布局比例 3/4
        self.bottomLayout.addWidget(self.loggingWidget, 1)  # Logging 布局比例 1/4

    @Slot()
    def start(self):
        """開始讀取序列埠並更新圖表"""

        self.serialThread.start()
        self.dataFetcherThread.start()

    @Slot()
    def stop(self):
        """停止讀取序列埠並更新圖表"""

        self.serialThread.quit()
        self.dataFetcherThread.quit()

    @Slot(list)
    def updateWidget(self, data: list):
        """更新圖表

        Args:
            data (list): 圖表更新所需數據
        """

        elapsed_time: list[float] = data[0]
        speed: list[float] = data[1]
        x_velocity: list[float] = data[2]
        y_velocity: list[float] = data[3]
        z_velocity: list[float] = data[4]
        altitude: list[float] = data[5]
        y_angle: list[float] = data[6]
        latitude_longitude: tuple[tuple[float]] = data[7]

        self.vtPlot.update_plot(elapsed_time, speed, x_velocity, y_velocity, z_velocity)
        self.htPlot.update_plot(elapsed_time, altitude)
        # self.vtkWidget.set_y_angle(y_angle)
        self.map.updateMap(latitude_longitude)
