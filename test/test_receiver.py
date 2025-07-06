import serial
import struct
import time

FLOATS = 9

SER = serial.Serial(port='COM13', baudrate=115200)


def storage():
    global FLOATS
    global SER

    try:
        while True:
            if SER.in_waiting >= 36:
                DATA = struct.unpack(f'{FLOATS}f', SER.read(36))
                print(DATA)
                time.sleep(0.1)

            else:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("程式終止，關閉串口。")
        SER.close()


if __name__ == '__main__':
    storage()
