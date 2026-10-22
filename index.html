<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Интерактивная карта</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    * { box-sizing: border-box; }
    html, body { margin: 0; height: 100%; font-family: system-ui, sans-serif; background: #f5f5f5; color: #222; }
    body { display: flex; flex-direction: column; }
    header { padding: 12px 16px; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,.1); z-index: 1000; }
    h1 { margin: 0 0 10px; font-size: 18px; }
    .tabs { display: flex; gap: 4px; margin-bottom: 10px; }
    .tab { border: 0; padding: 8px 14px; border-radius: 8px; background: #eee; cursor: pointer; font-size: 14px;
           transition: background .25s, color .25s, transform .15s; }
    .tab:hover { background: #e0e7ff; }
    .tab:active { transform: scale(.96); }
    .tab.active { background: #2563eb; color: #fff; }
    .panel { display: none; gap: 8px; flex-wrap: wrap; align-items: center; }
    .panel.active { display: flex; animation: fadeIn .3s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: none; } }
    input { padding: 8px 10px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; min-width: 0;
            transition: border-color .2s, box-shadow .2s; }
    input:focus { outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.2); }
    .pin { border-radius: 50%; border: 3px solid #fff; box-shadow: 0 0 4px #0008;
           transition: background .4s, width .4s, height .4s; animation: drop .45s cubic-bezier(.3,1.6,.5,1); }
    @keyframes drop { from { opacity: 0; transform: translateY(-30px) scale(.5); } to { opacity: 1; transform: none; } }
    #city { flex: 1 1 240px; }
    .num { width: 130px; }
    #title { flex: 1 1 160px; }
    button.go { padding: 8px 14px; border: 0; border-radius: 8px; background: #2563eb; color: #fff; cursor: pointer; font-size: 14px;
                transition: background .2s, opacity .2s, transform .15s; }
    button.go:hover { background: #1d4ed8; }
    button.go:active { transform: scale(.96); }
    button.go:disabled { opacity: .5; cursor: wait; }
    button.clear { background: #6b7280; }
    button.clear:hover { background: #4b5563; }
    #status { margin-top: 8px; font-size: 13px; color: #555; min-height: 1em; transition: opacity .3s; }
    select { padding: 8px 10px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; background: #fff; max-width: 100%; }
    button.launch { background: #dc2626; }
    button.launch:hover { background: #b91c1c; }
    #wrap { flex: 1; position: relative; }
    #map { position: absolute; inset: 0; }
    #flash { position: absolute; inset: 0; background: #fff; opacity: 0; pointer-events: none; z-index: 1100;
             transition: opacity .7s ease-out; }
    #flash.on { opacity: .95; transition: none; }
    #legend { position: absolute; left: 10px; bottom: 24px; z-index: 1000; background: rgba(255,255,255,.95);
              border-radius: 10px; padding: 10px 12px; font-size: 13px; max-width: min(400px, calc(100% - 20px));
              max-height: 60%; overflow: auto; box-shadow: 0 2px 10px rgba(0,0,0,.2);
              opacity: 0; transform: translateY(10px); pointer-events: none; transition: opacity .4s, transform .4s; }
    #legend.show { opacity: 1; transform: none; pointer-events: auto; }
    #legend .row { display: flex; gap: 8px; margin-top: 6px; }
    #legend .sw { flex: 0 0 14px; height: 14px; border-radius: 50%; margin-top: 2px; }
    #legend .note { display: block; margin-top: 8px; color: #777; }
  </style>
</head>
<body>
  <header>
    <h1>🗺️ Интерактивная карта: город или координаты</h1>
    <div class="tabs">
      <button class="tab active" data-panel="p-city">🌍 Поиск по городу</button>
      <button class="tab" data-panel="p-coords">📍 Координаты вручную</button>
      <button class="tab" data-panel="p-bomb">☢️ Бомба</button>
    </div>

    <form id="p-city" class="panel active">
      <input id="city" placeholder="Например: Москва, Алматы, Париж..." autocomplete="off">
      <button class="go" type="submit">Найти город</button>
    </form>

    <form id="p-coords" class="panel">
      <input id="lat" class="num" placeholder="Широта: 55.751244" inputmode="decimal">
      <input id="lon" class="num" placeholder="Долгота: 37.618423" inputmode="decimal">
      <input id="title" placeholder="Название метки (необязательно)">
      <button class="go" type="submit">Показать</button>
      <button class="go clear" type="button" id="clear">Очистить метки</button>
    </form>

    <form id="p-bomb" class="panel">
      <select id="bomb"></select>
      <input id="kt" class="num" placeholder="Мощность" inputmode="decimal">
      <select id="unit" title="Единицы мощности">
        <option value="1">кт</option>
        <option value="1000">Мт</option>
      </select>
      <button class="go launch" type="submit">🚀 Запуск</button>
      <button class="go clear" type="button" id="clear-zones">Убрать зоны</button>
    </form>

    <div id="status">Клик по карте — поставить метку. Бомба падает на последнюю метку (или в центр карты).</div>
  </header>

  <div id="wrap">
    <div id="map"></div>
    <div id="legend"></div>
    <div id="flash"></div>
  </div>

  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const map = L.map('map', {
      zoomSnap: 0.25,           // дробный зум — без рывков
      zoomDelta: 0.5,
      wheelPxPerZoomLevel: 120, // колесо мыши зумит мягче
      inertiaDeceleration: 2000 // карта «доезжает» после перетаскивания
    }).setView([51.1694, 71.4491], 5); // Астана
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    const markers = L.layerGroup().addTo(map);
    const statusEl = document.getElementById('status');
    const buttons = document.querySelectorAll('button.go[type=submit]');
    const redIcon = L.divIcon({ className: '', html: '<div class="pin" style="width:18px;height:18px;background:#dc2626"></div>', iconSize: [18, 18] });
    const blueIcon = L.divIcon({ className: '', html: '<div class="pin" style="width:14px;height:14px;background:#2563eb;animation:none"></div>', iconSize: [14, 14] });

    // Вкладки
    document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => {
      document.querySelectorAll('.tab, .panel').forEach(el => el.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(tab.dataset.panel).classList.add('active');
    }));

    function escapeHtml(s) {
      return s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    }

    function setBusy(busy, text) {
      buttons.forEach(b => b.disabled = busy);
      statusEl.textContent = text;
    }

    async function nominatim(path) {
      const res = await fetch('https://nominatim.openstreetmap.org/' + path + '&format=json&accept-language=ru');
      if (!res.ok) throw new Error('Сервер вернул ' + res.status);
      return res.json();
    }

    function addMarker(lat, lon, title, address, zoom) {
      markers.eachLayer(m => m.setIcon(blueIcon));
      const popup = '<b>' + escapeHtml(title) + '</b>' +
        (address ? '<br><small>' + escapeHtml(address) + '</small>' : '') +
        '<br><small>' + lat.toFixed(6) + ', ' + lon.toFixed(6) + '</small>';
      const marker = L.marker([lat, lon], { icon: redIcon }).bindPopup(popup, { autoPan: false }).addTo(markers);
      if (zoom) {
        // Плавный перелёт: отдаление → полёт → приближение; попап открывается по прилёте
        map.flyTo([lat, lon], zoom, { duration: 1.8, easeLinearity: 0.2 });
        map.once('moveend', () => marker.openPopup());
      } else {
        map.panTo([lat, lon], { animate: true, duration: 0.6, easeLinearity: 0.2 });
        marker.openPopup();
      }
      setBusy(false, address || title);
    }

    async function reverseAndMark(lat, lon, title, zoom) {
      setBusy(true, 'Определяю адрес...');
      let address = '';
      try {
        const data = await nominatim('reverse?lat=' + lat + '&lon=' + lon);
        address = data.display_name || '';
      } catch (e) { /* адрес не обязателен */ }
      const name = title || (address ? address.split(',')[0] : lat + ', ' + lon);
      addMarker(lat, lon, name, address, zoom);
    }

    // Поиск по городу
    document.getElementById('p-city').addEventListener('submit', async e => {
      e.preventDefault();
      const city = document.getElementById('city').value.trim();
      if (!city) { alert('Введите название города!'); return; }
      setBusy(true, 'Ищу «' + city + '»...');
      try {
        const data = await nominatim('search?q=' + encodeURIComponent(city) + '&limit=1');
        if (!data.length) { setBusy(false, ''); alert("Город '" + city + "' не найден."); return; }
        const p = data[0];
        addMarker(parseFloat(p.lat), parseFloat(p.lon), p.display_name.split(',')[0], p.display_name, 12);
      } catch (err) {
        setBusy(false, '');
        alert('Не удалось получить данные:\n' + err.message);
      }
    });

    // Поиск по координатам
    document.getElementById('p-coords').addEventListener('submit', e => {
      e.preventDefault();
      const latStr = document.getElementById('lat').value.trim().replace(',', '.');
      const lonStr = document.getElementById('lon').value.trim().replace(',', '.');
      if (!latStr || !lonStr) { alert('Заполните поля широты и долготы!'); return; }
      const lat = Number(latStr), lon = Number(lonStr);
      if (Number.isNaN(lat) || Number.isNaN(lon)) { alert('Широта и долгота должны быть числами!'); return; }
      if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
        alert('Неверные координаты!\nШирота: от -90 до 90\nДолгота: от -180 до 180'); return;
      }
      reverseAndMark(lat, lon, document.getElementById('title').value.trim(), 14);
    });

    // Клик по карте — метка
    map.on('click', e => reverseAndMark(+e.latlng.lat.toFixed(6), +e.latlng.lng.toFixed(6), '', null));

    document.getElementById('clear').addEventListener('click', () => {
      markers.clearLayers();
      statusEl.textContent = 'Метки очищены';
    });

    // ================= Бомба =================
    const BOMBS = [
      ['Little Boy — Хиросима, 1945', 15],
      ['Fat Man — Нагасаки, 1945', 21],
      ['W76 — боеголовка Trident', 100],
      ['W87 — боеголовка Minuteman III', 300],
      ['W88 — боеголовка Trident II', 475],
      ['B83 — авиабомба США', 1200],
      ['Castle Bravo — испытание США, 1954', 15000],
      ['Царь-бомба — испытание СССР, 1961', 50000],
    ];

    // Зоны поражения (воздушный взрыв): радиус_км = k * мощность_кт ^ p.
    // Приблизительные формулы подобия, откалиброваны по данным для Хиросимы.
    const EFFECTS = [
      { name: 'Огненный шар', k: 0.068, p: 0.4, color: '#facc15', fill: 0.6, desc: 'всё внутри испаряется' },
      { name: 'Сильная ударная волна (20 psi)', k: 0.243, p: 1 / 3, color: '#b91c1c', fill: 0.3, desc: 'разрушены даже бетонные здания' },
      { name: 'Радиация (500 бэр)', k: 0.72, p: 0.19, color: '#16a34a', fill: 0.25, desc: 'смертельная доза для 50–90% людей' },
      { name: 'Средняя ударная волна (5 psi)', k: 0.693, p: 1 / 3, color: '#6b7280', fill: 0.25, desc: 'рушатся жилые дома' },
      { name: 'Тепловое излучение', k: 0.627, p: 0.41, color: '#f97316', fill: 0.2, desc: 'ожоги 3-й степени на открытом месте' },
      { name: 'Слабая ударная волна (1 psi)', k: 1.906, p: 1 / 3, color: '#60a5fa', fill: 0.15, desc: 'выбиты окна, ранения стеклом' },
    ];

    const bombSelect = document.getElementById('bomb');
    const ktInput = document.getElementById('kt');
    const unitSelect = document.getElementById('unit');
    const legendEl = document.getElementById('legend');
    const flashEl = document.getElementById('flash');
    const zones = L.layerGroup().addTo(map);
    let zoneAnim = null, launchTimer = null;

    BOMBS.forEach(([name, kt]) => bombSelect.add(new Option(name, kt)));
    // Подставляет мощность бомбы в поле: от 1000 кт — в мегатоннах
    function setYield(kt) {
      const mt = kt >= 1000;
      unitSelect.value = mt ? '1000' : '1';
      ktInput.value = mt ? kt / 1000 : kt;
    }
    setYield(BOMBS[0][1]);
    bombSelect.addEventListener('change', () => setYield(Number(bombSelect.value)));

    function fmtKt(kt) {
      return kt >= 1000 ? (kt / 1000).toLocaleString('ru') + ' Мт' : kt.toLocaleString('ru') + ' кт';
    }

    function clearZones() {
      cancelAnimationFrame(zoneAnim);
      clearTimeout(launchTimer);
      zones.clearLayers();
      legendEl.classList.remove('show');
    }

    function showLegend(kt, list) {
      legendEl.innerHTML = '<b>☢️ ' + fmtKt(kt) + '</b>' +
        list.slice().reverse().map(z =>
          '<div class="row"><span class="sw" style="background:' + z.color + '"></span><div><b>' + z.name + '</b> — ' +
          z.r.toFixed(2) + ' км (' + (Math.PI * z.r * z.r).toFixed(1) + ' км²)<br><small>' + z.desc + '</small></div></div>'
        ).join('') +
        '<small class="note">Приблизительная модель, воздушный взрыв.</small>';
      legendEl.classList.add('show');
    }

    function detonate(target, list, kt) {
      flashEl.classList.add('on');
      setTimeout(() => flashEl.classList.remove('on'), 120);

      const circles = list.map(z => L.circle(target, {
        radius: 1, color: z.color, weight: 2, fillColor: z.color, fillOpacity: z.fill
      }).bindTooltip(z.name + ': ' + z.r.toFixed(2) + ' км', { sticky: true }).addTo(zones));

      const start = performance.now();
      const step = now => {
        const t = Math.min((now - start) / 1500, 1);
        const e = 1 - Math.pow(1 - t, 3); // быстро в начале, плавно в конце — как ударная волна
        circles.forEach((c, i) => c.setRadius(Math.max(list[i].r * 1000 * e, 1)));
        if (t < 1) zoneAnim = requestAnimationFrame(step);
      };
      zoneAnim = requestAnimationFrame(step);

      showLegend(kt, list);
      statusEl.textContent = 'Взрыв ' + fmtKt(kt) + ' в точке ' + target.lat.toFixed(4) + ', ' + target.lng.toFixed(4);
    }

    document.getElementById('p-bomb').addEventListener('submit', e => {
      e.preventDefault();
      const value = Number(ktInput.value.trim().replace(',', '.'));
      if (!value) { alert('Мощность должна быть положительным числом!'); return; }
      const kt = value * Number(unitSelect.value);
      if (kt < 0.001 || kt > 100000) { alert('Мощность: от 0,001 кт до 100 Мт'); return; }

      // Цель — последняя метка, а если меток нет — центр карты
      const last = markers.getLayers().at(-1);
      const target = last ? last.getLatLng() : map.getCenter();
      clearZones();

      const list = EFFECTS.map(z => ({ ...z, r: z.k * Math.pow(kt, z.p) }))
                          .sort((a, b) => b.r - a.r); // от большой к малой, чтобы малые были сверху
      map.flyToBounds(target.toBounds(list[0].r * 2000 * 1.15), { duration: 1.2 });
      statusEl.textContent = 'Запуск...';
      launchTimer = setTimeout(() => detonate(target, list, kt), 1300);
    });

    document.getElementById('clear-zones').addEventListener('click', () => {
      clearZones();
      statusEl.textContent = 'Зоны убраны';
    });
  </script>
</body>
</html>
