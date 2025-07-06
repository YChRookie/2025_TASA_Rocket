#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
BLECharacteristic *pCharacteristic;
bool deviceConnected = false;
#define SERVICE_UUID        "12345678-1234-1234-1234-1234567890ab"
#define CHARACTERISTIC_UUID "abcd1234-abcd-1234-abcd-1234567890ab"
class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
  };

  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
  }
};

// 你可以自己定義UUID（建議用隨機產生的）：
#define SERVICE_UUID        "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

float lorasend[7] = {1.234567,12.34567,123.4567,1234.567,12345.67,123456.7,1234567};

void setup() {
  Serial.begin(115200);

  // BLE 初始化
  NimBLEDevice::init("凌焰");  // 你可以改成你要的藍牙名稱
  pServer = NimBLEDevice::createServer();

  NimBLEService* pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      NIMBLE_PROPERTY_NOTIFY | NIMBLE_PROPERTY_READ
                    );

  pService->start();
  NimBLEAdvertising* pAdvertising = NimBLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();
  Serial.println("BLE ready, advertising...");
}

void loop() {
  btsend();
  delay(200);
  // put your main code here, to run repeatedly:

}

void btsend() {
  String result;
  for (int i = 0; i < 15; i++) {
    result += String(lorasend[i], 5); //保留5位
    if (i < 14) {
      result += ",";
    }
  }

  // BLE 送出資料
  pCharacteristic->setValue(result.c_str());
  pCharacteristic->notify();

  Serial.println("BLE Sent: " + result);
}