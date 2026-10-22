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
ZONE_FRAMES = 30     # кадров в анимации расширения зон

# Бомбы: (название, мощность в килотоннах)
BOMBS = [
    ("Little Boy — Хиросима, 1945", 15),
    ("Fat Man — Нагасаки, 1945", 21),
    ("W76 — боеголовка Trident", 100),
    ("W87 — боеголовка Minuteman III", 300),
    ("W88 — боеголовка Trident II", 475),
    ("B83 — авиабомба США", 1200),
    ("Castle Bravo — испытание США, 1954", 15000),
    ("Царь-бомба — испытание СССР, 1961", 50000),
]
UNITS = {"кт": 1, "Мт": 1000}  # множитель для перевода в килотонны

# Зоны поражения (воздушный взрыв): радиус_км = k * мощность_кт ** p.
# Приблизительные формулы подобия, откалиброваны по данным для Хиросимы.
FIREBALL = "Огненный шар"
EFFECTS = [
    (FIREBALL, 0.068, 0.4, "#facc15", "всё внутри испаряется"),
    ("Сильная ударная волна (20 psi)", 0.243, 1 / 3, "#b91c1c", "разрушены даже бетонные здания"),
    ("Радиация (500 бэр)", 0.72, 0.19, "#16a34a", "смертельная доза для 50–90% людей"),
    ("Средняя ударная волна (5 psi)", 0.693, 1 / 3, "#6b7280", "рушатся жилые дома"),
    ("Тепловое излучение", 0.627, 0.41, "#f97316", "ожоги 3-й степени на открытом месте"),
    ("Слабая ударная волна (1 psi)", 1.906, 1 / 3, "#60a5fa", "выбиты окна, ранения стеклом"),
]


def smoothstep(t):
    """Плавный старт и плавная остановка анимации."""
    return t * t * (3 - 2 * t)


def circle_points(lat, lon, radius_km, n=64):
    """Точки окружности радиусом radius_km вокруг (lat, lon)."""
    dlat = radius_km / 111.32
    dlon = radius_km / (111.32 * max(math.cos(math.radians(lat)), 0.01))
    return [(lat + dlat * math.sin(2 * math.pi * i / n),
             lon + dlon * math.cos(2 * math.pi * i / n)) for i in range(n)]


def format_kt(kt):
    return f"{kt / 1000:g} Мт" if kt >= 1000 else f"{kt:g} кт"


