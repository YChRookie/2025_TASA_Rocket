# view/widget/mplWidget.py

"""
QWidget（視窗元件）
└── QVBoxLayout
    └── FigureCanvas（Matplotlib 畫布）
         └── Figure（圖像容器）
             └── Axes（坐標系）

Matplotlib
│
├─ Figure（圖像容器，通常取作 fig）
│   └─ Axes（坐標系，通常取作 ax）
│       ├─ Line2D、Text、Patch（繪製的元素）
│       └─ Axis（x 軸與 y 軸）
│
└─ Backend（Qt 使用 QtAgg）
    └─ FigureCanvas ← 畫布，把 Figure 畫出來
"""

# pylint: disable=no-name-in-module, missing-module-docstring, missing-class-docstring, missing-function-docstring
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class mplWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 建立 Figure 與 Canvas
        self.figure = Figure()  # 建立圖像容器
        self.canvas = FigureCanvas(self.figure)  # 將圖像繪製至 Qt 元件上
        self.ax = self.figure.add_subplot(111)  # type:  ignore
        (self.line,) = self.ax.plot([], [])  # type:  ignore

        # 建立 Layout 並加入 Canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    @Slot(list[float], list[float])
    def update(self, x: list[float], y: list[float]):
        self.line.set_data(x, y)
        return self.line
