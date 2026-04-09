import json
import time
import pandas as pd
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.fotmob.com"
TEAM_ID = 10086
OUTPUT_FILE = r"C:\Users\feder\OneDrive\Escritorio\argentinos_juniors_stats.xlsx"

with open("plantel.json", encoding="utf-8") as f:
    plantel_data = json.load(f)
with open("partidos.json", encoding="utf-8") as f:
    partidos = json.load(f)

player_ids = {p["id"] for p in plantel_data["players"]}

def parse_player_stats(next_data, fecha, rival, local, resultado, match_id):
    """Extrae stats de jugadores de AJ desde __NEXT_DATA__."""
    rows = []
    try:
        ps = next_data["props"]["pageProps"]["content"]["playerStats"]
    except (KeyError, TypeError):
        return rows

    for pid, p in ps.items():
        if str(p.get("teamId", "")) != str(TEAM_ID):
            continue

        name = p.get("name", "")
        shirt = p.get("shirtNumber", "")

        row = {
            "Fecha": fecha,
            "Rival": rival,
            "Local_Visitante": local,
            "Resultado": resultado,
            "Jugador": name,
            "Camiseta": shirt,
            "Jugador_ID": pid,
        }

        for section in p.get("stats", []):
            for stat_name, stat_obj in section.get("stats", {}).items():
                if stat_name == "Shotmap":
                    continue
                stat = stat_obj.get("stat", {})
                value = stat.get("value", "")
                total = stat.get("total", None)
                if total is not None:
                    row[stat_name] = f"{value}/{total}"
                else:
                    row[stat_name] = value

        rows.append(row)
    return rows


all_rows = []

# --- Partido 1 (vs Sarmiento): ya tenemos next_data.json ---
print("[1/12] 2026-01-26 vs Sarmiento (Local) 1 - 0")
with open("next_data.json", encoding="utf-8") as f:
    nd = json.load(f)
rows = parse_player_stats(nd, "2026-01-26", "Sarmiento", "Local", "1 - 0", 5101880)
print(f"  Jugadores AJ: {len(rows)}")
all_rows.extend(rows)

# --- Partidos 2-12: navegar y extraer __NEXT_DATA__ ---
remaining = partidos[1:]  # ya procesamos el primero

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=150)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="es-AR",
        viewport={"width": 1280, "height": 900}
    )
    page = context.new_page()

    for i, partido in enumerate(remaining):
        match_id = partido["id"]
        fecha = partido["fecha"]
        rival = partido["rival"]
        local = "Local" if partido["local"] else "Visitante"
        resultado = partido["resultado"]
        url = partido["url"]

        print(f"[{i+2}/{len(partidos)}] {fecha} vs {rival} ({local}) {resultado}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            time.sleep(4)

            nd = page.evaluate("() => window.__NEXT_DATA__")
            if not nd:
                print(f"  WARN: sin __NEXT_DATA__")
                continue

            rows = parse_player_stats(nd, fecha, rival, local, resultado, match_id)
            print(f"  Jugadores AJ: {len(rows)}")
            all_rows.extend(rows)

        except Exception as e:
            print(f"  ERROR: {e}")

        time.sleep(2)

    browser.close()

# --- Exportar a Excel ---
print(f"\nTotal filas: {len(all_rows)}")

if not all_rows:
    print("ERROR: no hay datos para exportar")
else:
    df = pd.DataFrame(all_rows)

    # Ordenar columnas: primero las de identificación, luego el resto
    id_cols = ["Fecha", "Rival", "Local_Visitante", "Resultado", "Jugador", "Camiseta", "Jugador_ID"]
    stat_cols = [c for c in df.columns if c not in id_cols]
    df = df[id_cols + stat_cols]

    # Ordenar por fecha y jugador
    df = df.sort_values(["Fecha", "Jugador"]).reset_index(drop=True)

    df.to_excel(OUTPUT_FILE, index=False, sheet_name="Stats por partido")
    print(f"Excel guardado: {OUTPUT_FILE}")
    print(f"Filas: {len(df)} | Columnas: {len(df.columns)}")
    print(f"Estadísticas: {stat_cols}")
