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
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Slot, QThread
from view.widget.MplWidget import VtWidget, HtWidget
from view.widget.MapWidget import MapWidget
# from view.widget.VtkWidget import VtkWidget

from database.database_manager import DatabaseManager
from services.serial_manager import SerialManager
from services.data_fetcher import DataFetcher


class Window(QMainWindow):
    def __init__(self, database_manager: DatabaseManager) -> None:
        super().__init__()

        self.setup_ui()

        # 引用 DatabaseManager 實例
        self.db_mgr = database_manager

        # 實例化 SerialManager
        self.serial_manager = SerialManager(
            self.db_mgr,
            port="/dev/ttyUSB0",
            baudrate=115200,
            timeout=0.1,
            pack_length=10,
        )
        self.serial_manager.messageSignal.connect(self.logging_widget.appendPlainText)
        self.serial_manager.errorSignal.connect(self.logging_widget.appendPlainText)
        self.serial_thread = QThread()  # 實例化 serial_thread 執行緒
        self.serial_manager.moveToThread(
            self.serial_thread
        )  # 將 SerialManager 移至 serial_thread 執行緒
        self.serial_thread.started.connect(
            self.serial_manager.start_serial_communication
        )

        # 實例化 DataFetcher
        self.data_fetcher_thread = QThread()
        self.data_fetcher = DataFetcher(self.db_mgr)
        self.data_fetcher.dataReady.connect(self.update_widget)
        self.data_fetcher.messageSignal.connect(self.logging_widget.appendPlainText)
        self.data_fetcher.errorSignal.connect(self.logging_widget.appendPlainText)
        self.data_fetcher.moveToThread(self.data_fetcher_thread)
        self.data_fetcher_thread.started.connect(self.data_fetcher.start_fetching)

    def setup_ui(self):
        """初始化 UI"""

        self.setWindowTitle('161凌焰中學組 地面端監控系統')
        self.setWindowIcon(QIcon('D:\\WorkSpace\\Program\\2025_TASA_Rocket_refactor\\sources\\logo.png'))

        # 實例化並設置 tool_bar
        self.tool_bar = QToolBar(parent=self)
        self.addToolBar(self.tool_bar)
        # 實例化 QAction
        start_button = QAction(text="開始", parent=self.tool_bar)
        start_button.triggered.connect(self.start)
        stop_button = QAction(text="停止", parent=self.tool_bar)
        stop_button.triggered.connect(self.stop)
        # 設置 QAction
        self.tool_bar.addAction(start_button)
        self.tool_bar.addAction(stop_button)

        # 實例化 dashboard_widget
        self.dashboard_widget = QWidget()
        self.dashboard_layout = QGridLayout()
        self.dashboard_widget.setLayout(self.dashboard_layout)

        # 實例化 dashboard_widget 圖表元件
        self.dashboard_vt_plot = VtWidget()
        self.dashboard_vt_plot.set_title("Velocity")
        self.dashboard_ht_plot = HtWidget()
        self.dashboard_ht_plot.set_title("Altitude")
        self.dashboard_model_orientation = QWidget()  # <----- VTK
        self.dashboard_map = MapWidget()
        # 設置 dashboard_widget 圖表元件
        self.dashboard_layout.addWidget(self.dashboard_vt_plot, 0, 0)
        self.dashboard_layout.addWidget(self.dashboard_ht_plot, 0, 1)
        self.dashboard_layout.addWidget(self.dashboard_model_orientation, 1, 0)
        self.dashboard_layout.addWidget(self.dashboard_map, 1, 1)

        # 實例化 tab_widget 圖表元件
        self.vt_plot = VtWidget()
        self.vt_plot.set_title("Velocity")
        self.ht_plot = HtWidget()
        self.ht_plot.set_title("Altitude")
        self.model_orientation = QWidget()  # <----- VTK
        self.map_widget = MapWidget()

        # 設置 tab_widget
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.dashboard_widget, "DashBoard")
        self.tab_widget.addTab(self.vt_plot, "Velocity")
        self.tab_widget.addTab(self.ht_plot, "Altitude")
        self.tab_widget.addTab(self.model_orientation, "Orientation")
        self.tab_widget.addTab(self.map_widget, "Location")

        # 實例化 logging_widget 元件
        self.logging_widget = QPlainTextEdit()
        self.logging_widget.setReadOnly(True)

        # 實例化並設置 bottom_widget
        self.bottom_widget = QWidget()
        self.bottom_layout = QVBoxLayout()
        self.bottom_widget.setLayout(self.bottom_layout)
        self.setCentralWidget(self.bottom_widget)

        # 設置 tab_widget, logging_widget 佔比
        self.bottom_layout.addWidget(self.tab_widget, 3)  # Chart 布局比例 3/4
        self.bottom_layout.addWidget(self.logging_widget, 1)  # Logging 布局比例 1/4

    @Slot()
    def start(self):
        """開始讀取序列埠並更新圖表"""

        self.serial_thread.start()
        self.data_fetcher_thread.start()

    @Slot()
    def stop(self):
        """停止讀取序列埠並更新圖表"""

        self.serial_thread.quit()
        self.data_fetcher_thread.quit()

    @Slot(list)
    def update_widget(self, data: list):
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

        self.vt_plot.update_plot(
            elapsed_time, speed, x_velocity, y_velocity, z_velocity
        )
        self.dashboard_vt_plot.update_plot(
            elapsed_time, speed, x_velocity, y_velocity, z_velocity
        )

        self.ht_plot.update_plot(elapsed_time, altitude)
        self.dashboard_ht_plot.update_plot(elapsed_time, altitude)

        # self.model_orientation.set_y_angle(y_angle)
        # self.dashboard_model_orientation.set_y_angle(y_angle)

        self.map_widget.updateMap(latitude_longitude)
        self.dashboard_map.updateMap(latitude_longitude)
