from database_manager import DatabaseManager
from serial_manager import SerialManager


db_mgr = DatabaseManager()
ser_mgr = SerialManager(database_manager=db_mgr,
                        port='/dev/ttyUSB~',
                        baudrate=115200,
                        timeout=0.1,
                        pack_length=10)
