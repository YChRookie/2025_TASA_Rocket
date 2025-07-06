


#include "Arduino.h"
#include "LoRa_E22.h"

LoRa_E22 e22ttl(&Serial1, 18, 23, 19); //  RX AUX M0 M1
#define E22_TX 26
#define E22_RX 25
#define ENABLE_RSSI true

void setup() {
  delay(1000);
  Serial.begin(115200);
  Serial1.begin(9600, SERIAL_8N1, E22_RX, E22_TX);
  e22ttl.begin();
  ResponseStructContainer c;
	c = e22ttl.getConfiguration();
  Configuration configuration = *(Configuration*) c.data;

  
  // 印出設定狀態
  //Serial.println(rs.getResponseDescription());
  //printParameters(configuration);
  ResponseStructContainer cMi;
	cMi = e22ttl.getModuleInformation();
	// It's important get information pointer before all other operation
	ModuleInformation mi = *(ModuleInformation*)cMi.data;

	// Serial.println(cMi.status.getResponseDescription());
	// Serial.println(cMi.status.code);

	c.close();
	cMi.close();
  //printModuleInformation(mi);
}

void loop() {
  if (e22ttl.available() > 0) {
    //Serial.println("get");
        // 接收 LoRa 傳來的二進制數據
        ResponseContainer rc = e22ttl.receiveMessage();

        if (rc.status.code != 1) {
            // Serial.println(rc.status.getResponseDescription());
        } else {
            // 取得接收的資料長度
            int dataLength = rc.data.length();
            // Serial.print("length: ");
            // Serial.print(dataLength);  // 應該是 24
            
            if (dataLength % 4 != 0) {  // 確保長度是 4 的倍數（因為 float 佔 4 bytes）
                //Serial.println("Error: Received data length is not a multiple of 4!");
                // Serial.print("Received raw data: ");
                // for (int i = 0; i < rc.data.length(); i++) {
                //     Serial.print(rc.data[i], HEX);
                //     Serial.print(" ");
                // }
              
                return;
            }

            // 計算有幾個 float
            int numFloats = dataLength / 4;

            // 建立一個 buffer 儲存二進制數據
            uint8_t buffer[dataLength];
            // Serial.print("  ");
            // Serial.println(sizeof(buffer));
            memcpy(buffer, rc.data.c_str(), dataLength);  // 轉成 byte array

            // 解析成 float 陣列
            float receivedArray[numFloats];
            memcpy(receivedArray, buffer, dataLength);  // 直接複製記憶體數據

            // 顯示收到的浮點數
            //  for (int i = 0; i < numFloats; i++) {
            // //     Serial.print("Float["); Serial.print(i); Serial.print("]: ");
            //      Serial.println(receivedArray[i], 6);
            //  }
            // Serial.print("RSSI: ");
            // Serial.println(rc.rssi);
            size_t dataSize = sizeof(receivedArray) / sizeof(receivedArray[0]);
            Serial.write((uint8_t *)receivedArray, dataSize * sizeof(int));
            // Serial.print("Received raw data: ");
            // for (int i = 0; i < rc.data.length(); i++) {
            //     Serial.print(rc.data[i], HEX);
            //     Serial.print(" ");
            // }
            // Serial.println();
    
        }
    

    }
}

