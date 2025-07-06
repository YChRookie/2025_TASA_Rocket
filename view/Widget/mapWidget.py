from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
import os


class mapWidget(QWidget):
    def __init__(self, html_path=None):
        super().__init__()

        self.browser = QWebEngineView()

        # 如果沒有提供HTML文件路徑，則創建內嵌的Leaflet地圖
        if html_path is None:
            self.browser = QWebEngineView()
            self.initializeLeafletMap()
        else:
            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl.fromLocalFile(html_path))

        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        self.setLayout(layout)

        # 存儲標記位置
        self.current_marker = None
        self.path_coords = []

    def initializeLeafletMap(self):
        """初始化Leaflet地圖"""
        # 獲取Leaflet資源路徑
        leaflet_path = r'D:\WorkSpace\Program\2025_TASA_Rocket\resources\leaflet'

        # 基本HTML模板，包含Leaflet地圖
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rocket Location</title>
            <link rel="stylesheet" href="file://{leaflet_path}/leaflet.css"/>
            <script src="file://{leaflet_path}/leaflet.js"></script>
            <style>
                body {{ margin: 0; padding: 0; }}
                #map {{ width: 100%; height: 100vh; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // 初始化地圖
                var map = L.map('map').setView([23.5, 121.0], 8);  // 台灣中心點
                
                // 添加底圖
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }}).addTo(map);
                
                // 火箭標記
                var rocketIcon = L.icon({{
                    iconUrl: 'file://{leaflet_path}/images/marker-icon.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowUrl: 'file://{leaflet_path}/images/marker-shadow.png',
                    shadowSize: [41, 41]
                }});
                
                var rocketMarker = null;
                var rocketPath = L.polyline([], {{color: 'red', weight: 3}}).addTo(map);
                
                function updateRocketPosition(lat, lng, alt) {{
                    if (rocketMarker) {{
                        map.removeLayer(rocketMarker);
                    }}
                    
                    rocketMarker = L.([lat, lng], {{icon: rocketIcon}})
                        .bindPopup('高度: ' + alt.toFixed(2) + ' 公尺<br>緯度: ' + lat.toFixed(6) + '<br>經度: ' + lng.toFixed(6))
                        .addTo(map);
                    
                    rocketPath.addLatLng([lat, lng]);
                    
                    map.panTo([lat, lng]);
                }}
            </script>
        </body>
        </html>
        '''

        self.browser.setHtml(html)

    def updatePosition(self, latitude, longitude):
        """更新火箭位置"""
        self.path_coords.append([latitude, longitude])

        js_code = f"updateRocketPosition({latitude}, {longitude});"
        self.browser.page().runJavaScript(js_code)

    def clearPath(self):
        """清除路徑"""
        self.path_coords.clear()
        self.browser.page().runJavaScript("rocketPath.setLatLngs([]);")
