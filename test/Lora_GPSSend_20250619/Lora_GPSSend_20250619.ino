#include "Arduino.h"

// 設定Lora
#include "LoRa_E22.h"
#define E22_M0 14
#define E22_M1 13
#define E22_AUX 12
#define E22_TX 18
#define E22_RX 17
float lorasend[15] = {1, 1, 1, 1, 1, 1, 120.9, 22.2, 1, 1, 1, 1, 1, 1, 1};
#define ENABLE_RSSI true
LoRa_E22 e22ttl(E22_RX, E22_TX, &Serial1, E22_AUX, E22_M0, E22_M1,
                UART_BPS_RATE_115200); //  RX AUX M0 M1

// Wifi設定
#include <WiFi.h>
const char *ssid = "凌焰";
const char *password = "12345678";
WiFiServer server(3333);
WiFiClient client;
char buffer[64] = {0};
int dataIndex = 0;
bool tcpmode = 1

#include "Timer.h"
    Timer t;
Timer t2;
Timer tcp;
Timer send;
Timer mpu6050;

// 設定陀螺儀
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
MPU6050 mpu;
bool dmpReady = false;
uint8_t devStatus;
uint16_t packetSize;
uint8_t fifoBuffer[64];
Quaternion q;
VectorFloat gravity;
VectorInt16 aa, aaReal;
VectorInt16 gyro;
float ypr[3];

// 設定磁場感測器
#include <HMC5883L.h>
HMC5883L mag;
// TwoWire Wire1(1);
float rawMag[3];
float magEarth[3];

// 設定氣壓感測器
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp;
float Pressure = 8;
float StartPressure = 0;
float BmpHigh[5];

// GPS設定
#include <TinyGPS++.h>
#define RXD2 21
#define TXD2 16
#define GPS_BAUD 9600
TinyGPSPlus gps;
HardwareSerial gpsSerial(2);
float gpsget[6] = {8, 8, 8, 8, 8, 8};
float starthigh = 0;
bool a = 1;
float GPSHigh[3];
const uint8_t UBX_UPDATE_5HZ[] = {
    0xB5, 0x62, // UBX header
    0x06, 0x08, // CFG-RATE
    0x06, 0x00, // Payload length (6 bytes)
    0xC8, 0x00, // Measurement Rate (200ms = 5Hz)
    0x01, 0x00, // Navigation Rate (固定 1)
    0x00, 0x00, // Time Reference (固定 0)
    0xDE, 0x6A  // Checksum (自動計算)
};
void sendUBX(const uint8_t *ubxMsg, uint8_t len) {
  gpsSerial.write(ubxMsg, len);
  gpsSerial.flush();
}

// 降落傘設定
int opentime = 5000; // 降落傘馬達通電時間(ms)
byte MotorPin = 45;  // 降落傘馬達腳位
int opendelay = 0;   // 降落傘開啟馬達延時(ms)
int startopen = 0;
int stopopen = 0;
bool down = 0;
bool sdfwe = 0;

