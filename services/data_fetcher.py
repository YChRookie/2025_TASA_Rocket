# ~/controller/data_fetcher.py


# pylint: disable=C0114, E0611, C0115
import threading
from PySide6.QtCore import QObject, Signal, Slot  # type: ignore
from database.database_manager import DatabaseManager


class DataFetcher(QObject):

    dataReady = Signal(list)

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()

        self.__db_mgr = database_manager

    @Slot()
    def start(self):
        p = threading.Thread(target=self.fetch_data)
        p.start()

    def fetch_data(self):
        speed = self.__db_mgr.get_speed()
        x_velocity = self.__db_mgr.get_x_velocity()
        y_velocity = self.__db_mgr.get_y_velocity()
        z_velocity = self.__db_mgr.get_z_velocity()
        altitude = self.__db_mgr.get_altitude()
        xy_angle = self.__db_mgr.get_xy_angle()
        self.dataReady.emit(
            [speed, x_velocity, y_velocity, z_velocity, altitude, xy_angle]
        )
