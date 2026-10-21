import sys
import os
from geopy.geocoders import Nominatim
import folium
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                               QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QLabel, QMessageBox, 
                               QTabWidget, QFormLayout)
from PyQt5 import QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView

class CityMapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Интерактивная карта: Город или Координаты")
        self.resize(1000, 750)
        
        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Создаем вкладки для выбора способа ввода
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # ==================== ВКЛАДКА 1: Поиск по городу ====================
        tab_city = QWidget()
        city_layout = QVBoxLayout(tab_city)
        
        form_city = QHBoxLayout()
        self.input_city = QLineEdit()
        self.input_city.setPlaceholderText("Например: Москва, Алматы, Париж...")
        self.input_city.returnPressed.connect(self.search_by_city)
        
        btn_city = QPushButton("Найти город")
        btn_city.clicked.connect(self.search_by_city)
        
        form_city.addWidget(QLabel("Город:"))
        form_city.addWidget(self.input_city)
        form_city.addWidget(btn_city)
        city_layout.addLayout(form_city)
        
        self.tabs.addTab(tab_city, "🌍 Поиск по названию города")
        
        # ==================== ВКЛАДКА 2: Ввод координат ====================
        tab_coords = QWidget()
        coords_layout = QVBoxLayout(tab_coords)
        
        form_coords = QFormLayout()
        self.input_lat = QLineEdit()
        self.input_lat.setPlaceholderText("Например: 55.751244")
        
        self.input_lon = QLineEdit()
        self.input_lon.setPlaceholderText("Например: 37.618423")
        
        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Например: Моя любимая точка")
        
        form_coords.addRow("Широта (Lat):", self.input_lat)
        form_coords.addRow("Долгота (Lon):", self.input_lon)
        form_coords.addRow("Название метки:", self.input_title)
        
        btn_coords = QPushButton("Показать точку по координатам")
        btn_coords.clicked.connect(self.search_by_coords)
        
        coords_layout.addLayout(form_coords)
        coords_layout.addWidget(btn_coords)
        
        self.tabs.addTab(tab_coords, "📍 Добавить координаты вручную")
        
        # ==================== Виджет карты (Общий) ====================
        self.browser = QWebEngineView()
        main_layout.addWidget(self.browser)
        
        # Инициализируем геокодер
        self.geolocator = Nominatim(user_agent="custom_coordinate_app")
        
        # Загружаем стартовую карту (по умолчанию Астана)
        self.load_map(51.1694, 71.4491, "Астана", zoom=5)

    def search_by_city(self):
        city_name = self.input_city.text().strip()
        if not city_name:
            QMessageBox.warning(self, "Ошибка", "Введите название города!")
            return
            
        try:
            location = self.geolocator.geocode(city_name)
            if location:
                lat = location.latitude
                lon = location.longitude
                self.load_map(lat, lon, city_name.capitalize(), location.address, zoom=12)
            else:
                QMessageBox.warning(self, "Не найдено", f"Город '{city_name}' не найден. Проверьте правильность написания.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить данные:\n{e}")

    def search_by_coords(self):
        try:
            # Получаем текст и заменяем запятые на точки (на случай ввода 55,75 вместо 55.75)
            lat_str = self.input_lat.text().strip().replace(',', '.')
            lon_str = self.input_lon.text().strip().replace(',', '.')
            
            if not lat_str or not lon_str:
                QMessageBox.warning(self, "Ошибка", "Заполните поля широты и долготы!")
                return
                
            lat = float(lat_str)
            lon = float(lon_str)
            
            # Проверка на корректность диапазона координат
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                QMessageBox.warning(self, "Ошибка", "Неверные координаты!\nШирота: от -90 до 90\nДолгота: от -180 до 180")
                return
                
            title = self.input_title.text().strip()
            if not title:
                title = f"Координаты: {lat}, {lon}"
                
            self.load_map(lat, lon, title, zoom=14)
            
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Широта и долгота должны быть числами!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка:\n{e}")

    def load_map(self, lat, lon, title, address="", zoom=12):
        # Создаем карту
        m = folium.Map(location=[lat, lon], zoom_start=zoom)
        
        # Формируем текст всплывающего окна
        popup_text = f"<b>{title}</b>"
        if address:
            popup_text += f"<br><small>{address}</small>"
            
        folium.Marker(
            location=[lat, lon],
            popup=popup_text,
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)
        
        # Сохраняем во временный файл и выводим во вкладке браузера
        file_path = os.path.abspath("temp_map.html")
        m.save(file_path)
        self.browser.load(QtCore.QUrl.fromLocalFile(file_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CityMapApp()
    window.show()
    sys.exit(app.exec_())
