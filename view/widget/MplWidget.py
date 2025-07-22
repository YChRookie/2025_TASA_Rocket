# ~/view/widget/MplWidget.py


# pylint: disable=E0611, C0114
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Slot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class VtWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 建立 Figure 與 Canvas
        self.__figure = Figure()
        self.__canvas = FigureCanvas(self.__figure)
        self.__ax = self.__figure.add_subplot(111)

        self.__lines: dict[str, Line2D] = {}

        # 初始化 X, Y, Z 軸速度分量的 Line2D
        (self.__lines["x_velocity"],) = self.__ax.plot([], [], "r-", label="X Velocity")
        (self.__lines["y_velocity"],) = self.__ax.plot([], [], "g-", label="Y Velocity")
        (self.__lines["z_velocity"],) = self.__ax.plot([], [], "b-", label="Z Velocity")
        # 初始化速率向量 Line2D
        (self.__lines["speed"],) = self.__ax.plot([], [], "k--", label="Speed")

        # 建立 Layout 並加入 Canvas
        layout = QVBoxLayout(self)
        layout.addWidget(self.__canvas)
        self.setLayout(layout)

        # 初始化 Lable 與 Title
        self.set_labels("Time (s)", "Velocity (m/s)")

        # 啟用 grid
        self.__ax.grid(True)

        # 添加 legend
        self.__ax.legend()

    @Slot(list, list, list, list, list)
    def update_plot(
        self,
        elapsed_time: list[float],
        speed: list[float],
        x_velocity: list[float],
        y_velocity: list[float],
        z_velocity: list[float],
    ):
        # 確保數據長度一致
        num_points = min(
            len(elapsed_time),
            len(speed),
            len(x_velocity),
            len(y_velocity),
            len(z_velocity),
        )
        time_data = elapsed_time[:num_points]

        # 更新 Line2D 的數據
        self.__lines["x_velocity"].set_data(time_data, x_velocity[:num_points])
        self.__lines["y_velocity"].set_data(time_data, y_velocity[:num_points])
        self.__lines["z_velocity"].set_data(time_data, z_velocity[:num_points])
        self.__lines["speed"].set_data(time_data, speed[:num_points])

        self.__ax.relim()  # 重新計算數據限制
        self.__ax.autoscale_view(True, True, True)  # 自動縮放視圖

        self.__canvas.draw()  # 重繪 Canvas

    def set_title(self, title_string: str):
        self.__ax.set_title(title_string)
        self.__canvas.draw()

    def set_labels(self, x_label: str, y_label: str):
        self.__ax.set_xlabel(x_label)
        self.__ax.set_ylabel(y_label)
        self.__canvas.draw()

    def clear_plot(self):
        for line_name in self.__lines.values():
            line_name.set_data([], [])
        self.__canvas.draw()


class HtWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 建立 Figure 與 Canvas
        self.__figure = Figure()
        self.__canvas = FigureCanvas(self.__figure)
        self.__ax = self.__figure.add_subplot(111)

        self.__lines: dict[str, Line2D] = {}

        # 初始化海拔的 Line2D
        (self.__lines["altitude"],) = self.__ax.plot([], [], "b-", label="Altitude")

        # 建立 Layout 並加入 Canvas
        layout = QVBoxLayout(self)
        layout.addWidget(self.__canvas)
        self.setLayout(layout)

        # 初始化 Lable 與 Title
        self.set_labels("Time (s)", "Altitude (m/s)")
        self.set_title("Altitude")

        # 啟用 grid
        self.__ax.grid(True)

        # 添加 legend
        self.__ax.legend()

    @Slot(list, list)
    def update_plot(self, elapsed_time: list[float], altitude: list[float]):
        # 確保數據長度一致
        num_points = min(len(elapsed_time), len(altitude))
        time_data = elapsed_time[:num_points]

        # 更新 Line2D 的數據
        self.__lines["altitude"].set_data(time_data, altitude[:num_points])

        self.__ax.relim()  # 重新計算數據限制
        self.__ax.autoscale_view(True, True, True)  # 自動縮放視圖

        self.__canvas.draw()  # 重繪 Canvas

    def set_title(self, title_string: str):
        self.__ax.set_title(title_string)
        self.__canvas.draw()

    def set_labels(self, x_label: str, y_label: str):
        self.__ax.set_xlabel(x_label)
        self.__ax.set_ylabel(y_label)
        self.__canvas.draw()

    def clear_plot(self):
        for line_name in self.__lines.values():
            line_name.set_data([], [])
        self.__canvas.draw()
