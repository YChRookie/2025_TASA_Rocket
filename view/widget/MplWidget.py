# view/widget/mplWidget.py

# pylint: disable=no-name-in-module, missing-module-docstring, missing-class-docstring, missing-function-docstring, C0103
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot  # type: ignore
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class MplWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 建立 Figure 與 Canvas
        self.m_figure = Figure()
        self.m_canvas = FigureCanvas(self.m_figure)
        self.m_ax = self.m_figure.add_subplot(111)  # type: ignore

        self.m_lines: dict[str, Line2D] = {}

        # 初始化 X, Y, Z 軸速度分量的 Line2D
        (self.m_lines["x_velocity"],) = self.m_ax.plot([], [], "r-", label="X Velocity")  # type: ignore
        (self.m_lines["y_velocity"],) = self.m_ax.plot([], [], "g-", label="Y Velocity")  # type: ignore
        (self.m_lines["z_velocity"],) = self.m_ax.plot([], [], "b-", label="Z Velocity")  # type: ignore
        # 初始化速率向量 Line2D
        (self.m_lines["speed"],) = self.m_ax.plot([], [], "k--", label="Speed")  # type: ignore

        # 建立 Layout 並加入 Canvas
        m_layout = QVBoxLayout(self)
        m_layout.addWidget(self.m_canvas)
        self.setLayout(m_layout)

        # 初始化 Lable 與 Title
        self.setLabels("Time (s)", "Velocity (m/s)")
        self.setTitle("Velocity and Speed")

        # 啟用 grid
        self.m_ax.grid(True)  # type: ignore

        # 添加 legend
        self.m_ax.legend()  # type: ignore

    @Slot(list, list, list, list)
    def updatePlot(
        self,
        speed: list[float],
        xVelocity: list[float],
        yVelocity: list[float],
        zVelocity: list[float],
    ):
        # 確保數據長度一致
        num_points = min(len(speed), len(xVelocity), len(yVelocity), len(zVelocity))
        time_data = list(range(num_points))

        # 更新 Line2D 的數據
        self.m_lines["x_velocity"].set_data(time_data, xVelocity[:num_points])  # type: ignore
        self.m_lines["y_velocity"].set_data(time_data, yVelocity[:num_points])  # type: ignore  # type: ignore
        self.m_lines["z_velocity"].set_data(time_data, zVelocity[:num_points])  # type: ignore
        self.m_lines["total_speed"].set_data(  # type: ignore
            time_data, speed[:num_points]
        )

        self.m_ax.relim()  # 重新計算數據限制
        self.m_ax.autoscale_view(True, True, True)  # 自動縮放視圖

        self.m_canvas.draw()  # 重繪 Canvas

    def setTitle(self, titleString: str):
        self.m_ax.set_title(titleString)  # type: ignore
        self.m_canvas.draw()

    def setLabels(self, xLabel: str, yLabel: str):
        self.m_ax.set_xlabel(xLabel)  # type: ignore
        self.m_ax.set_ylabel(yLabel)  # type: ignore
        self.m_canvas.draw()

    def clearPlot(self):
        for line_name in self.m_lines.values():
            line_name.set_data([], [])
        self.m_canvas.draw()
