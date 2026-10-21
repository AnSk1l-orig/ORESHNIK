"""Интерактивная карта: поиск города или точки по координатам.

Карта показывается прямо в окне (tkintermapview), без PyQt и браузера.
Установка:  python -m pip install tkintermapview geopy
"""
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import tkintermapview
from geopy.geocoders import Nominatim

START_LAT, START_LON = 51.1694, 71.4491  # Астана
FLY_FRAMES = 40      # кадров в анимации перелёта
FLY_FRAME_MS = 20    # мс между кадрами (~50 кадров/с)


class CityMapApp:
    def __init__(self, root):
        self.root = root
        root.title("Интерактивная карта: Город или Координаты")
        root.geometry("1000x750")

        self.geolocator = Nominatim(user_agent="city_map_app_tk_demo", timeout=10)
        self.markers = []
        self.busy = False
        self.fly_job = None  # текущая анимация перелёта

        tabs = ttk.Notebook(root)
        tabs.pack(fill="x", padx=10, pady=(10, 5))

        # ===== Вкладка 1: город =====
        tab_city = ttk.Frame(tabs, padding=8)
        tabs.add(tab_city, text="🌍 Поиск по городу")

        ttk.Label(tab_city, text="Город:").pack(side="left")
        self.input_city = ttk.Entry(tab_city, width=50)
        self.input_city.pack(side="left", padx=5, fill="x", expand=True)
        self.input_city.bind("<Return>", lambda e: self.search_by_city())
        self.btn_city = ttk.Button(tab_city, text="Найти город", command=self.search_by_city)
        self.btn_city.pack(side="left")

        # ===== Вкладка 2: координаты =====
        tab_coords = ttk.Frame(tabs, padding=8)
        tabs.add(tab_coords, text="📍 Координаты вручную")

        ttk.Label(tab_coords, text="Широта:").pack(side="left")
        self.input_lat = ttk.Entry(tab_coords, width=12)
        self.input_lat.pack(side="left", padx=(2, 8))
        ttk.Label(tab_coords, text="Долгота:").pack(side="left")
        self.input_lon = ttk.Entry(tab_coords, width=12)
        self.input_lon.pack(side="left", padx=(2, 8))
        ttk.Label(tab_coords, text="Название:").pack(side="left")
        self.input_title = ttk.Entry(tab_coords, width=20)
        self.input_title.pack(side="left", padx=(2, 8))
        for entry in (self.input_lat, self.input_lon, self.input_title):
            entry.bind("<Return>", lambda e: self.search_by_coords())
        self.btn_coords = ttk.Button(tab_coords, text="Показать", command=self.search_by_coords)
        self.btn_coords.pack(side="left")

        # ===== Карта =====
        self.map = tkintermapview.TkinterMapView(root, corner_radius=0)
        self.map.pack(fill="both", expand=True, padx=10)
        self.map.set_position(START_LAT, START_LON)
        self.map.set_zoom(5)
        # Правый клик по карте — поставить метку в этой точке
        self.map.add_right_click_menu_command("Поставить метку здесь",
                                              self.marker_from_click, pass_coords=True)

        # ===== Нижняя панель =====
        bottom = ttk.Frame(root)
        bottom.pack(fill="x", padx=10, pady=5)
        self.status = ttk.Label(bottom, text="Готово. Правый клик по карте — поставить метку.")
        self.status.pack(side="left")
        ttk.Button(bottom, text="Очистить метки", command=self.clear_markers).pack(side="right")

    # ---------- Фоновые запросы ----------
    def run_in_background(self, func, on_done, text):
        if self.busy:
            return
        self.busy = True
        self.btn_city.config(state="disabled")
        self.btn_coords.config(state="disabled")
        self.status.config(text=text)

        def worker():
            try:
                result, error = func(), None
            except Exception as e:
                result, error = None, str(e)
            self.root.after(0, lambda: self.finish(on_done, result, error))

        threading.Thread(target=worker, daemon=True).start()

    def finish(self, on_done, result, error):
        self.busy = False
        self.btn_city.config(state="normal")
        self.btn_coords.config(state="normal")
        self.status.config(text="Готово")
        if error:
            messagebox.showerror("Ошибка", f"Не удалось получить данные:\n{error}")
        else:
            on_done(result)

    # ---------- Город ----------
    def search_by_city(self):
        city = self.input_city.get().strip()
        if not city:
            messagebox.showwarning("Ошибка", "Введите название города!")
            return

        def on_done(location):
            if not location:
                messagebox.showwarning("Не найдено", f"Город '{city}' не найден.")
                return
            title = location.address.split(",")[0]
            self.add_marker(location.latitude, location.longitude, title, location.address, 12)

        self.run_in_background(lambda: self.geolocator.geocode(city, language="ru"),
                               on_done, f"Ищу «{city}»...")

    # ---------- Координаты ----------
    def search_by_coords(self):
        lat_str = self.input_lat.get().strip().replace(",", ".")
        lon_str = self.input_lon.get().strip().replace(",", ".")
        if not lat_str or not lon_str:
            messagebox.showwarning("Ошибка", "Заполните поля широты и долготы!")
            return
        try:
            lat, lon = float(lat_str), float(lon_str)
        except ValueError:
            messagebox.showwarning("Ошибка", "Широта и долгота должны быть числами!")
            return
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            messagebox.showwarning("Ошибка",
                                   "Неверные координаты!\nШирота: от -90 до 90\nДолгота: от -180 до 180")
            return
        title = self.input_title.get().strip() or f"{lat}, {lon}"
        self.reverse_and_mark(lat, lon, title)

    def marker_from_click(self, coords):
        lat, lon = coords
        self.reverse_and_mark(round(lat, 6), round(lon, 6), None)

    def reverse_and_mark(self, lat, lon, title):
        def on_done(location):
            address = location.address if location else ""
            name = title or (address.split(",")[0] if address else f"{lat}, {lon}")
            self.add_marker(lat, lon, name, address, 14 if title else None)

        self.run_in_background(lambda: self.geolocator.reverse((lat, lon), language="ru"),
                               on_done, "Определяю адрес...")

    # ---------- Метки ----------
    def add_marker(self, lat, lon, title, address, zoom):
        for m in self.markers:  # предыдущие метки — синие
            m.marker_color_circle, m.marker_color_outside = "#1e40af", "#3b82f6"
            m.draw()
        marker = self.map.set_marker(lat, lon, text=title,
                                     command=lambda m, a=address: self.show_info(m, a))
        self.markers.append(marker)
        self.fly_to(lat, lon, zoom if zoom else self.map.zoom)
        self.status.config(text=address or title)

    # ---------- Плавный перелёт ----------
    def fly_to(self, lat, lon, zoom):
        if self.fly_job is not None:
            self.root.after_cancel(self.fly_job)
            self.fly_job = None

        start_lat, start_lon = self.map.get_position()
        start_zoom = self.map.zoom
        # Чем дальше лететь, тем сильнее «отдаляемся» в середине пути
        distance = math.hypot(lat - start_lat, lon - start_lon)
        dip = min(max(math.log2(distance + 1) * 1.5, 0), 6)

        def ease(t):  # плавный старт и плавная остановка
            return t * t * (3 - 2 * t)

        def step(frame):
            t = ease(frame / FLY_FRAMES)
            cur_zoom = start_zoom + (zoom - start_zoom) * t - dip * math.sin(math.pi * t)
            self.map.set_zoom(max(cur_zoom, 2))
            self.map.set_position(start_lat + (lat - start_lat) * t,
                                  start_lon + (lon - start_lon) * t)
            if frame < FLY_FRAMES:
                self.fly_job = self.root.after(FLY_FRAME_MS, step, frame + 1)
            else:
                self.fly_job = None

        step(1)

    def show_info(self, marker, address):
        messagebox.showinfo(marker.text, f"{address}\n\n{marker.position[0]:.6f}, {marker.position[1]:.6f}")

    def clear_markers(self):
        self.map.delete_all_marker()
        self.markers.clear()
        self.status.config(text="Метки очищены")


if __name__ == "__main__":
    root = tk.Tk()
    CityMapApp(root)
    root.mainloop()
