from PySide6.QtCore import QObject, Signal
from controller.database_manager import DatabaseManager


class DataFetcher(QObject):
    dataReady = Signal(list)

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()

        self.__db_mgr = database_manager

    def fetch_speed(self):
        speed = self.__db_mgr.get_speed()
        self.dataReady.emit(speed)
        
    def fetch_altitude(self):
        altitude = self.__db_mgr.get_altitude()
        self.dataReady.emit(altitude)

    def fetch_xyz_angle(self):
        xyz_angle = self.__db_mgr.get_xyz_angle()
        self.dataReady.emit(*xyz_angle)
    
    def fetch_location(self):
        longitude = self.__db_mgr.get_longitude()   
        latitude

    def start(self):
        while True

"""
    def get_x_angle(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("orientation", "x_angle", limit, limit_count)

    def get_y_angle(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("orientation", "y_angle", limit, limit_count)

    def get_z_angular_velocity(
        self, limit: bool = False, limit_count: int | None = None
    ):
        return self.__fetch_data(
            "orientation", "z_angular_velocity", limit, limit_count
        )

    def get_elapsed_time(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("time_info", "elapsed_time", limit, limit_count)

    def get_speed(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("motion", "speed", limit, limit_count)

    def get_x_velocity(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("motion", "x_velocity", limit, limit_count)

    def get_y_velocity(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("motion", "y_velocity", limit, limit_count)

    def get_z_velocity(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("motion", "z_velocity", limit, limit_count)

    def get_altitude(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("location", "altitude", limit, limit_count)

    def get_longitude(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("location", "longitude", limit, limit_count)

    def get_latitude(self, limit: bool = False, limit_count: int | None = None):
        return self.__fetch_data("location", "latitude", limit, limit_count)
"""
