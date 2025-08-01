# ~/database/database_manager.py


# pylint: disable=C0114
import threading
import pymysql
import pymysql.cursors


class DatabaseManager:
    """資料庫管理類"""

    INIT_ORIENTATION_TABLE_SQL: str = """
    create table orientation (
        id int auto_increment primary key,
        x_angle float,
        y_angle float,
        z_angular_velocity float
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
        """初始化表"""

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

    def __get_connection(self) -> pymysql.connections.Connection:
        """取得連線"""

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

    def __get_cursor(self) -> pymysql.cursors.Cursor:
        """取得游標"""

        return self.__get_connection().cursor()

    def insert_to_table(self, table: str, columns: str, data: tuple | list):
        """插入數據至指定表與欄位

        Args:
            table (str): 表名
            columns (str): 欄位名稱
            data (tuple | list): 數據

        Raises:
            e: pymysql.Error
        """

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
        limit_count: int = 0,
    ) -> tuple:
        """從指定表與欄位取得數據

        Args:
            table (str): 表名
            columns (str): 欄位名稱
            limit_count (int): 限制查詢數量. Defaults to 0.

        Raises:
            e: pymysql.Error

        Returns:
            tuple: 資料庫返回之數據，例如：((a,), (b,), (c,), ...)
        """

        cur = self.__get_cursor()
        sql = f"select {columns} from {table} order by id asc"

        if limit_count > 0:
            sql += f" limit {limit_count}"
        try:
            cur.execute(sql)
            result = cur.fetchall()
            return result
        except pymysql.Error as e:
            raise e

    def __flatten(self, data: tuple[tuple, ...]) -> list:
        """扁平化巢狀數據

        Args:
            data (tuple[tuple, ...]): 巢狀數據，例如：((a,), (b,), (c,), ...)

        Returns:
            list: 扁平化後之數據，例如：[a, b, c]
        """

        return [item[0] for item in data]

    def get_elapsed_time(self, limit_count: int = 0) -> list:
        """取得歷經時間

        Args:
            limit_count (int): 限制查詢數量. Defaults to 0.

        Returns:
            list: 歷經時間序列，為資料庫返回之數據且經過扁平化。
        """

        data = self.__fetch_data("time_info", "elapsed_time", limit_count)
        result = self.__flatten(data)
        return result

    def get_speed(self, limit_count: int = 0) -> list:
        """取得速度

        Args:
            limit_count (int, optional): 限制數量. Defaults to 0.

        Returns:
            list: 速度序列，為資料庫返回之數據且經過扁平化。
        """

        data = self.__fetch_data("motion", "speed", limit_count)
        result = self.__flatten(data)
        return result

    def get_x_velocity(self, limit_count: int = 0) -> list:
        """取得X速度

        Args:
            limit_count (int, optional): _description_. Defaults to 0.

        Returns:
            list: _description_
        """

        data = self.__fetch_data("motion", "x_velocity", limit_count)
        result = self.__flatten(data)
        return result

    def get_y_velocity(self, limit_count: int = 0):
        data = self.__fetch_data("motion", "y_velocity", limit_count)
        result = self.__flatten(data)
        return result

    def get_z_velocity(self, limit_count: int = 0):
        data = self.__fetch_data("motion", "z_velocity", limit_count)
        result = self.__flatten(data)
        return result

    def get_altitude(self, limit_count: int = 0):
        data = self.__fetch_data("location", "altitude", limit_count)
        result = self.__flatten(data)
        return result

    def get_y_angle(self):
        cur = self.__get_cursor()
        try:
            cur.execute("select y_angle from orientation order by id desc limit 1")
            data = cur.fetchone()
            return data
        except pymysql.Error as e:
            raise e

    def get_longitude_lattitude(self, limit_count: int = 0):
        data = self.__fetch_data("location", "latitude, longitude", limit_count)
        return data

    def close_all_connections(self):
        if hasattr(self.__local, "connection") and self.__local.connection is not None:
            self.__local.connection.close()
            self.__local.connection = None
