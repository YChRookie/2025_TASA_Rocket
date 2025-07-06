#include "Arduino.h"

//設定Lora
#include "LoRa_E22.h"
#define E22_M0 14
#define E22_M1 13
#define E22_AUX 12
#define E22_TX 18
#define E22_RX 17
float lorasend[15] = {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1};
#define ENABLE_RSSI true
LoRa_E22 e22ttl(E22_RX, E22_TX, &Serial1, E22_AUX, E22_M0, E22_M1, UART_BPS_RATE_115200); //  RX AUX M0 M1

#include <BluetoothSerial.h> 
BluetoothSerial SerialBT; 

#include "Timer.h" 
Timer t;
Timer send;
Timer mpu6050;

//設定陀螺儀
#include <basicMPU6050.h>
basicMPU6050<> imu;
float pitch_angle,roll_angle;

//設定氣壓感測器
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp;
float Pressure = 8;
float StartPressure = 0;

//GPS設定
#include <TinyGPS++.h>
#define RXD2 21
#define TXD2 16
#define GPS_BAUD 9600
TinyGPSPlus gps;
HardwareSerial gpsSerial(2);
float gpsget[6] = {8,8,8,8,8,8};
float starthigh = 0;
bool a = 1;
const uint8_t UBX_UPDATE_5HZ[] = { 
  0xB5, 0x62,  // UBX header
  0x06, 0x08,  // CFG-RATE
  0x06, 0x00,  // Payload length (6 bytes)
  0xC8, 0x00,  // Measurement Rate (200ms = 5Hz)
  0x01, 0x00,  // Navigation Rate (固定 1)
  0x00, 0x00,  // Time Reference (固定 0)
  0xDE, 0x6A   // Checksum (自動計算)
};
void sendUBX(const uint8_t *ubxMsg, uint8_t len) {
    gpsSerial.write(ubxMsg, len);
  gpsSerial.flush();
}


void setup(){
  // Serial Monitor
  Serial.begin(115200);
  
  //啟動藍芽
  SerialBT.begin("Rocket");

  //啟動lora
  //Serial1.begin(115200, SERIAL_8N1, E22_RX, E22_TX);
  pinMode(E22_AUX, INPUT);
  e22ttl.begin();
  

  //啟動GPS UART
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, RXD2, TXD2);
  
  //啟動氣壓感測器
  bool status;
  status = bmp.begin(0x76);
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
  }

  //啟動陀螺儀
  delay(1000);
  Serial.println("陀螺儀校準中...");
  imu.setup();
  imu.setBias();
  Serial.println("校準完成");

  //更改GPS更新頻率
  sendUBX(UBX_UPDATE_5HZ, sizeof(UBX_UPDATE_5HZ));

  //進入藍芽模式
  bool btmode = 1;
  while(btmode){

    if(gpsSerial.available() > 3){
      gps.encode(gpsSerial.read());
      gps.encode(gpsSerial.read());
      gps.encode(gpsSerial.read());
    }
    else if(gpsSerial.available() > 0){
      gps.encode(gpsSerial.read());
    }

    if (SerialBT.available()) {
      String incoming = SerialBT.readStringUntil('\n');
      incoming.trim();
      Serial.println("收到訊息: " + incoming);

      if (incoming == "start") {
        btmode = 0;
      }
    }

    
    getMPU6050();
    //取得氣壓計算高度
    if(a==0){
      float i = StartPressure - bmp.readPressure();
      i = i/12;
      lorasend[8] = i+starthigh;
      Serial.print("high: ");
      Serial.println(lorasend[8]);
      
    }
    else{
      Serial.print("Pressure: ");
      Serial.println(bmp.readPressure());
    }
    getgps();

  }
  //200ms更新GPS
  t.every(200, getgps);
  
  // send.every(30, []() {
  //   sendFloatArray(lorasend, 15);
  // });
  // mpu6050.every(30,getMPU6050);
}

void loop(){
  t.update();
  //send.update();
  //mpu6050.update();
  //讀取GPS UART
  if(gpsSerial.available() > 3){
    gps.encode(gpsSerial.read());
    gps.encode(gpsSerial.read());
    gps.encode(gpsSerial.read());
  }
  else if(gpsSerial.available() > 0){
    gps.encode(gpsSerial.read());
  }
  getMPU6050();

  //取得氣壓計算高度
  if(a==0){
    
    float i = StartPressure - bmp.readPressure();
    i = i/12;
    lorasend[8] = i+starthigh;
    Serial.print("high: ");
    Serial.println(lorasend[8]);
  }
  else{
    Serial.print("Pressure: ");
    Serial.println(bmp.readPressure());
  }
  
  

  sendFloatArray(lorasend, 15);
}

void getgps(){
  if (gps.location.isUpdated()) {
    if(a){
      Serial.println("取得平均高度...");
      int i = 0;
      while(i<10){
        while (gpsSerial.available() > 0) {
          gps.encode(gpsSerial.read());
        }
        if (gps.location.isUpdated()) {
          StartPressure = StartPressure + bmp.readPressure();
          starthigh = starthigh + gps.altitude.meters();
          i=i+1;
        }
        

      }
      StartPressure = StartPressure/10;
      starthigh = starthigh/10;
      a = 0;
    }
    lorasend[6] = gps.location.lng();
    lorasend[7] = gps.location.lat();
  }
  else{

    Serial.println("GPS尚未更新");
  }
}

//更新MPU6050
void getMPU6050(){

  imu.updateBias();
  lorasend[3] = imu.gx();
  lorasend[4] = imu.gy();
  lorasend[5] = imu.gz();
  lorasend[0] = atan2(imu.ay(),imu.az())*180/3.14159264;
  lorasend[1] = atan2(imu.ax(),imu.az())*180/3.14159264;
  lorasend[2] = imu.az();
  Serial.println(lorasend[0]);
  Serial.println(lorasend[1]);
}

//發送float陣列函式
void sendFloatArray(float *arr, uint8_t len) {
  if(digitalRead(E22_AUX) == HIGH){
    uint8_t buffer[len * 4]; // 每個 float 佔 4 bytes
    memcpy(buffer, arr, len * 4); // 將 float 陣列轉成 uint8_t 陣列
    Serial.print("length:");
    Serial.print(sizeof(buffer)); // 應該是 24
    Serial.print("    time:");
    Serial.println(millis());
    ResponseStatus rs = e22ttl.sendMessage(buffer, sizeof(buffer)); // 發送二進制資料
    //Serial.println(rs.getResponseDescription());
  }
  else{
    Serial.println("Err: E22忙碌中...");
  }
}

