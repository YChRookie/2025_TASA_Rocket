# # # pylint: disable=no-name-in-module, C0103
# # from PySide6.QtWidgets import QApplication


# # from controller.database_manager import DatabaseManager
# # from controller.serial_manager import SerialManager
# # from view.gui import MainWindow

# # db_mgr = DatabaseManager('localhost', 'root', 'IntScope_-2147483648~2147483647', 'sensor_data')
# # ser_mgr = SerialManager(db_mgr, '/dev/...', 115200, 0.1, 11)
# # win = MainWindow(db_mgr)
# # win.show()
# # app = QApplication()
# # app.exec()

# from PySide6.QtWidgets import QApplication
# from controller.database_manager import DatabaseManager
# from view.gui import MainWindow

# db_mgr = DatabaseManager()

# app = QApplication()
# win = MainWindow(db_mgr)
# win.show()
# app.exec()


from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QToolBar, QTabWidget, QGridLayout, QPlainTextEdit
)
from PySide6.QtGui import QAction

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PySide6 排版與樣式範例")
        self.resize(800, 600) # 設定初始視窗大小

        # 初始化 toolbar(ToolBar)
        startButton = QAction(text="開始", parent=self)
        stopButton = QAction(text="停止", parent=self)
        restartSensorButton = QAction(text="重啟感測器", parent=self)
        self.__toolBar = QToolBar(parent=self)
        self.addToolBar(self.__toolBar)
        self.__toolBar.addAction(startButton)
        self.__toolBar.addAction(stopButton)
        self.__toolBar.addAction(restartSensorButton)
        
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        # 初始化 monitor(QTabWidget)
        self.__monitor = QTabWidget()
        # 創建一個 QWidget 作為 QTabWidget 的一個頁面內容
        monitor_page_widget = QWidget() 
        self.__monitor.addTab(monitor_page_widget, "監控視圖") # 將其作為一個標籤頁

        self.__monitor_layout = QGridLayout(monitor_page_widget) # 佈局應用到這個頁面內容Widget上
        
        # 測試顏色設定
        # 修正顏色代碼並給它們一個最小尺寸，讓顏色可見
        temp1 = QWidget()
        temp1.setStyleSheet('background-color: #FF0000;') # 紅色
        temp1.setMinimumSize(100, 100) # 給個尺寸確保能看見

        temp2 = QWidget()
        temp2.setStyleSheet('background-color: #00FF00;') # 綠色
        temp2.setMinimumSize(100, 100)

        temp3 = QWidget()
        temp3.setStyleSheet('background-color: #0000FF;') # 藍色
        temp3.setMinimumSize(100, 100)

        temp4 = QWidget()
        temp4.setStyleSheet('background-color: #FFFF00;') # 黃色
        temp4.setMinimumSize(100, 100)

        self.__monitor_layout.addWidget(temp1, 0, 0)
        self.__monitor_layout.addWidget(temp2, 0, 1)
        self.__monitor_layout.addWidget(temp3, 1, 0)
        self.__monitor_layout.addWidget(temp4, 1, 1)
        
        # 如果你希望格子內部的 Widget 也能按比例拉伸
        # 可以為 QGridLayout 的行和列設定拉伸因子
        self.__monitor_layout.setRowStretch(0, 1) # 第0行拉伸因子1
        self.__monitor_layout.setRowStretch(1, 1) # 第1行拉伸因子1
        self.__monitor_layout.setColumnStretch(0, 1) # 第0列拉伸因子1
        self.__monitor_layout.setColumnStretch(1, 1) # 第1列拉伸因子1


        # 初始化 terminal(QPlainTextEdit)
        self.__terminal = QPlainTextEdit()
        self.__terminal.setStyleSheet('background-color: #333333; color: white;') # 設定終端機背景色與文字顏色

        # 套用 layout (QVBoxLayout) - 設定比例
        # monitor 佔 2 份，terminal 佔 1 份，這樣 monitor 會佔據大約 2/3 的垂直空間
        self.mainLayout.addWidget(self.__monitor, 2) 
        self.mainLayout.addWidget(self.__terminal, 1)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
