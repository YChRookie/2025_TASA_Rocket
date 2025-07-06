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
  digitalWrite(E22_M0, HIGH);
  digitalWrite(E22_M1, HIGH);
  Serial1.begin(115200, SERIAL_8N1, E22_RX, E22_TX);
  
}

void loop(){
  if (Serial.available()) {
        String cmd = Serial.readStringUntil('\n');
        Serial1.println(cmd);
    }

    // 讀取 E22 回應並顯示
    if (Serial1.available()) {
        String response = Serial1.readString();
        Serial.println("E22 回應: " + response);
    }
}