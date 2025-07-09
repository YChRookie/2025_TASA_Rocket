import struct
import time
from threading import Thread, Lock
import serial


class SerialReceiver(Thread):
    def __init__(self, database, port: str, baudrate: int, floats: int = 17):
        super().__init__()
        self.__serial: serial.Serial = serial.Serial(
            port=port, baudrate=baudrate, timeout=1
        )
        self.array_len: int = floats
        self.receive_buffer: list = []
        self.running_flag = False
        self.start_time = None
        self.prev_timestamp = None
        self.database_ctl = database()
        self.lock = Lock()

    def __parse_data(self, data):
        unpacked_array = list(struct.unpack(f"{self.array_len}f", data))
        return unpacked_array

    def receive(self):
        self.running_flag = True
        self.start()

        while self.running_flag:
            if self.__serial.in_waiting >= 68:
                with self.lock:
                    try:
                        data = self.__serial.read(68)
                        unpacked_array = self.__parse_data(data)
                        current_timestamp = unpacked_array[-1]

                        if self.prev_timestamp is None:
                            self.prev_timestamp = current_timestamp
                            continue

                        delta_time = current_timestamp - self.prev_timestamp
                        self.prev_timestamp = current_timestamp

                        row_data = unpacked_array + [delta_time]
                        self.receive_buffer.append(row_data)

                        if self.receive_buffer:
                            self.database_ctl.concat(self.receive_buffer)
                            self.receive_buffer.clear()

                    except struct.error as e:
                        print(f"[Error] Failed to unpack data: {e}")
                        self.unpack_error += 1
                    except Exception as e:
                        print(f"[Error] {e}")
            else:
                time.sleep(0.01)

        if self.receive_buffer and len(self.receive_buffer) >= 68:
            try:
                self.database_ctl.concat(self.receive_buffer)
            except Exception as e:
                print(f"[Error] Failed to write remaining data: {e}")
            finally:
                self.receive_buffer.clear()

    def stop(self):
        with self.lock:
            self.running_flag = False

            if self.is_alive():
                self.join(timeout=1)

            if self.__serial and self.serial.is_open:
                self.serial.close()

    def restart(self):
        return NotImplemented

    def write(self, msg):
        return NotImplemented

    def is_running(self):
        return self.running_flag and self.serial.is_open
