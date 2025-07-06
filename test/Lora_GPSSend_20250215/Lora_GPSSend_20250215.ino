#include "Arduino.h"


#include "LoRa_E22.h"
LoRa_E22 e22ttl(&Serial1, 18, 23, 19); //  RX AUX M0 M1
#define E22_TX 26
#define E22_RX 25
#define ENABLE_RSSI true
float lorasend[15] = {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1};


#include "Timer.h" 
Timer t;
Timer send;
Timer mpu6050;

//設定陀螺儀
#include <basicMPU6050.h>
basicMPU6050<> imu;
float pitch_angle,roll_angle;

//GPS設定
#include <TinyGPS++.h>
#define RXD2 16
#define TXD2 17
#define GPS_BAUD 9600
TinyGPSPlus gps;
HardwareSerial gpsSerial(2);
float gpsget[6] = {8,8,8,8,8,8};
float starthigh;
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
  
  //啟動lora
  Serial1.begin(9600, SERIAL_8N1, E22_RX, E22_TX);
  e22ttl.begin();

  //啟動GPS UART
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, RXD2, TXD2);

  //啟動陀螺儀
  delay(1000);
  Serial.println("陀螺儀校準中...");
  imu.setup();
  imu.setBias();
  Serial.println("校準完成");

  //更改GPS更新頻率
  sendUBX(UBX_UPDATE_5HZ, sizeof(UBX_UPDATE_5HZ));
  
  //取得lora設定
  ResponseStructContainer c;
	c = e22ttl.getConfiguration();
  Configuration configuration = *(Configuration*) c.data;

  // 印出設定狀態
  //Serial.println(rs.getResponseDescription());
  printParameters(configuration);
  ResponseStructContainer cMi;
	cMi = e22ttl.getModuleInformation();
	// It's important get information pointer before all other operation
	ModuleInformation mi = *(ModuleInformation*)cMi.data;
	Serial.println(cMi.status.getResponseDescription());
	Serial.println(cMi.status.code);

  //關閉狀態取得
	c.close();
	cMi.close();
  printModuleInformation(mi);
  
  //200ms更新GPS
  t.every(200, getgps);
  // send.every(100, []() {
  //   sendFloatArray(lorasend, 5);
  // });
  // mpu6050.every(30,getMPU6050);
}

void loop(){
  t.update();
  send.update();
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
  sendFloatArray(lorasend, 15);
  
}

void getgps(){
  if (gps.location.isUpdated()) {
    if(a){
      starthigh = gps.altitude.meters();
      a = 0;
    }
    lorasend[6] = gps.location.lng();
    lorasend[7] = gps.location.lat();
  }
  else{

    Serial.println("GPS尚未更新");
  }
}

