import json
import time
import urllib.request

BASE_URL = "https://www.fotmob.com"
TEAM_ID = 10086

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.fotmob.com/",
}

with open("plantel.json", encoding="utf-8") as f:
    plantel_data = json.load(f)
with open("partidos.json", encoding="utf-8") as f:
    partidos = json.load(f)

player_ids = {p["id"] for p in plantel_data["players"]}
player_names = {p["id"]: p["name"] for p in plantel_data["players"]}

print(f"Plantel: {len(player_ids)} jugadores")
print(f"Partidos a procesar: {len(partidos)}\n")

def fetch_json(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def extract_player_rows(match_data, fecha, rival, local, resultado, match_id):
    """Extrae filas de estadísticas de jugadores de AJ desde matchDetails."""
    rows = []
    content = match_data.get("content", {})

    # --- Intentar desde playerStats (sección dedicada) ---
    player_stats = content.get("playerStats", {})
    # playerStats puede tener estructura: {home: {players: [...]}, away: {players: [...]}}
    for side_key in ["home", "away"]:
        side = player_stats.get(side_key, {})
        side_team_id = str(side.get("teamId", ""))
        if side_team_id != str(TEAM_ID):
            continue
        players_list = side.get("players", [])
        for p in players_list:
            pid = str(p.get("id", ""))
            pname = p.get("name", "")
            stats_raw = p.get("stats", [])
            # stats puede ser lista de {key, value} o dict
            row = {
                "Fecha": fecha,
                "Rival": rival,
                "Local_Visitante": local,
                "Resultado": resultado,
                "Jugador": pname,
                "Jugador_ID": pid,
                "Match_ID": match_id,
            }
            if isinstance(stats_raw, list):
                for s in stats_raw:
                    if isinstance(s, dict):
                        k = s.get("key", s.get("title", ""))
                        v = s.get("value", s.get("stat", ""))
                        if k:
                            row[k] = v
            elif isinstance(stats_raw, dict):
                row.update(stats_raw)
            rows.append(row)

    if rows:
        return rows

    # --- Fallback: desde lineup ---
    lineup_data = content.get("lineup", {})
    lineups = lineup_data.get("lineup", [])
    for team_lineup in lineups:
        team_id_in_match = team_lineup.get("teamId", 0)
        if str(team_id_in_match) != str(TEAM_ID):
            continue
        # Aplanar jugadores: starters + bench
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
                "Match_ID": match_id,
            }
            if isinstance(stats_raw, list):
                for s in stats_raw:
                    if isinstance(s, dict):
                        k = s.get("key", s.get("title", ""))
                        v = s.get("value", s.get("stat", ""))
                        if k:
                            row[k] = v
            elif isinstance(stats_raw, dict):
                row.update(stats_raw)
            if pid or pname:
                rows.append(row)

    return rows

all_rows = []

for i, partido in enumerate(partidos):
    match_id = partido["id"]
    fecha = partido["fecha"]
    rival = partido["rival"]
    local = "Local" if partido["local"] else "Visitante"
    resultado = partido["resultado"]

    print(f"[{i+1}/{len(partidos)}] {fecha} vs {rival} ({local}) {resultado}")

    api_url = f"{BASE_URL}/api/data/matchDetails?matchId={match_id}"
    try:
        match_data = fetch_json(api_url)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    # Guardar raw del primer partido para inspección
    if i == 0:
        with open(f"match_sample_raw.json", "w", encoding="utf-8") as f:
            json.dump(match_data, f, ensure_ascii=False, indent=2)
        print("  (match_sample_raw.json guardado para inspección)")

    rows = extract_player_rows(match_data, fecha, rival, local, resultado, match_id)
    print(f"  Filas extraídas: {len(rows)}")
    if rows:
        sample = rows[0]
        stats_keys = [k for k in sample.keys() if k not in ("Fecha","Rival","Local_Visitante","Resultado","Jugador","Jugador_ID","Match_ID")]
        print(f"  Stats disponibles: {stats_keys[:8]}{'...' if len(stats_keys)>8 else ''}")
    all_rows.extend(rows)

    time.sleep(1.5)

print(f"\n{'='*50}")
print(f"Total filas recolectadas: {len(all_rows)}")

with open("stats_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_rows, f, ensure_ascii=False, indent=2)
print("Stats guardadas en stats_raw.json")
