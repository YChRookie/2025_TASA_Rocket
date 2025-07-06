# -- Model --


import sqlite3
from typing import List, Tuple, Any, Dict
from threading import Thread, Lock
import os


class DBInterface:
    def __init__(self, path: str = 'D:\\WorkSpace\\Program\\2025_TASA_Rocket\\database\\db.sql'):
        db_path = path
        self.lock = Lock()

        # 確保數據庫文件所在的目錄存在
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"創建數據庫目錄: {db_dir}")

        print(f"數據庫路徑設定為: {db_path}")

    def connect(self, path: str = 'D:\\WorkSpace\\Program\\2025_TASA_Rocket\\database\\db.sql'):
        return sqlite3.connect(path)

    def init_table(self) -> None:
        init_sql_str = '''
        CREATE TABLE IF NOT EXISTS SensorData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            angle_x REAL,
            angle_y REAL,
            angular_velocity_z REAL,
            acceleration_x REAL,
            acceleration_y REAL,
            acceleration_z REAL,
            longitude REAL,
            latitude REAL,
            altitude REAL,
            magnetic_dir_x REAL,
            magnetic_dir_y REAL,
            magnetic_dir_z REAL,
            magnetic_strength_x REAL,
            magnetic_strength_y REAL,
            magnetic_strength_z REAL,
            signal_strength REAL,
            timestamp REAL,
            time_interval REAL
        )
        '''
        with self.lock:
            con = None
            try:
                con = self.connect()
                cur = con.cursor()
                cur.execute(init_sql_str)
                con.commit()
                print("SensorData 表格已初始化或已存在。")
            except sqlite3.Error as e:
                print(f"初始化表格時發生錯誤: {e}")
                if con:
                    con.rollback()
                raise
            finally:
                if con:
                    con.close()

    def concat(self, rows: List[Tuple]) -> None:
        sql = '''
        INSERT INTO SensorData (
            angle_x, angle_y, angular_velocity_z,
            acceleration_x, acceleration_y, acceleration_z,
            longitude, latitude, altitude,
            magnetic_dir_x, magnetic_dir_y, magnetic_dir_z,
            magnetic_strength_x, magnetic_strength_y, magnetic_strength_z,
            signal_strength, timestamp, time_interval
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        with self.lock:
            con = None
            try:
                con = self.connect()
                cur = con.cursor()
                cur.executemany(sql, rows)
                con.commit()
            except sqlite3.Error as e:
                print(f"批量插入數據時發生錯誤: {e}")
                if con:
                    con.rollback()
                raise e
            finally:
                if con:
                    con.close()

    def get_column(self, column: str, limit_yn: bool = True, limit: int = 100) -> List[Any]:
        valid_columns = [
            'angle_x', 'angle_y', 'angular_velocity_z',
            'acceleration_x', 'acceleration_y', 'acceleration_z',
            'longitude', 'latitude', 'altitude',
            'magnetic_dir_x', 'magnetic_dir_y', 'magnetic_dir_z',
            'magnetic_strength_x', 'magnetic_strength_y', 'magnetic_strength_z',
            'signal_strength', 'timestamp', 'time_interval'  # 包含 time_interval
        ]

        if column not in valid_columns:
            raise ValueError(f"無效的列名: {column}")

        query = f"SELECT {column} FROM SensorData ORDER BY timestamp DESC"
        if limit_yn:
            query += f" LIMIT {limit}"

        with self.lock:
            con = None
            try:
                con = self.connect()
                cur = con.cursor()
                if limit_yn:
                    cur.execute(query, (limit,))
                else:
                    cur.execute(query)
                result = [row[0] for row in cur.fetchall()]
                # 返回逆序結果，使時間順序從早到晚
                return list(reversed(result))
            except sqlite3.Error as e:
                print(f"獲取列 '{column}' 數據時發生錯誤: {e}")
                raise e
            finally:
                if con:
                    con.close()

    def get_time_series(self, column, limit_yn, limit) -> Tuple[List[float], List[float]]:
        valid_columns = [
            'angle_x', 'angle_y', 'angular_velocity_z',
            'acceleration_x', 'acceleration_y', 'acceleration_z',
            'longitude', 'latitude', 'altitude',
            'magnetic_dir_x', 'magnetic_dir_y', 'magnetic_dir_z',
            'magnetic_strength_x', 'magnetic_strength_y', 'magnetic_strength_z',
            'signal_strength', 'time_interval'  # 'timestamp' 是時間軸本身，不作為數據列
        ]

        if column not in valid_columns:
            raise ValueError(f"無效的列名: {column}")

        if limit_yn:
            query = f'SELECT timestamp, {column} FROM SensorData ORDER BY timestamp DESC LIMIT ?'
        else:
            query = 'SELECT timestamp FROM SensorData ORDER BY timestamp DESC'

        with self.lock:
            con = None
            try:
                con = self.connect()
                cur = con.cursor()
                if limit_yn:
                    cur.execute(query, (limit,))
                else:
                    cur.execute(query)
                rows = cur.fetchall()

                # 逆序並分離時間戳和數值
                rows = list(reversed(rows))
                # 轉換為秒 (使用浮點數除法)
                timestamps = [row[0] / 1000.0 for row in rows]
                values = [row[1] for row in rows]

                return timestamps, values
            except sqlite3.Error as e:
                print(f"獲取時間序列數據時發生錯誤: {e}")
                raise e
            finally:
                if con:
                    con.close()

    def get_latest_data(self) -> Dict[str, Any]:
        sql = '''
            SELECT
                angle_x, angle_y, angular_velocity_z,
                acceleration_x, acceleration_y, acceleration_z,
                longitude, latitude, altitude,
                magnetic_dir_x, magnetic_dir_y, magnetic_dir_z,
                magnetic_strength_x, magnetic_strength_y, magnetic_strength_z,
                signal_strength, timestamp, time_interval
            FROM SensorData
            ORDER BY timestamp DESC
            LIMIT 1
        '''
        with self.lock:
            con = None
            try:
                con = self.connect()
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute(sql)
                row = cur.fetchone()

                if not row:
                    return {}

                return dict(row)
            except sqlite3.Error as e:
                print(f"獲取最新數據時發生錯誤: {e}")
                raise e
            finally:
                if con:
                    con.close()
