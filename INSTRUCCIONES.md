# Scraper de Estadísticas FotMob

Extrae la tabla "Estad. Jugador" de FotMob partido por partido y la exporta a Excel,
replicando exactamente las secciones y columnas de la interfaz web.

---

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `config_equipo.py` | **Único archivo que cambiás** para otro equipo: TEAM_ID, liga, torneo |
| `keys_fotmob.py` | Mapeo español → keys internos de FotMob. Universal, no tocar. |
| `scrape_partido.py` | Navega a un partido y guarda los datos crudos en JSON |
| `export_partido.py` | Lee el JSON y genera el Excel formateado |
| `paso1_api_directa.py` | Obtiene el plantel completo del equipo vía API |
| `paso2_guardar_partidos.py` | Lista todos los partidos jugados en el torneo |

---

## Dependencias

```bash
pip install playwright openpyxl pandas
python -m playwright install chromium
```

---

## Flujo completo para un equipo nuevo

### Paso 1 — Configurar el equipo

Editá `config_equipo.py` con los datos del equipo:

```python
TEAM_ID   = 10086               # ID del equipo en FotMob
TEAM_NAME = "Argentinos Juniors"
LEAGUE_ID   = 112               # ID de la liga
LEAGUE_NAME = "Liga Profesional"
SEASON_NAME = "Apertura 2026"   # Nombre del torneo a filtrar
```

**Cómo encontrar el TEAM_ID:**
1. Entrá a `fotmob.com` y navegá al perfil del equipo
2. La URL tiene el formato: `/teams/TEAM_ID/overview/nombre-equipo`
3. Ejemplo: `/teams/10086/overview/argentinos-juniors` → `TEAM_ID = 10086`

**Cómo encontrar el LEAGUE_ID:**
1. Navegá a la página de la liga
2. La URL tiene el formato: `/leagues/LEAGUE_ID/overview/nombre-liga`
3. Ejemplo: `/leagues/112/overview/liga-profesional` → `LEAGUE_ID = 112`

---

### Paso 2 — Obtener el plantel

```bash
python paso1_api_directa.py
```

Genera `plantel.json` con todos los jugadores y sus IDs.

---

### Paso 3 — Listar los partidos del torneo

```bash
python paso2_guardar_partidos.py
```

Genera `partidos.json` con la lista de partidos jugados, fechas, rivales y URLs.

---

### Paso 4 — Scrapear cada partido

Por cada partido, ejecutar:

```bash
python scrape_partido.py <url_partido> <archivo_salida.json>
```

**Ejemplo:**
```bash
python scrape_partido.py "https://www.fotmob.com/matches/aj-vs-sarmiento/xxx#5101880" "nd_sarmiento.json"
```

- Abre Chrome (visible), navega al partido y extrae los datos.
- El JSON resultante contiene toda la información que FotMob carga en la página.

---

### Paso 5 — Exportar a Excel

```bash
python export_partido.py <next_data.json> <fecha> <rival> <Local|Visitante> <resultado> <salida.xlsx>
```

**Ejemplo:**
```bash
python export_partido.py "nd_sarmiento.json" "2026-01-26" "Sarmiento" "Local" "1 - 0" "AJ_vs_Sarmiento.xlsx"
```

Genera un Excel con:
- **Fila 1:** título del partido (equipo, rival, fecha, resultado)
- **Fila 2:** secciones mergeadas con colores (Top Estadísticas, Ataque, Pases, Defensa, Duelos, Portero)
- **Fila 3:** nombre de cada columna
- **Filas siguientes:** un jugador por fila, ordenados por minutos jugados

---

## Secciones y columnas exportadas

| Sección | Columnas |
|---|---|
| **Top Estadísticas** | Minutos jugados, Goles, Asistencias, xG, xA, xG+xA, Acciones defensivas |
| **Ataque** | Goles, xG, xGOT, Disparos a puerta, Regates, Gdes. oport. perdidas, Toques área rival, Fueras de juego |
| **Pases** | Toques, Pases precisos, Asistencias, xA, Oportunidades creadas, Pases últ. tercio, Centros precisos, Tiros largos precisos |
| **Defensa** | Acciones defensivas, Entradas, Interceptaciones, Bloqueos, Recuperaciones, Despejes, Despeje de cabeza, Regateado |
| **Duelos** | Duelos ganados, Duelos perdidos, Duelo terrestre ganado, Aéreo ganado, Faltas, Faltas recibidas, Regates, Entradas |
| **Portero** | Paradas, Goles en contra, xGOT recibidos, Goles evitados, Líbero, Salida por alto, Tiros largos, Pases precisos |

---

## Agregar o quitar columnas

Todo está centralizado en `keys_fotmob.py`:

- **Agregar una columna:** añadí el par `"Nombre en español": "Key FotMob"` al `KEY_MAP`, y sumá `"Nombre en español"` a la lista de la sección correspondiente en `SECTIONS`.
- **Quitar una columna:** eliminá el nombre de la lista en `SECTIONS` (no hace falta tocar `KEY_MAP`).
- **Cambiar el orden:** reorganizá los elementos dentro de cada lista en `SECTIONS`.

**Cómo encontrar el key interno de FotMob para una stat nueva:**
1. Scrapeá un partido con `scrape_partido.py`
2. Abrí el JSON generado y buscá `"playerStats"`
3. Cada jugador tiene `"stats"` → lista de secciones → cada sección tiene `"stats"` → diccionario con los keys

---

## Limitaciones conocidas

- **FotMob bloquea llamadas directas a su API** (responde 403). El scraper evita esto extrayendo los datos desde `window.__NEXT_DATA__`, que es el estado inicial que Next.js embebe en el HTML de cada página.
- **Se necesita abrir el browser** (Playwright con Chromium). No funciona en modo headless en algunos casos.
- **Los datos dependen de lo que FotMob registre**: partidos sin datos de Opta pueden tener menos estadísticas disponibles.
- **Jugadores sin minutos registrados** aparecen en la tabla con celdas vacías (no jugaron o no hay datos).
