# # pylint: disable=no-name-in-module, C0103
# from PySide6.QtWidgets import QApplication


# from database.database_manager import DatabaseManager
# from services.serial_manager import SerialManager
# from view.gui import MainWindow


# db_mgr = DatabaseManager(
#     "localhost", "root", "IntScope_-2147483648~2147483647", "sensor_data"
# )
# ser_mgr = SerialManager(db_mgr, "/dev/...", 115200, 0.1, 11)
# win = MainWindow(db_mgr)
# win.show()
# app = QApplication()
# app.exec()


import pymysql

con = pymysql.connect(
    host="localhost",
    user="root",
    password="IntScope_-2147483648~2147483647",
    database="sakila",
)
cur = con.cursor()


# cur.execute("select country_id from city order by city_id desc")
# data = cur.fetchmany(10)
# print(data)
# print()
# print(data[0])
# print()

# for i in data:
#     print(i)

cur.execute("select city_id, country_id from city order by city_id desc")
data = cur.fetchmany(5)
print(data)
print()

con.close()