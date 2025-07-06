import serial
import struct
import time
import pandas as pd

FLOATS = 16

# port='串口名稱'
# baudrate=波特率
SER = serial.Serial(port='COM7', baudrate=115200)

# columns=[陣列各項之意義(請以逗號隔開)]
DF = pd.DataFrame(columns=['X角度',
                           'Y角度',
                           'Z角速度',
                           'X加速度',
                           'Y加速度',
                           'Z加速度',
                           '經度',
                           '緯度',
                           '海拔',
                           '磁場方向X',
                           '磁場方向Y',
                           '磁場方向Z',
                           '磁場強度X',
                           '磁場強度Y',
                           '磁場強度Z',
                           '訊號強度'])

def storage():
    global FLOATS
    global SER
    global DF

    try:
        cnt = 1
        while True:
            if SER.in_waiting >= 64:
                DF.loc[cnt] = struct.unpack(f'{FLOATS}f', SER.read(64))
                cnt += 1
                print(DF)
                time.sleep(0.1)

            else:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("程式終止，關閉串口。")
        SER.close()


if __name__ == '__main__':
        storage()