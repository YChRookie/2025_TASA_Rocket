
#include "Arduino.h"
#include "LoRa_E22.h"
#include "Timer.h" 
#include <TinyGPS++.h>
LoRa_E22 e22ttl(&Serial1, 18, 23, 19); //  RX AUX M0 M1
#define E22_TX 26
#define E22_RX 25
#define ENABLE_RSSI true
Timer t;

#define RXD2 16
#define TXD2 17
#define GPS_BAUD 9600
TinyGPSPlus gps;
HardwareSerial gpsSerial(2);
float gpsget[6] = {8,8,8,8,8,8};

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

  Serial.begin(9600);
  Serial1.begin(9600, SERIAL_8N1, E22_RX, E22_TX);
  // Start Serial 2 with the defined RX and TX pins and a baud rate of 9600
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, RXD2, TXD2);
  delay(5000);
  Serial.println("Serial 2 started at 9600 baud rate");
  sendUBX(UBX_UPDATE_5HZ, sizeof(UBX_UPDATE_5HZ)); 
  e22ttl.begin();
  ResponseStructContainer c;
	c = e22ttl.getConfiguration();
  Configuration configuration = *(Configuration*) c.data;

  // 設定地址
  configuration.ADDH = 0x00;  // 高位地址
  configuration.ADDL = 0x00;  // 低位地址 (可根據需求更改)

  // 設定通道 (根據你使用的頻率)
  configuration.CHAN = 23;  // 例如 433MHz 的某個頻道

  // 設定功率
  configuration.OPTION.transmissionPower = POWER_22;  // 設定為 22dBm (最大功率)

  // 設定為 **通透模式**
  configuration.TRANSMISSION_MODE.fixedTransmission = FT_TRANSPARENT_TRANSMISSION; 

  // 儲存設定並應用
  ResponseStatus rs = e22ttl.setConfiguration(configuration, WRITE_CFG_PWR_DWN_SAVE);

  // 印出設定狀態
  Serial.println(rs.getResponseDescription());
  printParameters(configuration);
  ResponseStructContainer cMi;
	cMi = e22ttl.getModuleInformation();
	// It's important get information pointer before all other operation
	ModuleInformation mi = *(ModuleInformation*)cMi.data;

	Serial.println(cMi.status.getResponseDescription());
	Serial.println(cMi.status.code);

	c.close();
	cMi.close();
  printModuleInformation(mi);
  
  t.every(200, lorasendgps);
}

void loop(){
  t.update();
  if(gpsSerial.available() > 0){
    gps.encode(gpsSerial.read());
  }
}
void lorasendgps(){
  if (gps.location.isUpdated()) {
    // Serial.print("經度: "); 
    // Serial.println(gps.location.lng(), 6);
    // Serial.print("緯度: ");
    // Serial.println(gps.location.lat(), 6);
    // Serial.print("海拔: ");
    // Serial.println(gps.altitude.meters());
    // Serial.print("UTC時間: ");
    // Serial.println(String(gps.date.year()) + "/" + String(gps.date.month()) + "/" + String(gps.date.day()) + "," + String(gps.time.hour()) + ":" + String(gps.time.minute()) + ":" + String(gps.time.second()));
    gpsget[0] = gps.location.lng();
    gpsget[1] = gps.location.lat();
    gpsget[2] = gps.altitude.meters();
    gpsget[3] = gps.time.hour();
    gpsget[4] = gps.time.minute();
    gpsget[5] = gps.time.second();
    //sendFloatArray(gpsget, 6);
  }
  else{
    Serial.println("GPS尚未更新");
    // for(int i = 0;i <6; i++){
    //   gpsget[i] = 1.001;
    // }
    //sendFloatArray(gpsget, 6);
  }
  sendFloatArray(gpsget, 6);
}
void sendFloatArray(float *arr, uint8_t len) {
    uint8_t buffer[len * 4]; // 每個 float 佔 4 bytes
    memcpy(buffer, arr, len * 4); // 將 float 陣列轉成 uint8_t 陣列
    //Serial.print("Sending data length: ");
    //Serial.println(sizeof(buffer)); // 應該是 24
    ResponseStatus rs = e22ttl.sendMessage(buffer, sizeof(buffer)); // 發送二進制資料
    //Serial.println(rs.getResponseDescription());

}
// void lorasend(){
//   ResponseStatus rs = e22ttl.sendMessage(buffer, sizeof(buffer)); // 發送二進制資料
//   Serial.println(rs.getResponseDescription());
// }




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