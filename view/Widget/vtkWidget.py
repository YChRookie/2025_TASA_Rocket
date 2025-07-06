from PySide6.QtWidgets import QWidget, QVBoxLayout
from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper,
    vtkActor,
    vtkRenderer,
    vtkRenderWindow
)
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import os


class vtkWidget(QWidget):
    def __init__(self, stl_path=None):
        super().__init__()

        # 設置默認STL文件路徑
        if stl_path is None:
            stl_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                    'resources', 'rocket_3d', 'Fusee.STL')

        # 確保STL文件存在
        if not os.path.exists(stl_path):
            raise FileNotFoundError(f"STL file not found: {stl_path}")

        # 初始化VTK渲染窗口
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.render_window = self.vtk_widget.GetRenderWindow()

        # 初始化渲染器
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(0.2, 0.2, 0.2)  # 設置背景色
        self.render_window.AddRenderer(self.renderer)

        # 初始化交互器
        self.interactor = self.render_window.GetInteractor()

        # 載入STL模型
        self.reader = vtkSTLReader()
        self.reader.SetFileName(stl_path)
        self.reader.Update()

        # 設置Mapper
        self.mapper = vtkPolyDataMapper()
        self.mapper.SetInputConnection(self.reader.GetOutputPort())

        # 設置Actor
        self.actor = vtkActor()
        self.actor.SetMapper(self.mapper)
        self.actor.GetProperty().SetColor(0.8, 0.8, 0.8)  # 設置模型顏色

        # 添加Actor到渲染器
        self.renderer.AddActor(self.actor)

        # 設置相機位置
        self.renderer.ResetCamera()

        # 設置布局
        layout = QVBoxLayout()
        layout.addWidget(self.vtk_widget)
        self.setLayout(layout)

        # 初始化交互器
        self.interactor.Initialize()

        # 儲存當前角度
        self.current_angles = [0, 0, 0]

    def updateModule(self, angle_x, angle_y, angle_z):
        """更新火箭模型姿態"""
        # 更新當前角度
        self.current_angles = [angle_x, angle_y, angle_z]

        # 設置模型朝向
        self.actor.SetOrientation(angle_x, angle_y, angle_z)

        # 重新渲染場景
        self.render_window.Render()

    def resetView(self):
        """重置視圖"""
        self.renderer.ResetCamera()
        self.render_window.Render()

    def closeEvent(self, event):
        """關閉事件處理"""
        # 關閉VTK交互器
        self.interactor.TerminateApp()
        super().closeEvent(event)
