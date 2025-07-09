from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class mplWidget(QWidget):
    def __init__(self, chart_name, x_label="Time (s)", y_label="Value"):
        super().__init__()
        # 創建 Figure, Axes
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        # 初始化線條
        (self.line,) = self.ax.plot([], [])  # , 'b-'
        self.ax.set_title(chart_name)  # 設置標題
        self.ax.set_xlabel(x_label)  # 設置x軸標題
        self.ax.set_ylabel(y_label)  # 設置y軸標題
        self.ax.grid(True)  # 開啟網格

        # 創建FigureCanvas
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumSize()  # 設置最小尺寸

        # 添加到布局
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # 數據緩存
        self._x_data = []
        self._y_data = []

    def updateLine(self, x, y):
        """更新線圖數據"""
        # 更新數據
        if isinstance(x, list) and isinstance(y, list):
            self._x_data = x
            self._y_data = y
        else:
            # 添加新點
            self._x_data.append(x)
            self._y_data.append(y)

        # 更新線條數據
        self.line.set_data(self._x_data, self._y_data)

        # 自動調整軸範圍
        self.ax.relim()
        self.ax.autoscale_view()

        # 更新畫布
        self.fig.tight_layout()
        self.canvas.draw_idle()  # 使用 draw_idle 而不是 draw 以提高性能

    def addHorizontalLine(self, y_value, color="r", style="--", label=None):
        """添加水平參考線"""
        line = self.ax.axhline(y=y_value, color=color, linestyle=style, label=label)
        if label:
            self.ax.legend()
        self.canvas.draw_idle()
        return line

    def clearData(self):
        """清空數據"""
        self._x_data.clear()
        self._y_data.clear()
        self.line.set_data([], [])
        self.canvas.draw_idle()
