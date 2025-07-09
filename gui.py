# -- View --


from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QWidget,
    QTabWidget,
    QPlainTextEdit,
    QVBoxLayout,
    QGridLayout,
)
from PySide6.QtCore import QThread, QTimer, Slot
from PySide6.QtGui import QIcon, QAction, QFont
import os
from threading import Thread, Lock
from serial_receiver import SerialReceiver
from database.dbmgr import DBInterface
from widget.mplWidget import mplWidget
from widget.mapWidget import mapWidget
from widget.vtkWidget import vtkWidget


class Visualization(QMainWindow, Thread):
    def __init__(self, serial_ctl, database_ctl):
        super().__init__()
        self.lock = Lock()

        self.serial = serial_ctl  # 引用序列埠交互類
        self.database = database_ctl  # 引用數據庫交互類

        self.setWindowTitle("Ground Site Visualization")  # 設置主視窗標題
        self.setWindowIcon(
            # 設置圖標
            QIcon("D:\\WorkSpace\\Program\\2025_TASA_Rocket\\resources\\teamLogo2.png")
        )

        # 新增工具列
        self.toolBar = QToolBar("Main Toolbar", parent=self)

        # 建構開始監控按鈕
        self.startAction = QAction(text="開始監控", parent=self.toolBar)
        self.startAction.triggered.connect(self.start)

        # 建構停止監控按鈕
        self.stopAction = QAction(text="停止監控", parent=self.toolBar)
        self.stopAction.triggered.connect(self.stop)
        self.stopAction.setEnabled(False)  # 初始時禁用
        self.toolBar.addAction(self.stopAction)

        # 建構重啟感測器按鈕
        self.restartSensorAction = QAction(text="重啟感測器", parent=self.toolBar)
        self.restartSensorAction.triggered.connect(self.restartSensor)

        # 建構開啟降落傘按鈕
        self.restartSensorAction = QAction(text="開啟降落傘", parent=self.toolBar)
        self.restartSensorAction.triggered.connect(self.restartSensor)

        # 主視窗基底元件
        self.central_widget = QWidget(parent=self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 添加控制台
        self.terminal = QPlainTextEdit()
        font = QFont("Courier New", 14)
        self.terminal.setFont(font)
        self.terminal.setReadOnly(True)
        self.main_layout.addWidget(self.terminal)

        self.initWidgets()  # 初始化組件
        self.initTimer()  # 初始化定時器

        # 運行狀態
        self.running_flag = False
        self.start_time = None

    def initWidgets(self):
        """
        初始化工具列、標籤頁、控制台
        """

        self.tab = QTabWidget(parent=self.central_widget)  # 創建標籤頁
        self.dashBoard = QWidget(parent=self.tab)  # 創建儀表板
        self.grid_layout = QGridLayout(self.dashBoard)  # 設置布局

        self.vtWidget = mplWidget("Velocity-Time Curve", "s", "m/s")  # 創建速度-時間圖
        self.htWidget = mplWidget("Altitude-Time Curve", "s", "m")  # 創建海拔-時間圖
        self.mapWidget = mapWidget()  # 創建地圖
        self.vtkWidget = vtkWidget()  # 創建姿態圖

        # 添加組件到儀表板
        self.grid_layout.addWidget(self.vtWidget, 0, 0)
        self.grid_layout.addWidget(self.htWidget, 0, 1)
        self.grid_layout.addWidget(self.mapWidget, 1, 0)
        self.grid_layout.addWidget(self.vtkWidget, 1, 1)

        # 添加標籤頁
        self.tab.addTab(self.dashBoard, "儀錶板")
        self.tab.addTab(self.vtWidget, "速度-時間圖")
        self.tab.addTab(self.htWidget, "高度-時間圖")
        self.tab.addTab(self.mapWidget, "地圖")
        self.tab.addTab(self.vtkWidget, "火箭姿態")

        self.main_layout.addWidget(self.tab)  # 添加組件到主布局

    def initTimer(self):
        """初始化更新定時器"""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(1000)  # 每秒更新一次UI

    @Slot()
    def update(self, time, velocity, altitude, longitude, latitude):
        """
        更新V-T圖、H-T圖、地圖、3D姿態圖
        """
        if self.running_flag:
            if vtkWidget.
            self.vtWidget.updateLine(time, velocity)
            self.htWidget.updateLine(time, altitude)
            self.mapWidget.updatePosition(longitude, latitude)
        else:
            self.terminal

    @Slot()
    def start(self):
        """開始監控"""
        self.update()

    @Slot()
    def stop(self):
        """停止監控"""
        self.vtkWidget.closeEvent()

    @Slot()
    def restartSensor(self):
        """重啟感測器"""
        with self.lock:
            self.serial.restart()

    @Slot()
    def write(self, msg):
        """寫入ESP32"""
        with self.lock:
            if self.serial.is_running():
                self.serial.write(msg)
            else:
                self.terminal.appendPlainText("Serial port is not running.")
