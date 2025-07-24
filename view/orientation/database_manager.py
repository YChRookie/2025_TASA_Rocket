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

    def get_y_angle(self):
        cur = self.__get_cursor()
        try:
            cur.execute("select y_angle from orientation order by id desc limit 1")
            data = cur.fetchone()
            return data
        except pymysql.Error as e:
            raise e

    def close_all_connections(self):
        if hasattr(self.__local, "connection") and self.__local.connection is not None:
            self.__local.connection.close()
            self.__local.connection = None
