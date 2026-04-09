import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.fotmob.com"
TEAM_ID = 10086

with open("plantel.json", encoding="utf-8") as f:
    plantel_data = json.load(f)
with open("partidos.json", encoding="utf-8") as f:
    partidos = json.load(f)

player_ids = {p["id"] for p in plantel_data["players"]}
player_names = {p["id"]: p["name"] for p in plantel_data["players"]}

print(f"Plantel: {len(player_ids)} jugadores")
print(f"Partidos a procesar: {len(partidos)}\n")

def extract_player_rows(match_data, fecha, rival, local, resultado, match_id):
    rows = []
    content = match_data.get("content", {})

    # --- Desde playerStats ---
    player_stats = content.get("playerStats", {})
    for side_key in ["home", "away"]:
        side = player_stats.get(side_key, {})
        side_team_id = str(side.get("teamId", ""))
        if side_team_id != str(TEAM_ID):
            continue
        players_list = side.get("players", [])
        for p in players_list:
            pid = str(p.get("id", ""))
            pname = p.get("name", "")
            if isinstance(pname, dict):
                pname = pname.get("fullName", pname.get("lastName", pname.get("firstName", "")))
            stats_raw = p.get("stats", [])
            row = {
                "Fecha": fecha,
                "Rival": rival,
                "Local_Visitante": local,
                "Resultado": resultado,
                "Jugador": pname,
                "Jugador_ID": pid,
                "Match_ID": str(match_id),
            }
            if isinstance(stats_raw, list):
                for s in stats_raw:
                    if isinstance(s, dict):
                        # Puede tener subestructura: {title, stats: [{key, value}]}
                        if "stats" in s:
                            for sub in s["stats"]:
                                k = sub.get("key", sub.get("title", ""))
                                v = sub.get("value", sub.get("stat", ""))
                                if k:
                                    row[k] = v
                        else:
                            k = s.get("key", s.get("title", ""))
                            v = s.get("value", s.get("stat", ""))
                            if k:
                                row[k] = v
            elif isinstance(stats_raw, dict):
                row.update(stats_raw)
            rows.append(row)

    if rows:
        return rows

    # --- Fallback desde lineup ---
    lineup_data = content.get("lineup", {})
    lineups = lineup_data.get("lineup", [])
    for team_lineup in lineups:
        if str(team_lineup.get("teamId", 0)) != str(TEAM_ID):
            continue
        all_players = []
        starters = team_lineup.get("players", [])
        if starters and isinstance(starters[0], list):
            for line in starters:
                all_players.extend(line)
        else:
            all_players.extend(starters)
        all_players.extend(team_lineup.get("bench", []))

        for p in all_players:
            if not isinstance(p, dict):
                continue
            pid = str(p.get("id", ""))
            pname = p.get("name", {})
            if isinstance(pname, dict):
                pname = pname.get("fullName", pname.get("lastName", ""))
            stats_raw = p.get("stats", {})
            row = {
                "Fecha": fecha,
                "Rival": rival,
                "Local_Visitante": local,
                "Resultado": resultado,
                "Jugador": pname,
                "Jugador_ID": pid,
                "Match_ID": str(match_id),
            }
            if isinstance(stats_raw, list):
                for s in stats_raw:
                    if isinstance(s, dict):
                        if "stats" in s:
                            for sub in s["stats"]:
                                k = sub.get("key", "")
                                v = sub.get("value", "")
                                if k:
                                    row[k] = v
                        else:
                            k = s.get("key", s.get("title", ""))
                            v = s.get("value", "")
                            if k:
                                row[k] = v
            elif isinstance(stats_raw, dict):
                row.update(stats_raw)
            if pid or pname:
                rows.append(row)

    return rows

all_rows = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="es-AR",
        viewport={"width": 1280, "height": 900}
    )
    page = context.new_page()

    # Cargar la página principal para obtener cookies
    print("Cargando FotMob para obtener cookies...")
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
    time.sleep(3)

    for i, partido in enumerate(partidos):
        match_id = partido["id"]
        fecha = partido["fecha"]
        rival = partido["rival"]
        local = "Local" if partido["local"] else "Visitante"
        resultado = partido["resultado"]

        print(f"[{i+1}/{len(partidos)}] {fecha} vs {rival} ({local}) {resultado}")

        api_url = f"{BASE_URL}/api/data/matchDetails?matchId={match_id}"
        try:
            response = context.request.get(
                api_url,
                headers={"Accept": "application/json", "Referer": BASE_URL}
            )
            if not response.ok:
                print(f"  HTTP {response.status} - intentando con page.goto...")
                # Fallback: navegar al partido y capturar la respuesta
                match_url = partido["url"]
                match_data_holder = {}

                def on_response(resp):
                    if f"matchDetails?matchId={match_id}" in resp.url:
                        try:
                            match_data_holder["data"] = resp.json()
                        except:
                            pass

                page.on("response", on_response)
                page.goto(match_url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(4)
                page.remove_listener("response", on_response)

                if "data" in match_data_holder:
                    match_data = match_data_holder["data"]
                else:
                    print(f"  ERROR: no se pudo obtener datos del partido")
                    continue
            else:
                match_data = response.json()
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        # Guardar muestra del primer partido
        if i == 0:
            with open("match_sample_raw.json", "w", encoding="utf-8") as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)
            print("  (match_sample_raw.json guardado)")

        rows = extract_player_rows(match_data, fecha, rival, local, resultado, match_id)
        print(f"  Filas: {len(rows)}")

        if rows:
            stats_keys = [k for k in rows[0].keys() if k not in
                         ("Fecha","Rival","Local_Visitante","Resultado","Jugador","Jugador_ID","Match_ID")]
            print(f"  Stats: {stats_keys[:6]}{'...' if len(stats_keys)>6 else ''}")

        all_rows.extend(rows)
        time.sleep(1.5)

    browser.close()

print(f"\n{'='*50}")
print(f"Total filas: {len(all_rows)}")

with open("stats_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_rows, f, ensure_ascii=False, indent=2)
print("Guardado en stats_raw.json")
