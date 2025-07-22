# /controller/serial_manager.py


# pylint: disable=E0611, C0114
import struct
import serial
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot, QTimer
from database.database_manager import DatabaseManager


class SerialManager(QObject):
    messageSignal: Signal = Signal(str)
    errorSignal: Signal = Signal(str)

    def __init__(
        self,
        database_manager: DatabaseManager,
        port: str,
        baudrate: int = 115200,
        timeout: float = 0.1,
        pack_length: int = 11,
    ) -> None:
        super().__init__()

        # 初始化序列埠參數
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = baudrate
        self.serial.timeout = timeout
        print(self.serial.is_open)

        # 引用資料庫管理器實例
        self.__db_mgr = database_manager
        # 標誌位，指示序列埠讀取是否正在進行
        self.is_running = False

        # 封包配置
        self.__pack_length = pack_length
        self.__pack_size = self.__pack_length * 4

        # 初始化狀態變量
        self.__first_timestamp = 0.0
        self.__previous_timestamp = 0.0
        self.__velocity: list[float] = [0.0, 0.0, 0.0]

        # 初始化計時器
        self.__read_timer = QTimer(self)
        self.__read_timer.timeout.connect(self.__read_serial_data)
        self.__polling_interval_ms = 10

    def __log_message(self, message: str):
        self.messageSignal.emit(f"[SerialManager][LOG]: {message}")

    def __log_error(self, error: Exception):
        self.errorSignal.emit(f"[SerialManager][ERROR]: {error}")

    def __parse_raw_data(self, data: bytes, mode: str = "struct") -> tuple[float, ...]:
        if mode == "struct":
            return struct.unpack(f"<{self.__pack_length}f", data)
        elif mode == "numpy":
            return tuple(np.frombuffer(data, np.float32, count=self.__pack_length))
        else:
            self.errorSignal.emit("[SerialManager][ERROR] Unknowed unpack mode.")
            raise ValueError("Unknown unpack mode.")

    @Slot()
    def start_serial_communication(self):
        try:
            if not self.serial.is_open:
                self.serial.open()
            self.is_running = True
            self.__read_timer.start(self.__polling_interval_ms)
            self.__log_message(
                f"[SerialManager]: Serial port {self.serial.port} opened and polling started."
            )
        except serial.SerialException as e:
            self.__log_error(e)
            self.is_running = False
        except Exception as e:
            self.__log_error(e)
            self.is_running = False

    @Slot()
    def stop_serial_communication(self):
        self.is_running = False
        self.__read_timer.stop()
        if self.serial.is_open:
            self.serial.close()
        self.__log_message(
            f"[SerialManager]: Serial port {self.serial.port} closed and polling stopped."
        )

    @Slot()
    def __read_serial_data(self):
        if not self.is_running or not self.serial.is_open:
            return

        try:
            while self.serial.in_waiting >= self.__pack_size:
                raw_data = self.serial.read(self.__pack_size)
                parsed = self.__parse_raw_data(raw_data)
                self.__process_packet(parsed)
        except serial.SerialException as e:
            self.__log_error(e)
            self.stop_serial_communication()
        except Exception as e:
            self.__log_error(e)

    def __process_packet(self, parsed: tuple[float, ...]):
        (
            x_angle,
            y_angle,
            z_angular_velocity,
            x_acc,
            y_acc,
            z_acc,
            lon,
            lat,
            alt,
            _,
            boot_ts,
        ) = parsed

        if not self.__first_timestamp:
            self.__first_timestamp = boot_ts / 1000
            self.__previous_timestamp = boot_ts / 1000
            return

        delta_t = (boot_ts - self.__previous_timestamp) / 1000
        elapsed = (boot_ts - self.__first_timestamp) / 1000
        self.__previous_timestamp = boot_ts

        self.__update_velocity(x_acc, y_acc, z_acc, delta_t)
        speed = self.__calculate_speed()

        self.__write_all_to_db(
            x_angle,
            y_angle,
            z_angular_velocity,
            x_acc,
            y_acc,
            z_acc,
            self.__velocity,
            speed,
            lon,
            lat,
            alt,
            boot_ts,
            elapsed,
        )

    def __update_velocity(self, x: float, y: float, z: float, dt: float):
        self.__velocity[0] += x * dt
        self.__velocity[1] += y * dt
        self.__velocity[2] += z * dt

    def __calculate_speed(self) -> float:
        v = self.__velocity
        return np.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)

    def __write_all_to_db(
        self,
        x_angle: float,
        y_angle: float,
        z_angular_velocity: float,
        x_acc: float,
        y_acc: float,
        z_acc: float,
        velocity: list[float],
        speed: float,
        lon: float,
        lat: float,
        alt: float,
        boot_ts: float,
        elapsed: float,
    ):
        self.__db_mgr.insert_to_table(
            "orientation",
            "x_angle, y_angle, z_angular_velocity, speed",
            (x_angle, y_angle, z_angular_velocity, speed),
        )

        self.__db_mgr.insert_to_table(
            "motion",
            "x_acceleration, y_acceleration, z_acceleration, x_velocity, y_velocity, z_velocity, speed",
            [x_acc, y_acc, z_acc] + velocity + [speed],
        )

        self.__db_mgr.insert_to_table(
            "location", "longitude, latitude, altitude", (lon, lat, alt)
        )

        self.__db_mgr.insert_to_table(
            "timestamp", "boot_timestamp, elapsed_time", (boot_ts, elapsed)
        )
