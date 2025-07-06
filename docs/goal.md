- 資料類設計
  - 新增行
  - 存取列
  - HDF5文件存儲
  - CSV文件存儲
- 建構地圖
  - Flask服務器
  - Leaflet框架設計
    - Polyline動態更新
    - 自訂圖標
    - 設置地圖
  - QWebEngineView接入Flask服務器
- 建構3D圖
  - Python VTK
  - 載入STL模型
  - 3D模型姿態動態更新

你的理解完全正確！C語言本身沒有「字串」這種高階型別， **字串在C語言中是用「字元陣列（`char[]`）」來實現的** ，並且**以空字元 `\0` 作為結尾**來表示這是一個字串。

---

## 用 C 語言撰寫的 ESP32 如何接收來自 Python 的字串？

當你從 Python 使用串口（如 `pyserial`）傳送字串給 ESP32 時，實際上是把字串當作一串位元（bytes）透過 UART 傳過去。

### Python 端（使用 PySerial）傳送字串

```python
import serial

ser = serial.Serial('COM3', 115200)
ser.write(b'hello_esp32\n')  # 傳送一串字串並以換行結尾
```

---

### ESP32 端（C 語言）如何接收？

ESP32 開發時常使用 ESP-IDF 或 Arduino 開發環境，兩者接收字串的方式類似。我們以 C 為主說明核心概念：

#### 一般流程

1. 配置 UART。
2. 準備一個 `char` 陣列當作緩衝區。
3. 持續監聽 UART 緩衝區，接收字元放入陣列中。
4. 碰到 `\n` 或 `\r` 或接收滿時，視為一個字串結束，加上 `\0` 做終止字元。

---

### 範例（ESP-IDF 的寫法）

```c
#define BUF_SIZE 128
uint8_t data[BUF_SIZE];

void uart_receive_task(void *arg) {
    while (1) {
        // 讀取 UART 內容
        int len = uart_read_bytes(UART_NUM_1, data, BUF_SIZE - 1, 20 / portTICK_PERIOD_MS);
        if (len > 0) {
            data[len] = '\0';  // 字串終止符
            printf("Received: %s\n", data);
  
            // 你可以在這裡解析字串
            if (strcmp((char *)data, "start\n") == 0) {
                // 啟動某個功能
            }
        }
    }
}
```

---

### 重點解析

| 元素                       | 說明                                           |
| -------------------------- | ---------------------------------------------- |
| `char[]`或 `uint8_t[]` | 作為接收緩衝區                                 |
| `\0`                     | 將接收到的資料標示為 C 字串的結尾              |
| `strcmp()`               | 用來比對指令內容，例如判斷是否收到 `"start"` |
| `uart_read_bytes()`      | ESP-IDF 的 API，可從 UART 接收資料             |

---

### 如果你用的是 Arduino 而非 ESP-IDF？

```cpp
char buffer[64];
byte i = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      buffer[i] = '\0';
      Serial.print("Received: ");
      Serial.println(buffer);
      i = 0;  // 重置索引
    } else {
      buffer[i++] = c;
      if (i >= 63) {
        buffer[63] = '\0';
        i = 0;
      }
    }
  }
}
```

---

### 小技巧

- 在 Python 傳送端的每個字串建議 **以 `\n` 結尾** ，這樣 C 可以很容易偵測結尾。
- 可以加入字首協定，如 `@CMD_START\n`、`@CMD_STOP\n`，幫助你在ESP32上解析更準確。

---

如果你想把「後端發送資料到 Leaflet 前端」這件事視為一個網絡編程問題來統計，根據資料傳輸的方式與 Leaflet 前端的整合程度，大致可以歸納出  **以下 6 種解決方案** ：

---

### **1. WebSocket 方式（推薦）**

- **傳輸通道** ：WebSocket（雙向）
- **前端接收** ：JavaScript 原生支援
- **即時性** ：高
- **Leaflet 整合** ：直接接收座標資料、更新地圖圖層

> **使用情境** ：即時定位、物件追蹤、資料流監控等

---

### **2. HTTP + AJAX 請求**

- **傳輸通道** ：HTTP（請求-回應）
- **前端接收** ：JavaScript AJAX (如 `fetch`)
- **即時性** ：中（需手動定時輪詢）
- **Leaflet 整合** ：AJAX 回傳 JSON，更新 Leaflet 地圖

> **使用情境** ：每隔幾秒更新資料即可的應用，如歷史軌跡回放

---

### **3. REST API + 前端自動輪詢**

- **傳輸通道** ：HTTP REST API（`Flask`, `FastAPI` 等）
- **前端接收** ：JavaScript 定時呼叫 API
- **即時性** ：中
- **Leaflet 整合** ：前端取資料後加到地圖上