void setup() {
  // Serial Monitor
  Serial.begin(115200);

  // 啟動wifi
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  Serial.println("WiFi AP 啟動");
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());

  // 啟動TCP Server
  server.begin();
  Serial.println("TCP server 啟動, 監聽 port 3333");

  // 啟動lora
  // Serial1.begin(115200, SERIAL_8N1, E22_RX, E22_TX);
  pinMode(E22_AUX, INPUT);
  e22ttl.begin();

  // 啟動i2c及陀螺儀
  Wire.begin();
  mpu.initialize();

  // 啟動磁場感測器
  Wire1.begin(41, 42);
  mag.initialize();

  // 啟動GPS UART
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, RXD2, TXD2);

  // 啟動氣壓感測器
  bool status;
  status = bmp.begin(0x76);
  if (!status) {
    Serial.println("氣壓感測器錯誤");
  }

  // 更改GPS更新頻率
  sendUBX(UBX_UPDATE_5HZ, sizeof(UBX_UPDATE_5HZ));

  // 200ms更新GPS
  t.every(200, getgps);
  t2.every(200, getgps);

  // wifi更新
  tcp.every(2000, wifisend);

  // 進入藍芽模式
  while (tcpmode) {

    t2.update();

    if (gpsSerial.available() > 3) {
      gps.encode(gpsSerial.read());
      gps.encode(gpsSerial.read());
      gps.encode(gpsSerial.read());
    } else if (gpsSerial.available() > 0) {
      gps.encode(gpsSerial.read());
    }

    getMPU6050();

    // 取得氣壓計算高度
    if (a == 0) {
      float i = StartPressure - bmp.readPressure();
      i = i / 12;
      lorasend[8] = i + starthigh;
      Serial.print("high: ");
      Serial.println(lorasend[8]);
    } else {
      // Serial.print("Pressure: ");
      // Serial.println(bmp.readPressure());
    }

    client = server.available();

    if (client) {

      Serial.println("有客戶端連線");
      // tcp.update();
      while (client.connected()) {
        tcp.update();
        t2.update();
        if (gpsSerial.available() > 3) {
          gps.encode(gpsSerial.read());
          gps.encode(gpsSerial.read());
          gps.encode(gpsSerial.read());
        } else if (gpsSerial.available() > 0) {
          gps.encode(gpsSerial.read());
        }
        if (client.available()) {
          String msg = client.readStringUntil('\n');
          msg.trim(); // 移除前後空白與換行

          Serial.print("收到訊息: ");
          Serial.println(msg);

          if (msg.equalsIgnoreCase("set")) {
            Serial.println("校準陀螺儀");
          } else if (msg.equalsIgnoreCase("start")) {
            Serial.println("開始記錄");

            // 關閉 WiFi
            Serial.println("關閉WiFi");
            WiFi.disconnect(true);
            WiFi.mode(WIFI_OFF);
            tcpmode = 0;
            return; // 離開 loop，因為 WiFi 已經關閉
          } else {
            Serial.println("未知指令");
          }
        }
        getMPU6050();

        // 取得氣壓計算高度
        if (a == 0) {
          float i = StartPressure - bmp.readPressure();
          i = i / 12;
          lorasend[8] = i + starthigh;
          Serial.print("high: ");
          Serial.println(lorasend[8]);
        }
      }

      client.stop();
      Serial.println("客戶端已離線");
    }
  }

  // send.every(30, []() {
  //   sendFloatArray(lorasend, 15);
  // });
  // mpu6050.every(30,getMPU6050);
}

void loop() {
  t.update();
  // send.update();
  // mpu6050.update();
  // 讀取GPS UART
  if (gpsSerial.available() > 3) {
    gps.encode(gpsSerial.read());
    gps.encode(gpsSerial.read());
    gps.encode(gpsSerial.read());
  } else if (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }
  getMPU6050(); // 更新mpu6050

  if (mag.testConnection()) {
    int16_t x, y, z;
    mag.getHeading(&x, &y, &z);
    float rawMag[3] = {(float)x, (float)y, (float)z};

    transformMagneticToEarth();
  }

  // 取得氣壓計算高度
  if (a == 0) {

    float i = StartPressure - bmp.readPressure();
    i = i / 12;
    lorasend[8] = i + starthigh;
    Serial.print("high: ");
    Serial.println(lorasend[8]);
  } else {
    // Serial.print("Pressure: ");
    Serial.println(bmp.readPressure());
  }

  sendFloatArray(lorasend, 15); // lora發送數據

  if (!down) {
    if (millis() > startopen && !sdfwe) {

      // 馬達開啟
      digitalWrite(MotorPin, HIGH);
      sdfwe = 1;
    }
    if (millis() > stopopen) {

      // 馬達停止
      digitalWrite(MotorPin, HIGH);
    }
  } else if (starthigh + 100 < gps.altitude.meters() && lorasend[5] < -8) {
    BmpHigh[4] = BmpHigh[3];
    BmpHigh[3] = BmpHigh[2];
    BmpHigh[2] = BmpHigh[1];
    BmpHigh[1] = BmpHigh[0];
    BmpHigh[0] = lorasend[8];
    if (BmpHigh[4] > BmpHigh[3] && BmpHigh[3] > BmpHigh[2] &&
        BmpHigh[2] > BmpHigh[1] && BmpHigh[1] > BmpHigh[0]) {
      landing();
    }
    GPSHigh[2] = GPSHigh[1];
    GPSHigh[1] = GPSHigh[0];
    GPSHigh[0] = gps.altitude.meters();
    if (GPSHigh[2] > GPSHigh[1] && GPSHigh[1] > GPSHigh[0]) {
      landing();
    }
  }
}

void getgps() {
  if (gps.location.isUpdated())
    &&a {
      Serial.println("取得平均高度...");
      int i = 0;
      while (i < 10) {
        while (gpsSerial.available() > 0) {
          gps.encode(gpsSerial.read());
        }
        if (gps.location.isUpdated()) {
          StartPressure = StartPressure + bmp.readPressure();
          starthigh = starthigh + gps.altitude.meters();
          i = i + 1;
        }
      }
      StartPressure = StartPressure / 10;
      starthigh = starthigh / 10;
      a = 0;
    }
  lorasend[6] = gps.location.lng();
  lorasend[7] = gps.location.lat();
}
else {
  Serial.println("GPS尚未更新");
}

