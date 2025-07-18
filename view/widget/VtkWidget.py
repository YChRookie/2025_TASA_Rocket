# vtkWidget.py


# pylint: disable=no-name-in-module, missing-module-docstring, missing-class-docstring, missing-function-docstring, C0103
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QCloseEvent
from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper,
    vtkActor,
    vtkRenderer,
)
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VtkWidget(QWidget):
    def __init__(
        self,
        stlPath: str = "/media/ubuntu/Data/WorkSpace/Program/2025_TASA_Rocket_refactor/sources/model.stl",
    ):
        super().__init__()

        self.m_vtkWidget = QVTKRenderWindowInteractor(self)
        self.m_renderWindow = self.m_vtkWidget.GetRenderWindow()  # type: ignore

        # 初始化 Renderer
        self.m_renderer = vtkRenderer()
        self.m_renderer.SetBackground(0.2, 0.2, 0.2)
        self.m_renderWindow.AddRenderer(self.m_renderer)  # type: ignore

        # 初始化 Interactor
        self.m_interactor = self.m_renderWindow.GetInteractor()  # type: ignore

        # 載入 STL 模型
        self.m_reader = vtkSTLReader()
        self.m_reader.SetFileName(stlPath)
        self.m_reader.Update()  # type: ignore

        # 設置 Mapper
        self.m_mapper = vtkPolyDataMapper()
        self.m_mapper.SetInputConnection(self.m_reader.GetOutputPort())

        # 設置 Actor
        self.m_actor = vtkActor()
        self.m_actor.SetMapper(self.m_mapper)
        self.m_actor.GetProperty().SetColor(0.8, 0.8, 0.8)

        # 添加 Actor 到 Renderer
        self.m_renderer.AddActor(self.m_actor)

        # 設置 Camera 位置
        self.m_renderer.ResetCamera()

        # 設置 Layout
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.m_vtkWidget)
        self.setLayout(mainLayout)

        # 初始化 Interactor
        self.m_interactor.Initialize()  # type: ignore
        self.m_renderWindow.Render()  # type: ignore

    def updateModule(self, xyzAngle: list[float]):
        # 設置 Actor 朝向
        self.m_actor.SetOrientation(*xyzAngle)

        # 重新渲染場景
        self.m_renderWindow.Render()  # type: ignore

    def closeEvent(self, event: QCloseEvent):
        # 關閉VTK交互器
        self.m_interactor.TerminateApp()  # type: ignore
        super().closeEvent(event)