> **使用情境** ：穩定簡單，後端與前端分離清楚

---

### **4. 後端產生完整 HTML（含 Leaflet + 靜態資料）**

- **傳輸通道** ：HTTP（傳送靜態網頁）
- **前端接收** ：直接載入靜態地圖點資料
- **即時性** ：低（需重新載入頁面）
- **Leaflet 整合** ：後端把資料寫進 HTML（如 `Jinja2` 模板）

> **使用情境** ：發佈一次性地圖報告、靜態分析報表

---

### **5. TCP/UDP 原始 Socket + 中介後端轉 HTTP/WebSocket**

- **傳輸通道** ：TCP / UDP（原始通訊）
- **前端接收** ：無法直接接收，需中介（如 `Flask`、`Node.js`）
- **即時性** ：取決於中介設計
- **Leaflet 整合** ：資料寫入共享結構，再由前端取得

> **使用情境** ：你已有嵌入式設備傳 TCP 資料，需要 Web 顯示

---

### **6. MQTT 或 ZeroMQ 等訊息佇列 + Web前端橋接**

- **傳輸通道** ：MQTT、ZeroMQ 等
- **前端接收** ：需額外橋接層（如 MQTT over WebSocket）
- **即時性** ：高
- **Leaflet 整合** ：橋接層將資料傳入 JS 並更新地圖

> **使用情境** ：IoT 裝置通訊、大規模分散式設備追蹤

---

### **總結表格**

| 方案編號 | 類型                     | 是否需中介 | 即時性 | 複雜度 | 是否推薦           |
| -------- | ------------------------ | ---------- | ------ | ------ | ------------------ |
| 1        | WebSocket                | 否         | 高     | 中     | **強烈推薦** |
| 2        | AJAX + 輪詢              | 否         | 中     | 低     | 推薦（低頻更新）   |
| 3        | REST API + 定時請求      | 否         | 中     | 中     | 推薦               |
| 4        | 後端產生靜態 HTML        | 否         | 低     | 低     | 可接受             |
| 5        | TCP/UDP + 中介轉前端協定 | 是         | 中高   | 高     | 中（嵌入式需用）   |
| 6        | MQTT / ZeroMQ            | 是         | 高     | 高     | 進階應用（IoT）    |

```sql
'''
\sql

CREATE DATABASE Prac CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE Prac;

SELECT DATABASE();

CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL
);

INSERT INTO locations (name, latitude, longitude) VALUES
    ('Taipei 101', 25.033964, 121.564468),
    ('Taipei Main Station', 25.047675, 121.517055),
    ('National Palace Museum', 25.102398, 121.548523),
    ('Kaohsiung Arena', 22.666534, 120.300152),
    ('Tainan Confucius Temple', 22.993624, 120.203392),
    ('Taichung Park', 24.144584, 120.683379),
    ('Chiang Kai-shek Memorial Hall', 25.034277, 121.521044),
    ('Alishan Forest Recreation Area', 23.508346, 120.802708),
    ('Sun Moon Lake', 23.865900, 120.916878),
    ('Keelung Miaokou Night Market', 25.128297, 121.741222),
    ('Hualien Taroko Gorge', 24.161228, 121.621216),
    ('Yilan Luodong Night Market', 24.676876, 121.765005),
    ('Penghu Central Street', 23.566667, 119.566667),
    ('Green Island Lighthouse', 22.673056, 121.493333),
    ('Kenting National Park', 21.946471, 120.800002),
    ('Fo Guang Shan Buddha Museum', 22.756111, 120.437222),
    ('Zhongli Night Market', 24.956341, 121.222478),
    ('Banqiao Station', 25.014799, 121.467196),
    ('New Taipei Yingge Ceramics Museum', 24.954121, 121.344066),
    ('Taoyuan International Airport', 25.077288, 121.232822),
    ('Lukang Old Street', 24.056093, 120.431279),
    ('Danshui Fisherman''s Wharf', 25.182239, 121.417672),
    ('Taitung Forest Park', 22.763181, 121.145799),
    ('Ximending', 25.042184, 121.507778);

SELECT * FROM locations;
'''
```

```python
con = pymysql.connect(
    host='localhost',
    port=3306,
    user='Apollo',
    password='IntScope_-2147483648~2147483647',
    database='Prac'
)


with con:
    cur = con.cursor()
    cur.execute('SELECT latitude, longitude FROM locations')
    data = cur.fetchall()

    lat_list = [row[0] for row in data]
    lon_list = [row[1] for row in data]

    print("Latitude:", lat_list)
    print("Longitude:", lon_list)
```