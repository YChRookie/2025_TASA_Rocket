


#include "Arduino.h"
#include "LoRa_E22.h"
#define E22_TX 26
#define E22_RX 25
#define ENABLE_RSSI true
LoRa_E22 e22ttl(E22_RX, E22_TX, &Serial1, 18, 23, 19, UART_BPS_RATE_115200);

void setup() {
  delay(1000);
  Serial.begin(115200);
  e22ttl.begin();
  
}

void loop() {
  if (e22ttl.available() > 0) {
    Serial.println("get");
    Serial.println(e22ttl.available());
        // 接收 LoRa 傳來的二進制數據
        ResponseContainer rc = e22ttl.receiveMessage();

        if (rc.status.code != 1) {
            Serial.println(rc.status.getResponseDescription());
        } else {
            // 取得接收的資料長度
            int dataLength = rc.data.length();
            Serial.print("length: ");
            Serial.print(dataLength);  // 應該是 24
            
            if (dataLength % 4 != 0) {  // 確保長度是 4 的倍數（因為 float 佔 4 bytes）
                //Serial.println("Error: Received data length is not a multiple of 4!");
                Serial.print("Received raw data: ");
                for (int i = 0; i < rc.data.length(); i++) {
                    Serial.print(rc.data[i], HEX);
                    Serial.print(" ");
                }
                return;
            }
            if (dataLength != 60){
              if(dataLength != 120){
                Serial.println("error");
                //return;
              }
            }

            // 計算有幾個 float
            int numFloats = dataLength / 4;

            // 建立一個 buffer 儲存二進制數據
            uint8_t buffer[dataLength];
            Serial.print("  ");
            Serial.println(sizeof(buffer));
            memcpy(buffer, rc.data.c_str(), dataLength);  // 轉成 byte array

            // 解析成 float 陣列
            float receivedArray[numFloats];
            memcpy(receivedArray, buffer, dataLength);  // 直接複製記憶體數據

            //顯示收到的浮點數
             for (int i = 0; i < numFloats; i++) {
            //     Serial.print("Float["); Serial.print(i); Serial.print("]: ");
                 Serial.println(receivedArray[i], 6);
             }
            Serial.print("RSSI: ");
            Serial.println(rc.rssi);
            // Serial.print("Received raw data: ");
            // for (int i = 0; i < rc.data.length(); i++) {
            //     Serial.print(rc.data[i], HEX);
            //     Serial.print(" ");
            // }
            // Serial.println();
    
        }
    

    }
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

