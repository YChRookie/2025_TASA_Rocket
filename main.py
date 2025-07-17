from controller.database_manager import DatabaseManager
from controller.serial_manager import SerialManager

db_mgr = DatabaseManager('localhost', 'root', 'IntScope_-2147483648~2147483647', 'sensor_data')
ser_mgr = SerialManager(db_mgr, '/dev/...', 115200, 0.1, 11)
