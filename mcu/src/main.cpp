#include <Arduino.h>

float data[9];

// 範圍上限（正負對稱或正向）
const float maxRange[9] = {
    180.0, 180.0, 51.1, 102.3, 102.3, 102.3,
    0.032767, 0.032767, 1638.3};

const unsigned long PERIOD_MS = 16000; // 16 秒週期（上下各 8 秒）
unsigned long startTime;

void setup()
{
  Serial.begin(115200);
  delay(1000);
  startTime = millis();
}

void loop()
{
  unsigned long t = (millis() - startTime) % PERIOD_MS;

  // 0~8000: 上升, 8000~16000: 下降
  float phase = (t <= PERIOD_MS / 2)
                    ? (float)t / (PERIOD_MS / 2)
                    : 1.0 - ((float)(t - PERIOD_MS / 2) / (PERIOD_MS / 2));

  for (int i = 0; i < 9; i++)
  {
    float mid = (i == 8) ? maxRange[i] / 2.0 : 0.0;
    float amp = (i == 8) ? maxRange[i] / 2.0 : maxRange[i];

    data[i] = mid + amp * phase;
  }

  // 傳送 raw binary float 資料
  Serial.write((uint8_t *)data, sizeof(float) * 9);

  // 為除錯輸出：
  // Serial.print("送出: ");
  // for (int i = 0; i < 9; i++) {
  //   Serial.print(data[i], 6);
  //   Serial.print(i < 8 ? ", " : "\n");
  // }

  delay(100); // 每 100ms 傳送一次
}
