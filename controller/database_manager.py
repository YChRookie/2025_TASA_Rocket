# /controller/database_manager.py


# pylint: disable=no-name-in-module, missing-module-docstring, missing-class-docstring, missing-function-docstring
import pymysql
from PySide6.QtCore import QObject, Signal
from pymysql.connections import Connection
from pymysql.cursors import Cursor


class DatabaseManager(QObject):
    messageSignal: Signal = Signal(str)
    errorSignal: Signal = Signal(str)

    INIT_MAIN_TABLE_SQL: str = """
    create table telemetry (
        id int auto_increment primary key,
        x_angle float,
        y_angle float,
        z_angular_velocity float,
        x_acceleration float,
        y_acceleration float,
        z_acceleration float,
        velocity float,
        boot_timestamp float,
        elapsed_time float,
        longitude float,
        latitude float,
        altitude float,
        signal_strength float
    )
    """

    INIT_ANGLE_TABLE_SQL: str = """
    create table orientation (
        id int auto_increment primary key,
        x_angle float,
        y_angle float,
        z_angular_velocity float,
        z_angle float
    )
    """

    INIT_ACCELERATION_TABLE_SQL: str = """
    create table motion (
        id int auto_increment primary key,
        x_acceleration float,
        y_acceleration float,
        z_acceleration float,
        x_velocity float,
        y_velocity float,
        z_velocity float,
        speed float
    )
    """

    INIT_LOCATION_TABLE_SQL: str = """
    create table location (
        id int auto_increment primary key,
        longitude float,
        latitude float,
        altitude float
    )
    """

    INIT_TIMEINFO_TABLE_SQL: str = """
    create table time_info (
        id int auto_increment primary key,
        boot_timestamp float,
        elapsed_time float
    )
    """

    def __init__(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "IntScope_-2147483648~2147483647",
        database: str = "sensor_data",
    ):
        super().__init__()

        self.__host = host
        self.__user = user
        self.__password = password
        self.__database = database

        con = None
        cur = None

        try:
            con, cur = self.__connect()
            cur.execute(DatabaseManager.INIT_MAIN_TABLE_SQL)
            cur.execute(DatabaseManager.INIT_ANGLE_TABLE_SQL)
            cur.execute(DatabaseManager.INIT_ACCELERATION_TABLE_SQL)
            cur.execute(DatabaseManager.INIT_TIMEINFO_TABLE_SQL)
            cur.execute(DatabaseManager.INIT_LOCATION_TABLE_SQL)
            con.commit()
            self.__log_message("Tables successfully initialized!")
        except pymysql.Error as e:
            self.__log_error(e)
            if con:
                con.rollback()
            raise

    def __log_message(self, message: str):
        self.messageSignal.emit(f"[DatabaseManager][LOG]: {message}")  # type: ignore

    def __log_error(self, error: Exception):
        self.errorSignal.emit(f"[DatabaseManager][ERROR]: {error}")  # type: ignore

    def __connect(self):
        try:
            connection = pymysql.connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__database,
            )
            cursor = connection.cursor()
            return (connection, cursor)
        except pymysql.Error as e:
            self.__log_error(e)
            raise

    def __close(
        self,
        con: Connection | None,  # type: ignore
        cur: Cursor | None,
    ):
        if cur:
            cur.close()
        if con:
            con.close()

    def insert_to_table(
        self, table: str, columns: str, data: tuple[float, ...] | list[float]
    ):
        con, cur = self.__connect()

        if not con or not cur:
            return

        placeholders = ", ".join(["%s"] * len(data))
        sql = f"insert into {table} ({columns}) values ({placeholders})"

        try:
            cur.execute(sql, tuple(data))
            con.commit()
            self.messageSignal.emit("Successfully written to the table!")  # type: ignore
        except pymysql.Error as e:
            self.__log_error(e)
            if con:
                con.rollback()
            raise
        finally:
            self.__close(con, cur)  # type: ignore

    def __fetch_data(
        self,
        table: str,
        columns: str,
        limit: bool = False,
        limit_count: int | None = None,
    ):
        con, cur = None, None
        try:
            con, cur = self.__connect()
            sql = f"select {columns} from {table} order by id asc"
            if limit and limit_count is not None:
                sql += f" limit {limit_count}"
            cur.execute(sql)
            data = cur.fetchall()
            self.messageSignal.emit("Successfully get data from the table")  # type: ignore
            return data
        except pymysql.Error as e:
            self.__log_error(e)
            if con:
                con.rollback()
            raise
        finally:
            self.__close(con, cur)  # type: ignore

    def get_xyz_angle(self):
        con, cur = None, None

        try:
            con, cur = self.__connect()
            cur.execute(
                "select x_angle, y_angle, z_angle from orientation desc limit 1"
            )
            return cur.fetchall()
        except pymysql.Error as e:
            self.errorSignal(f"{e}")  # type: ignore
            _ = e
        finally:
            self.__close(con, cur)  # type: ignore

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
