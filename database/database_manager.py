# ~/database/database_manager.py


# pylint: disable=C0114
import threading
import pymysql


class DatabaseManager:

    INIT_ORIENTATION_TABLE_SQL: str = """
    create table orientation (
        id int auto_increment primary key,
        x_angle float,
        y_angle float,
        z_angular_velocity float,
        z_angle float
    )
    """

    INIT_MOTION_TABLE_SQL: str = """
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
        self.__host = host
        self.__user = user
        self.__password = password
        self.__database = database
        self.__local = threading.local()

    def init_table(self):
        conn = self.__get_connection()
        cur = conn.cursor()

        try:
            cur.execute(DatabaseManager.INIT_ORIENTATION_TABLE_SQL)
            cur.execute(DatabaseManager.INIT_MOTION_TABLE_SQL)
            cur.execute(DatabaseManager.INIT_LOCATION_TABLE_SQL)
            cur.execute(DatabaseManager.INIT_TIMEINFO_TABLE_SQL)
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            raise e
        finally:
            if cur:
                cur.close()

    def __get_connection(self):
        if not hasattr(self.__local, "connection") or self.__local.connection is None:
            try:
                self.__local.connection = pymysql.connect(
                    host=self.__host,
                    user=self.__user,
                    password=self.__password,
                    database=self.__database,
                )
            except pymysql.Error as e:
                raise e

        return self.__local.connection

    def __get_cursor(self):
        return self.__get_connection().cursor()

    def insert_to_table(
        self, table: str, columns: str, data: tuple[float, ...] | list[float]
    ):
        conn = self.__get_connection()
        cur = self.__get_cursor()
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"insert into {table} ({columns}) values ({placeholders})"
        try:
            cur.execute(sql, tuple(data))
            conn.commit()
        except pymysql.Error as e:
            conn.rollback()
            raise e

    def __fetch_data(
        self,
        table: str,
        columns: str,
        limit: bool = False,
        limit_count: int | None = None,
    ):
        cur = self.__get_cursor()
        sql = f"select {columns} from {table} order by id asc"
        if limit and limit_count is not None:
            sql += f" limit {limit_count}"
        try:
            cur.execute(sql)
            data = cur.fetchall()
            return data
        except pymysql.Error as e:
            raise e

    def get_elapsed_time(self, limit: bool = False, limit_count: int | None = None):
        data = self.__fetch_data("time_info", "elapsed_time", limit, limit_count)
        result = [item[0] for item in data]
        return result

    def get_speed(self, limit: bool = False, limit_count: int | None = None):
        data = self.__fetch_data("motion", "speed", limit, limit_count)
        result = [item[0] for item in data]
        return result

    def get_x_velocity(self, limit: bool = False, limit_count: int | None = None):
        data = self.__fetch_data("motion", "x_velocity", limit, limit_count)
        result = [item[0] for item in data]
        return result

    def get_y_velocity(self, limit: bool = False, limit_count: int | None = None):
        data = self.__fetch_data("motion", "y_velocity", limit, limit_count)
        result = [item[0] for item in data]
        return result

    def get_z_velocity(self, limit: bool = False, limit_count: int | None = None):
        data = self.__fetch_data("motion", "z_velocity", limit, limit_count)
        result = [item[0] for item in data]
        return result

    def get_altitude(self, limit: bool = False, limit_count: int | None = None):
        data = self.__fetch_data("location", "altitude", limit, limit_count)
        result = [item[0] for item in data]
        return result

    def get_xy_angle(self):
        cur = self.__get_cursor()
        try:
            cur.execute(
                "select x_angle, y_angle from orientation order by id desc limit 1"
            )
            data = cur.fetchone()
            return data if data else (22.174, 120.892)
        except pymysql.Error as e:
            raise e

    def get_y_angle(self):
        cur = self.__get_cursor()
        try:
            cur.execute("select y_angle from orientation order by id desc limit 1")
            data = cur.fetchone()
            return data if data else (22.174, 120.892)
        except pymysql.Error as e:
            raise e

    def get_longitude_lattitude(
        self, limit: bool = False, limit_count: int | None = None
    ):
        data = self.__fetch_data("location", "latitude, longitude", limit, limit_count)
        return data

    def close_all_connections(self):
        if hasattr(self.__local, "connection") and self.__local.connection is not None:
            self.__local.connection.close()
            self.__local.connection = None