class CityMapApp:
    def __init__(self, root):
        self.root = root
        root.title("Интерактивная карта: Город или Координаты")
        root.geometry("1000x750")

        self.geolocator = Nominatim(user_agent="city_map_app_tk_demo", timeout=10)
        self.markers = []
        self.busy = False
        self.fly_job = None  # текущая анимация перелёта
        self.zone_job = None  # текущая анимация зон
        self.zone_polys = []

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

        # ===== Вкладка 3: бомба =====
        tab_bomb = ttk.Frame(tabs, padding=8)
        tabs.add(tab_bomb, text="☢️ Бомба")

        ttk.Label(tab_bomb, text="Бомба:").pack(side="left")
        self.bomb_choice = ttk.Combobox(tab_bomb, values=[name for name, _ in BOMBS],
                                        state="readonly", width=36)
        self.bomb_choice.current(0)
        self.bomb_choice.pack(side="left", padx=(2, 8))
        self.bomb_choice.bind("<<ComboboxSelected>>", self.on_bomb_selected)
        ttk.Label(tab_bomb, text="Мощность:").pack(side="left")
        self.input_kt = ttk.Entry(tab_bomb, width=10)
        self.input_kt.pack(side="left", padx=(2, 2))
        self.input_kt.bind("<Return>", lambda e: self.launch())
        self.unit_choice = ttk.Combobox(tab_bomb, values=list(UNITS), state="readonly", width=4)
        self.unit_choice.pack(side="left", padx=(0, 8))
        self.set_yield(BOMBS[0][1])
        ttk.Button(tab_bomb, text="🚀 Запуск", command=self.launch).pack(side="left")
        ttk.Button(tab_bomb, text="Убрать зоны", command=self.clear_zones).pack(side="left", padx=(8, 0))

        # ===== Карта =====
        self.map = tkintermapview.TkinterMapView(root, corner_radius=0)
        self.map.pack(fill="both", expand=True, padx=10)
        self.map.set_position(START_LAT, START_LON)
        self.map.set_zoom(5)
        # Правый клик по карте — поставить метку в этой точке
        self.map.add_right_click_menu_command("Поставить метку здесь",
                                              self.marker_from_click, pass_coords=True)
        # Легенда зон поражения поверх карты (показывается после запуска)
        self.legend = tk.Frame(self.map, bg="white", bd=1, relief="solid")

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

    # ---------- Бомба ----------
    def set_yield(self, kt):
        """Подставляет мощность в поле: от 1000 кт — в мегатоннах."""
        unit = "Мт" if kt >= 1000 else "кт"
        self.unit_choice.set(unit)
        self.input_kt.delete(0, "end")
        self.input_kt.insert(0, f"{kt / UNITS[unit]:g}")

    def on_bomb_selected(self, _event=None):
        self.set_yield(BOMBS[self.bomb_choice.current()][1])

    def launch(self):
        try:
            value = float(self.input_kt.get().strip().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Ошибка", "Мощность должна быть числом!")
            return
        kt = value * UNITS[self.unit_choice.get()]
        if not (0.001 <= kt <= 100000):
            messagebox.showwarning("Ошибка", "Мощность: от 0,001 кт до 100 Мт")
            return

        if self.fly_job is not None:
            self.root.after_cancel(self.fly_job)
            self.fly_job = None
        # Цель — последняя метка, а если меток нет — центр карты
        lat, lon = self.markers[-1].position if self.markers else self.map.get_position()
        self.clear_zones()

        zones = sorted(((name, k * kt ** p, color, desc) for name, k, p, color, desc in EFFECTS),
                       key=lambda z: -z[1])  # от большой к малой, чтобы малые были сверху
        r = zones[0][1] * 1.15
        dlat = r / 111.32
        dlon = r / (111.32 * max(math.cos(math.radians(lat)), 0.01))
        self.map.fit_bounding_box((min(lat + dlat, 85), max(lon - dlon, -180)),
                                  (max(lat - dlat, -85), min(lon + dlon, 180)))

        self.flash()
        self.show_legend(kt, zones)
        self.status.config(text=f"Взрыв {format_kt(kt)} в точке {lat:.4f}, {lon:.4f}")
        self.animate_zones(lat, lon, zones, 1)

    def flash(self):
        overlay = tk.Frame(self.map, bg="white")
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.after(120, overlay.destroy)

    def animate_zones(self, lat, lon, zones, frame):
        for poly in self.zone_polys:
            poly.delete()
        self.zone_polys = []
        t = smoothstep(frame / ZONE_FRAMES)
        for name, radius, color, _ in zones:
            poly = self.map.set_polygon(circle_points(lat, lon, max(radius * t, 0.001)),
                                        fill_color=color if name == FIREBALL else "",
                                        outline_color=color, border_width=3)
            self.zone_polys.append(poly)
        if frame < ZONE_FRAMES:
            self.zone_job = self.root.after(30, self.animate_zones, lat, lon, zones, frame + 1)
        else:
            self.zone_job = None

    def show_legend(self, kt, zones):
        for widget in self.legend.winfo_children():
            widget.destroy()
        tk.Label(self.legend, text=f"☢️ {format_kt(kt)}", bg="white",
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=(4, 2))
        for i, (name, radius, color, desc) in enumerate(sorted(zones, key=lambda z: z[1]), start=1):
            tk.Label(self.legend, bg=color, width=2).grid(row=i, column=0, padx=(6, 4), pady=1)
            tk.Label(self.legend, bg="white", anchor="w",
                     text=f"{name}: {radius:.2f} км ({math.pi * radius ** 2:.1f} км²) — {desc}"
                     ).grid(row=i, column=1, sticky="w", padx=(0, 6))
        tk.Label(self.legend, bg="white", fg="gray40", anchor="w",
                 text="Приблизительная модель, воздушный взрыв").grid(
            row=len(zones) + 1, column=0, columnspan=2, sticky="w", padx=6, pady=(2, 4))
        self.legend.place(relx=0.01, rely=0.98, anchor="sw")

    def clear_zones(self):
        if self.zone_job is not None:
            self.root.after_cancel(self.zone_job)
            self.zone_job = None
        for poly in self.zone_polys:
            poly.delete()
        self.zone_polys = []
        self.legend.place_forget()


if __name__ == "__main__":
    root = tk.Tk()
    CityMapApp(root)
    root.mainloop()
