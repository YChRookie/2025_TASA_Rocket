import sqlite3
from traceback import format_exception
from threading import Lock
from PySide6.QtWidgets import QPlainTextEdit


class DatabaseManager:
    """資料庫管理類"""

    def __init__(
        self,
        terminal: QPlainTextEdit | None = None,
        path: str = "D:\\WorkSpace\\Program\\2025_TASA_Rocket\\database\\data.db",
    ):
        self.__path: str = path
        self.__lock: Lock = Lock()
        self.__terminal: QPlainTextEdit = terminal

        try:
            self.__con: sqlite3.Connection = sqlite3.connect(self.__path)
            self.__cur: sqlite3.Cursor = self.__con.cursor()

            self.__terminal.appendPlainText(f"資料庫位置：{self.__path}")
            self.__terminal.appendPlainText("資料庫已建立連線")
        except sqlite3.Error as e:
            self.__log_error(e)
            self.__con.rollback()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.__log_error(exc_value)
        self.__con.close()
        self.__terminal.appendPlainText("資料庫已關閉連線")

    def __log_error(self, err: Exception) -> None:
        """輸出錯誤"""

        msg = "".join(format_exception(type(err), err, err.__traceback__))

        if self.__terminal:
            self.__terminal.appendPlainText(msg)
        else:
            print(msg)

    def init_table(self) -> None:
        """初始化各表"""

        init_orientations = """
        create table orientations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            x_angle double,
            y_angle double,
            z_angle double
        )
        """

        init_acceleration = """
        create table acceleration (
            x_acceleration double,
            y_acceleration double,
            z_acceleration double,
            velocity double
        )
        """

        init_coordinates = """
        create table coordinates (
            latitude double,
            longitude double
        )
        """

        init_others = """
        create table others (
        signal_strength double,
        time_stamp double
        )
        """

        try:
            with self.__lock:
                script = "\n".join(
                    [
                        init_orientations,
                        init_acceleration,
                        init_coordinates,
                        init_others,
                    ]
                )

                self.__cur.executescript(script)
                self.__con.commit()
        except sqlite3.Error as e:
            self.__log_error(e)
            self.__con.rollback()

    def insert_to_table(self, table: str, columns: str, data: tuple) -> None:
        """插入數據"""

        placeholders = ", ".join(["?"] * len(data))
        sql = f"""
        insert into {table} ({columns})
        values ({placeholders})
        """

        try:
            with self.__lock:
                self.__cur.execute(sql, data)
                self.__con.commit()
        except sqlite3.Error as e:
            self.__log_error(e)

    def __fetch_data(
        self, table: str, columns: str, limit: bool, limit_cnt: int
    ) -> list | tuple | None:
        """獲取資料"""

        sql = f"""
        select {columns}
        from {table}
        """

        if limit:
            sql += f" limit {limit_cnt}"

        try:
            with self.__lock:
                self.__cur.execute(sql)
                return self.__cur.fetchall()
        except sqlite3.Error as e:
            self.__log_error(e)

    def fetch_time_series(self, limit: bool, limit_cnt: int) -> list | tuple:
        """獲取時間"""

        return self.__fetch_data("others", "time_stamp", limit, limit_cnt)

        # if limit:
        #     sql = f"""
        #     select time
        #     from others
        #     limit {limit_cnt}
        #     """
        # else:
        #     sql = """
        #     select time
        #     from others
        #     """

        # try:
        #     with self.__lock:
        #         self.__cur.execute(sql)
        #         return self.__cur.fetchall()
        # except sqlite3.Error:
        #     self.__terminal.appendPlainText(format_exc())

    def fetch_velocity(self, limit: bool, limit_cnt: int) -> list | tuple:
        """獲取速度"""

        return self.__fetch_data("acceleration", "velocity", limit, limit_cnt)

        # if limit:
        #     sql = f"""
        #     select velocity
        #     from acceleration
        #     limit {limit_cnt}
        #     """
        # else:
        #     sql = """
        #     select velocity
        #     from acceleration
        #     """

        # try:
        #     with self.__lock:
        #         self.__cur.execute(sql)
        #         return self.__cur.fetchall()
        # except sqlite3.Error:
        #     self.__terminal.appendPlainText(format_exc())

    def fetch_angle(self, limit: bool, limit_cnt: int) -> list | tuple:
        """獲取三軸角度"""

        return self.__fetch_data("orientations", "*", limit, limit_cnt)

        # if limit:
        #     sql = f"""
        #     select *
        #     from orientations
        #     limit {limit_cnt}
        #     """
        # else:
        #     sql = """
        #     select *
        #     from orientations
        #     """

        # try:
        #     with self.__lock:
        #         self.__cur.execute(sql)
        #         return self.__cur.fetchall()
        # except sqlite3.Error:
        #     self.__terminal.appendPlainText(format_exc())

    def fetch_coordinates(self, limit: bool, limit_cnt: int) -> list | tuple:
        """獲取經緯度"""

        return self.__fetch_data("coordinates", "*", limit, limit_cnt)

        # if limit:
        #     sql = f"""
        #     select *
        #     from coordinates
        #     limit {limit_cnt}
        #     """
        # else:
        #     sql = """
        #     select *
        #     from coordinates
        #     """

        # try:
        #     with self.__lock:
        #         self.__cur.execute(sql)
        #         return self.__cur.fetchall()
        # except sqlite3.Error:
        #     self.__terminal.appendPlainText(format_exc())
