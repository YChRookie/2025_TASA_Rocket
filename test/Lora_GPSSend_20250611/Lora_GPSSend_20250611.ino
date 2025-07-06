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
Timer t2;
Timer bt;
Timer send;
Timer mpu6050;

//設定陀螺儀
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
MPU6050 mpu;
bool dmpReady = false;
uint8_t devStatus;
uint16_t packetSize;
uint8_t fifoBuffer[64];
Quaternion q;
VectorFloat gravity;
VectorInt16 aa,aaReal;
VectorInt16 gyro;
float ypr[3];

//設定氣壓感測器
#include <Adafruit_BMP280.h>
Adafruit_BMP280 bmp;
float Pressure = 8;
float StartPressure = 0;
float BmpHigh[5];

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
float GPSHigh[3];
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


//降落傘設定
int opentime = 5;  //降落傘馬達通電時間(ms)
byte MotorPin = 45;   //降落傘馬達腳位
int opendelay = 0;   //降落傘開啟馬達延時(ms)
int startopen = 0;
int stopopen = 0;
bool down = 0;
bool sdfwe = 0;
void setup(){
  // Serial Monitor
  Serial.begin(115200);
  
  //啟動藍芽
  SerialBT.begin("Rocket");

  //啟動lora
  //Serial1.begin(115200, SERIAL_8N1, E22_RX, E22_TX);
  pinMode(E22_AUX, INPUT);
  e22ttl.begin();
  
  //啟動i2c及陀螺儀
  Wire.begin();
  mpu.initialize();

  //啟動GPS UART
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, RXD2, TXD2);
  
  //啟動氣壓感測器
  bool status;
  status = bmp.begin(0x76);
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
  }

  

  //更改GPS更新頻率
  sendUBX(UBX_UPDATE_5HZ, sizeof(UBX_UPDATE_5HZ));

  //200ms更新GPS
  t.every(200, getgps);
  t2.every(500, getgps);

  //500ms藍芽更新
  bt.every(500, btsend);
  //進入藍芽模式
  bool btmode = 1;
  while(btmode){
    t2.update();

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
      if(incoming == "mpuset"){
        mpu.initialize();
        calibrateMPU6050Offsets(); 
        devStatus = mpu.dmpInitialize(); 

        if (devStatus == 0) {
          mpu.setDMPEnabled(true);
          dmpReady = true;
          packetSize = mpu.dmpGetFIFOPacketSize();
        } else {
          Serial.println("DMP 初始化失敗");
          ESP.restart();
        }
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
    

  }
  
  
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

  
  if (!down){
    if(millis()>startopen && !sdfwe){

      //馬達開啟
      digitalWrite(MotorPin, HIGH);
      sdfwe = 1;
    }
    if(millis()>stopopen){

      //馬達停止
      digitalWrite(MotorPin, HIGH);
    }

  }else if(starthigh+100<gps.altitude.meters() && lorasend[5]<-8){
    BmpHigh[4] = BmpHigh[3];
    BmpHigh[3] = BmpHigh[2];
    BmpHigh[2] = BmpHigh[1];
    BmpHigh[1] = BmpHigh[0];
    BmpHigh[0] = lorasend[8];
    if(BmpHigh[4]>BmpHigh[3] && BmpHigh[3]>BmpHigh[2] && BmpHigh[2]>BmpHigh[1] && BmpHigh[1]>BmpHigh[0]){
      landing();
    }
    GPSHigh[2] = GPSHigh[1];
    GPSHigh[1] = GPSHigh[0];
    GPSHigh[0] = gps.altitude.meters();
    if(GPSHigh[2]>GPSHigh[1] && GPSHigh[1]>GPSHigh[0]){
      landing();
    }
  }
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
void getMPU6050() {
  if (!dmpReady) return;
  while (mpu.getFIFOCount() < packetSize);
  mpu.getFIFOBytes(fifoBuffer, packetSize);


  mpu.dmpGetQuaternion(&q, fifoBuffer);
  mpu.dmpGetGravity(&gravity, &q);
  mpu.dmpGetAccel(&aa, fifoBuffer);


  mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);//線性加速度
  mpu.dmpGetYawPitchRoll(ypr, &q, &gravity); //（Yaw, Pitch, Roll）
  mpu.getRotation(&gyro.x, &gyro.y, &gyro.z);//角速度
  

  lorasend[0] = ypr[2] * 180.0 / PI;
  lorasend[1] = - ypr[1] * 180.0 / PI;
  lorasend[2] = gyro.z / 131.0;

  lorasend[3] =  aaReal.x / 16384.0 * 9.8;
  lorasend[4] = -aaReal.y / 16384.0 * 9.8;
  lorasend[5] = -aaReal.z / 16384.0 * 9.8;
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

void btsend(){
  String result;
  for (int i = 0; i < 15; i++) {
    result += String(lorasend[i], 5); //保留5位
    if (i < 14) {
      result += ",";
    }
  }
  SerialBT.println(result);
}

//降落傘開啟
void landing(){
  down = 1;
  startopen = millis() + opendelay;
  stopopen = startopen + opentime;
}

//初始化mpu6050
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
  Serial.print(-ax); Serial.print(", ");
  Serial.print(-ay); Serial.print(", ");
  Serial.println(-az);

  Serial.print("Gyro Offset: ");
  Serial.print(-gx); Serial.print(", ");
  Serial.print(-gy); Serial.print(", ");
  Serial.println(-gz);
}