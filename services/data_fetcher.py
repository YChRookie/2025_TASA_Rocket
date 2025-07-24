# ~/controller/data_fetcher.py


# pylint: disable=E0611, C0114, W0718
import pymysql
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from database.database_manager import DatabaseManager


class DataFetcher(QObject):
    dataReady = Signal(list)
    errorSignal = Signal(str)
    messageSignal = Signal(str)

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()

        # 引用資料庫管理器實例
        self.__db_mgr = database_manager
        self.is_fetching = False

        # 創建 QTimer，用於定期獲取數據
        self.__fetch_timer = QTimer(self)
        self.__fetch_timer.timeout.connect(self.__fetch_data_periodically)
        self.__polling_interval_ms = 100

    def __log_message(self, message: str):
        self.messageSignal.emit(f"[DataFetcher][LOG]: {message}")

    def __log_error(self, error: Exception):
        self.errorSignal.emit(f"[DataFetcher][ERROR]: {error}")

    @Slot()
    def start_fetching(self):
        if not self.is_fetching:
            self.is_fetching = True
            self.__fetch_timer.start(self.__polling_interval_ms)
            self.__log_message("[DataFetcher]: Data fetching started.")
        else:
            self.__log_message("[DataFetcher]: Data fetching is already running.")

    @Slot()
    def stop_fetching(self):
        if self.is_fetching:
            self.is_fetching = False
            self.__fetch_timer.stop()
            self.__log_message("[DataFetcher]: Data fetching stopped.")
        else:
            self.__log_message("[DataFetcher]: Data fetching is not running.")

    @Slot()
    def __fetch_data_periodically(self):
        if not self.is_fetching:
            return

        try:
            elapsed_time = self.__db_mgr.get_elapsed_time(limit_count=50)
            speed = self.__db_mgr.get_speed(limit_count=50)
            x_velocity = self.__db_mgr.get_x_velocity(limit_count=50)
            y_velocity = self.__db_mgr.get_y_velocity(limit_count=50)
            z_velocity = self.__db_mgr.get_z_velocity(limit_count=50)
            altitude = self.__db_mgr.get_altitude(limit_count=50)
            y_angle = self.__db_mgr.get_y_angle()

            latitude_longitude = self.__db_mgr.get_longitude_lattitude()

            self.dataReady.emit(
                [
                    elapsed_time,
                    speed,
                    x_velocity,
                    y_velocity,
                    z_velocity,
                    altitude,
                    y_angle,
                    latitude_longitude,
                ]
            )
            self.__log_message("[DataFetcher]: Data fetched and signal emitted.")

        except pymysql.Error as e:
            self.__log_error(e)
            self.stop_fetching()
        except Exception as e:
            self.__log_error(e)