//發送float陣列函式
void sendFloatArray(float *arr, uint8_t len) {
    uint8_t buffer[len * 4]; // 每個 float 佔 4 bytes
    memcpy(buffer, arr, len * 4); // 將 float 陣列轉成 uint8_t 陣列
    Serial.print("length:");
    Serial.print(sizeof(buffer)); // 應該是 24
    Serial.print("    time:");
    Serial.println(millis());
    ResponseStatus rs = e22ttl.sendMessage(buffer, sizeof(buffer)); // 發送二進制資料
    //Serial.println(rs.getResponseDescription());

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




void printParameters(struct Configuration configuration) {
	Serial.println("----------------------------------------");

	Serial.print(F("HEAD : "));  Serial.print(configuration.COMMAND, HEX);Serial.print(" ");Serial.print(configuration.STARTING_ADDRESS, HEX);Serial.print(" ");Serial.println(configuration.LENGHT, HEX);
	Serial.println(F(" "));
	Serial.print(F("AddH : "));  Serial.println(configuration.ADDH, HEX);
	Serial.print(F("AddL : "));  Serial.println(configuration.ADDL, HEX);
	Serial.print(F("NetID : "));  Serial.println(configuration.NETID, HEX);
	Serial.println(F(" "));
	Serial.print(F("Chan : "));  Serial.print(configuration.CHAN, DEC); Serial.print(" -> "); Serial.println(configuration.getChannelDescription());
	Serial.println(F(" "));
	Serial.print(F("SpeedParityBit     : "));  Serial.print(configuration.SPED.uartParity, BIN);Serial.print(" -> "); Serial.println(configuration.SPED.getUARTParityDescription());
	Serial.print(F("SpeedUARTDatte     : "));  Serial.print(configuration.SPED.uartBaudRate, BIN);Serial.print(" -> "); Serial.println(configuration.SPED.getUARTBaudRateDescription());
	Serial.print(F("SpeedAirDataRate   : "));  Serial.print(configuration.SPED.airDataRate, BIN);Serial.print(" -> "); Serial.println(configuration.SPED.getAirDataRateDescription());
	Serial.println(F(" "));
	Serial.print(F("OptionSubPacketSett: "));  Serial.print(configuration.OPTION.subPacketSetting, BIN);Serial.print(" -> "); Serial.println(configuration.OPTION.getSubPacketSetting());
	Serial.print(F("OptionTranPower    : "));  Serial.print(configuration.OPTION.transmissionPower, BIN);Serial.print(" -> "); Serial.println(configuration.OPTION.getTransmissionPowerDescription());
	Serial.print(F("OptionRSSIAmbientNo: "));  Serial.print(configuration.OPTION.RSSIAmbientNoise, BIN);Serial.print(" -> "); Serial.println(configuration.OPTION.getRSSIAmbientNoiseEnable());
	Serial.println(F(" "));
	Serial.print(F("TransModeWORPeriod : "));  Serial.print(configuration.TRANSMISSION_MODE.WORPeriod, BIN);Serial.print(" -> "); Serial.println(configuration.TRANSMISSION_MODE.getWORPeriodByParamsDescription());
	Serial.print(F("TransModeTransContr: "));  Serial.print(configuration.TRANSMISSION_MODE.WORTransceiverControl, BIN);Serial.print(" -> "); Serial.println(configuration.TRANSMISSION_MODE.getWORTransceiverControlDescription());
	Serial.print(F("TransModeEnableLBT : "));  Serial.print(configuration.TRANSMISSION_MODE.enableLBT, BIN);Serial.print(" -> "); Serial.println(configuration.TRANSMISSION_MODE.getLBTEnableByteDescription());
	Serial.print(F("TransModeEnableRSSI: "));  Serial.print(configuration.TRANSMISSION_MODE.enableRSSI, BIN);Serial.print(" -> "); Serial.println(configuration.TRANSMISSION_MODE.getRSSIEnableByteDescription());
	Serial.print(F("TransModeEnabRepeat: "));  Serial.print(configuration.TRANSMISSION_MODE.enableRepeater, BIN);Serial.print(" -> "); Serial.println(configuration.TRANSMISSION_MODE.getRepeaterModeEnableByteDescription());
	Serial.print(F("TransModeFixedTrans: "));  Serial.print(configuration.TRANSMISSION_MODE.fixedTransmission, BIN);Serial.print(" -> "); Serial.println(configuration.TRANSMISSION_MODE.getFixedTransmissionDescription());


	Serial.println("----------------------------------------");
}
void printModuleInformation(struct ModuleInformation moduleInformation) {
	Serial.println("----------------------------------------");
	Serial.print(F("HEAD: "));  Serial.print(moduleInformation.COMMAND, HEX);Serial.print(" ");Serial.print(moduleInformation.STARTING_ADDRESS, HEX);Serial.print(" ");Serial.println(moduleInformation.LENGHT, DEC);

	Serial.print(F("Model no.: "));  Serial.println(moduleInformation.model, DEC);
	Serial.print(F("Version  : "));  Serial.println(moduleInformation.version, DEC);
	Serial.print(F("Features : "));  Serial.println(moduleInformation.features, BIN);
	Serial.println("----------------------------------------");

}