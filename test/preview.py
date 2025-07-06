from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPlainTextEdit, QToolBar, QTabWidget, QGridLayout, QLabel
from PySide6.QtCore import QTimer, QDateTime, Qt
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QAction
import sys
import os


class Visualization(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化主視窗標題、圖示
        self.setWindowTitle('地面端視覺化監控介面')

        # 嘗試設置圖標
        icon_path = icon_path = os.path.abspath("resources/teamLogo2.png")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 新增工具列
        self.toolBar = QToolBar("Main Toolbar", parent=self)
        # self.addToolBar(self.toolBar)

        # 建構開啟串口按鈕
        self.startSerialAction = QAction("開始接收數據", self)
        self.toolBar.addAction(self.startSerialAction)

        # 建構停止串口按鈕
        self.stopSerialAction = QAction("停止接收數據", self)
        self.stopSerialAction.setEnabled(False)  # 初始時禁用
        self.toolBar.addAction(self.stopSerialAction)

        # 建構重啟感測器按鈕
        self.restartSensorAction = QAction("重啟感測器", self)
        self.toolBar.addAction(self.restartSensorAction)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.initWidgets()
        self.initTimer()

    def initWidgets(self):
        self.tab = QTabWidget()
        self.dashBoard = QWidget()
        # self.dashBoard.setStyleSheet('background-color: white;')
        self.grid_layout = QGridLayout(self.dashBoard)

        # 其他 widget 初始化省略...
        self.vtWidget = QWidget()
        qss_str = 'background-color: white;'
        self.vtWidget.setStyleSheet(qss_str)

        self.htWidget = QWidget()
        self.htWidget.setStyleSheet(qss_str)

        self.mapWidget = QWidget()
        self.mapWidget.setStyleSheet(qss_str)

        self.vtkWidget = QWidget()
        self.vtkWidget.setStyleSheet(qss_str)

        self.grid_layout.addWidget(self.vtWidget, 0, 0)
        self.grid_layout.addWidget(self.htWidget, 0, 1)
        self.grid_layout.addWidget(self.mapWidget, 1, 0)
        self.grid_layout.addWidget(self.vtkWidget, 1, 1)

        self.tab.addTab(self.dashBoard, "儀錶板")
        self.tab.addTab(self.vtWidget, "速度-時間圖")
        self.tab.addTab(self.htWidget, "高度-時間圖")
        self.tab.addTab(self.mapWidget, "地圖")
        self.tab.addTab(self.vtkWidget, "火箭姿態")

        self.terminal = QPlainTextEdit()
        self.terminal.setFont(QFont("Courier New", 10))
        palette = self.terminal.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor('white'))
        palette.setColor(QPalette.ColorRole.Base, QColor('black'))
        self.terminal.setPalette(palette)
        self.terminal.setReadOnly(True)

        self.main_layout.addWidget(self.tab, stretch=3)
        self.main_layout.addWidget(self.terminal, stretch=1)

    def initTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_terminal_time)
        self.timer.start(1000)  # 每 1000 毫秒執行一次

    def update_terminal_time(self):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.terminal.appendPlainText(f"現在時間：{now}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Visualization()
    window.show()
    sys.exit(app.exec())
