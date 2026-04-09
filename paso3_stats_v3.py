import json
import time
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.fotmob.com"
TEAM_ID = 10086

with open("plantel.json", encoding="utf-8") as f:
    plantel_data = json.load(f)
with open("partidos.json", encoding="utf-8") as f:
    partidos = json.load(f)

print(f"Plantel: {len(plantel_data['players'])} jugadores")
print(f"Partidos a procesar: {len(partidos)}\n")

def extract_player_rows(match_data, fecha, rival, local, resultado, match_id):
    rows = []
    content = match_data.get("content", {})

    # Intentar desde playerStats
    player_stats = content.get("playerStats", {})
    for side_key in ["home", "away"]:
        side = player_stats.get(side_key, {})
        side_team_id = str(side.get("teamId", ""))
        if side_team_id != str(TEAM_ID):
            continue
        for p in side.get("players", []):
            pid = str(p.get("id", ""))
            pname = p.get("name", "")
            if isinstance(pname, dict):
                pname = pname.get("fullName", pname.get("lastName", ""))
            row = {
                "Fecha": fecha,
                "Rival": rival,
                "Local_Visitante": local,
                "Resultado": resultado,
                "Jugador": pname,
                "Jugador_ID": pid,
                "Match_ID": str(match_id),
            }
            stats_raw = p.get("stats", [])
            if isinstance(stats_raw, list):
                for s in stats_raw:
                    if isinstance(s, dict):
                        if "stats" in s:
                            for sub in s["stats"]:
                                k = sub.get("key", sub.get("title", ""))
                                v = sub.get("value", sub.get("stat", ""))
                                if k: row[k] = v
                        else:
                            k = s.get("key", s.get("title", ""))
                            v = s.get("value", s.get("stat", ""))
                            if k: row[k] = v
            elif isinstance(stats_raw, dict):
                row.update(stats_raw)
            rows.append(row)

    if rows:
        return rows

    # Fallback desde lineup
    lineup_data = content.get("lineup", {})
    for team_lineup in lineup_data.get("lineup", []):
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
            row = {
                "Fecha": fecha,
                "Rival": rival,
                "Local_Visitante": local,
                "Resultado": resultado,
                "Jugador": pname,
                "Jugador_ID": pid,
                "Match_ID": str(match_id),
            }
            stats_raw = p.get("stats", {})
            if isinstance(stats_raw, list):
                for s in stats_raw:
                    if isinstance(s, dict):
                        if "stats" in s:
                            for sub in s["stats"]:
                                k = sub.get("key", "")
                                v = sub.get("value", "")
                                if k: row[k] = v
                        else:
                            k = s.get("key", s.get("title", ""))
                            v = s.get("value", "")
                            if k: row[k] = v
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

    # Visitar primero la página del equipo para settear cookies
    print("Cargando página de AJ para settear cookies...")
    page.goto(f"{BASE_URL}/es/teams/10086/overview/argentinos-juniors",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)

    for i, partido in enumerate(partidos):
        match_id = partido["id"]
        fecha = partido["fecha"]
        rival = partido["rival"]
        local = "Local" if partido["local"] else "Visitante"
        resultado = partido["resultado"]

        print(f"[{i+1}/{len(partidos)}] {fecha} vs {rival} ({local}) {resultado}")

        api_url = f"{BASE_URL}/api/data/matchDetails?matchId={match_id}"

        # Hacer el fetch desde dentro del browser con sus cookies/headers
        try:
            result = page.evaluate(f"""
                async () => {{
                    const resp = await fetch('{api_url}', {{
                        headers: {{
                            'Accept': 'application/json',
                            'x-mas': 'eyJib2R5Ijp7InVybCI6Imh0dHBzOi8vd3d3LmZvdG1vYi5jb20vYXBpL2RhdGEvbWF0Y2hEZXRhaWxzP21hdGNoSWQ9NTEwMTg4MCIsImNvZGUiOjIwMCwidGltZSI6MTc0NDAxMTIwMCwic3RhdHVzQ29kZSI6MjAwfSwic2lnbmF0dXJlIjoiMDZkMjEwM2U3MDcwZTE3NDNiZTE5N2UwZGQ3MDI2MTcifQ=='
                        }}
                    }});
                    if (!resp.ok) return {{ error: resp.status }};
                    return await resp.json();
                }}
            """)

            if isinstance(result, dict) and "error" in result:
                print(f"  HTTP {result['error']} via fetch")
                result = None
        except Exception as e:
            print(f"  Error en evaluate: {e}")
            result = None

        if not result:
            # Navegar a la página del partido y capturar la respuesta
            print(f"  Navegando a la página del partido...")
            match_data_holder = {}

            def make_listener(holder):
                def listener(resp):
                    if f"matchDetails?matchId={match_id}" in resp.url:
                        try:
                            holder["data"] = resp.json()
                        except:
                            pass
                return listener

            listener = make_listener(match_data_holder)
            page.on("response", listener)
            page.goto(partido["url"], wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)
            page.remove_listener("response", listener)

            if "data" in match_data_holder:
                result = match_data_holder["data"]
                print("  Datos capturados via navegación")
            else:
                print(f"  ERROR: no se pudo obtener datos")
                continue

        match_data = result

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
            print(f"  Stats ({len(stats_keys)}): {stats_keys[:8]}{'...' if len(stats_keys)>8 else ''}")

        all_rows.extend(rows)
        time.sleep(1)

    browser.close()

print(f"\n{'='*50}")
print(f"Total filas: {len(all_rows)}")

with open("stats_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_rows, f, ensure_ascii=False, indent=2)
print("Guardado en stats_raw.json")
