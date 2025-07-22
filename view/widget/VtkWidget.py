# ~/view/widget/VtkWidget.py


# pylint: disable=E0611, C0114
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal, Slot
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor, vtkRenderer
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class VtkWidget(QWidget):
    messageSignal = Signal(str)
    errorSignal = Signal(str)

    def __init__(self, stl_file_path: str):
        super().__init__()
        self.current_y_angle = 0.0
        self.actor = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.vtk_interactor = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_interactor)

        self.ren_win = self.vtk_interactor.GetRenderWindow()
        self.renderer = vtkRenderer()
        self.ren_win.AddRenderer(self.renderer)

        interactor_style = vtkInteractorStyleTrackballCamera()
        self.vtk_interactor.SetInteractorStyle(interactor_style)

        if stl_file_path:
            self._load_stl(stl_file_path)
        else:
            print(
                "[VtkWidget] No STL files are provided, the default model will be used."
            )
            self._create_default_sphere()

        self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.renderer.ResetCamera()

        self.vtk_interactor.Initialize()

    def _load_stl(self, file_path: str):
        reader = vtkSTLReader()
        reader.SetFileName(file_path)
        reader.Update()

        if reader.GetOutput().GetNumberOfPoints() == 0:
            self.messageSignal.emit(f"[VtkWidget] Fail to load STL file: {file_path}.")
            return

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        self.actor = vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(0.9, 0.7, 0.1)

        self.renderer.AddActor(self.actor)
        self.renderer.ResetCamera()
        self.messageSignal.emit(
            f"[VtkWidget] Successfully loaded STL file: {file_path}."
        )

    def _create_default_sphere(self):
        from vtkmodules.vtkFiltersSources import vtkSphereSource

        sphere = vtkSphereSource()
        sphere.SetRadius(10.0)
        sphere.SetPhiResolution(30)
        sphere.SetThetaResolution(30)
        sphere.Update()

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        self.actor = vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(0.8, 0.3, 0.3)

        self.renderer.AddActor(self.actor)

    @Slot(float)
    def set_y_angle(self, angle: float):
        if self.actor:
            self.actor.SetOrientation(270, angle, 0)
            self.current_y_angle = angle
            self.ren_win.Render()
        else:
            print("[VtkWidget] 無可旋轉的模型。")

    def get_current_y_angle(self) -> float:
        return self.current_y_angle

    def closeEvent(self, event):
        interactor = self.vtk_interactor.GetRenderWindow().GetInteractor()
        if interactor is not None:
            interactor.Disable()
            self.ren_win.Finalize()
            self.vtk_interactor.TerminateApp()
        super().closeEvent(event)