// 更新MPU6050
void getMPU6050() {
  if (!dmpReady)
    return;
  while (mpu.getFIFOCount() < packetSize)
    ;
  mpu.getFIFOBytes(fifoBuffer, packetSize);

  mpu.dmpGetQuaternion(&q, fifoBuffer);
  mpu.dmpGetGravity(&gravity, &q);
  mpu.dmpGetAccel(&aa, fifoBuffer);

  mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity); // 線性加速度
  mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);     // （Yaw, Pitch, Roll）
  mpu.getRotation(&gyro.x, &gyro.y, &gyro.z);    // 角速度

  lorasend[0] = ypr[2] * 180.0 / PI;
  lorasend[1] = -ypr[1] * 180.0 / PI;
  lorasend[2] = gyro.z / 131.0;

  lorasend[3] = aaReal.x / 16384.0 * 9.8;
  lorasend[4] = -aaReal.y / 16384.0 * 9.8;
  lorasend[5] = -aaReal.z / 16384.0 * 9.8;
}

// 發送float陣列函式
void sendFloatArray(float *arr, uint8_t len) {
  if (digitalRead(E22_AUX) == HIGH) {
    uint8_t buffer[len * 4];      // 每個 float 佔 4 bytes
    memcpy(buffer, arr, len * 4); // 將 float 陣列轉成 uint8_t 陣列
    Serial.print("length:");
    Serial.print(sizeof(buffer)); // 應該是 24
    Serial.print("time:");
    Serial.println(millis());
    ResponseStatus rs =
        e22ttl.sendMessage(buffer, sizeof(buffer)); // 發送二進制資料
    // Serial.println(rs.getResponseDescription());
  } else {
    Serial.println("Err: E22忙碌中...");
  }
}

void wifisend() {
  String result;
  for (int i = 0; i < 15; i++) {
    result += String(lorasend[i], 5); // 保留5位
    if (i < 14) {
      result += ";";
    }
  }

  client.println(result);
  Serial.print("tcp發送:");
  Serial.println(result);
}

// 降落傘開啟
void landing() {
  down = 1;
  startopen = millis() + opendelay;
  stopopen = startopen + opentime;
}

// 感測磁場並計算
void transformMagneticToEarth() {
  float yaw = ypr[0];
  float pitch = ypr[1];
  float roll = ypr[2];

  float cy = cos(yaw), sy = sin(yaw);
  float cp = cos(pitch), sp = sin(pitch);
  float cr = cos(roll), sr = sin(roll);

  float dcm[3][3] = {{cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr},
                     {sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr},
                     {-sp, cp * sr, cp * cr}};

  for (int i = 0; i < 3; i++) {
    magEarth[i] =
        dcm[i][0] * rawMag[0] + dcm[i][1] * rawMag[1] + dcm[i][2] * rawMag[2];
  }
}

// 初始化mpu6050
void calibrateMPU6050Offsets() {
  Serial.println("保持靜止和水平5秒...");

  int32_t ax = 0, ay = 0, az = 0;
  int32_t gx = 0, gy = 0, gz = 0;
  const int samples = 100;

  for (int i = 0; i < samples; i++) {
    VectorInt16 a, g;
    mpu.getMotion6(&a.x, &a.y, &a.z, &g.x, &g.y, &g.z);
    ax += a.x;
    ay += a.y;
    az += a.z;
    gx += g.x;
    gy += g.y;
    gz += g.z;
    delay(50);
  }

  ax /= samples;
  ay /= samples;
  az /= samples;
  gx /= samples;
  gy /= samples;
  gz /= samples;

  az -= 16384;

  mpu.setXAccelOffset(-ax);
  mpu.setYAccelOffset(-ay);
  mpu.setZAccelOffset(-az);
  mpu.setXGyroOffset(-gx);
  mpu.setYGyroOffset(-gy);
  mpu.setZGyroOffset(-gz);

  Serial.println("校正完成，設定 Offset：");
  Serial.print("Accel Offset: ");
  Serial.print(-ax);
  Serial.print(", ");
  Serial.print(-ay);
  Serial.print(", ");
  Serial.println(-az);

  Serial.print("Gyro Offset: ");
  Serial.print(-gx);
  Serial.print(", ");
  Serial.print(-gy);
  Serial.print(", ");
  Serial.println(-gz);
}