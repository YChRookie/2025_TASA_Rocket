#include "Arduino.h"

#define E22_M0 23
#define E22_M1 19
#define E22_AUX 18
#define E22_TX 26
#define E22_RX 25
float loraget[15] = {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1};
uint8_t buffer[sizeof(loraget)];


void setup(){
  // Serial Monitor
  Serial.begin(115200);
  
  //啟動lora
  pinMode(E22_M0, OUTPUT);
  pinMode(E22_M1, OUTPUT);
  pinMode(E22_AUX, INPUT);
  digitalWrite(E22_M0, LOW);
  digitalWrite(E22_M1, LOW);
  Serial1.begin(115200, SERIAL_8N1, E22_RX, E22_TX);
  
}

void loop(){
  Serial.println(Serial1.available());
  if (Serial1.available() >= sizeof(loraget)) {
        // 讀取二進制數據
        Serial1.readBytes(buffer, sizeof(loraget));

        // 將 uint8_t 轉回 float 陣列
        memcpy(loraget, buffer, sizeof(loraget));

        // 顯示接收到的數據
        Serial.print("收到 float 陣列: ");
        for (int i = 0; i < 3; i++) {
            Serial.print(loraget[i], 2);
            Serial.print(" ");
        }
        Serial.println();
    }
}