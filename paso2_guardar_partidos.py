import json
import urllib.request
from datetime import datetime, timezone

TEAM_ID = 10086
BASE_URL = "https://www.fotmob.com"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.fotmob.com/",
}

url = f"{BASE_URL}/api/data/teams?id={TEAM_ID}&ccode3=ARG"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode("utf-8"))

def find_matches(obj, depth=0):
    if depth > 5: return []
    found = []
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                if "id" in item and "home" in item:
                    found.append(item)
                else:
                    found.extend(find_matches(item, depth+1))
    elif isinstance(obj, dict):
        for v in obj.values():
            found.extend(find_matches(v, depth+1))
    return found

all_matches = find_matches(data.get("fixtures", {}))
now = datetime.now(timezone.utc)

apertura_matches = []
for m in all_matches:
    tournament = m.get("tournament", {})
    name = tournament.get("name", "")
    league_id = tournament.get("leagueId", 0)
    status = m.get("status", {})
    utc_str = status.get("utcTime", "")
    finished = status.get("finished", False)

    if league_id == 112 and "Apertura" in name and not "Playoff" in name:
        # Solo partidos ya jugados
        if finished:
            # Determinar local/visitante
            home = m.get("home", {})
            away = m.get("away", {})
            is_home = home.get("id") == TEAM_ID
            rival = away.get("name") if is_home else home.get("name")
            score = status.get("scoreStr", "")
            page_url = m.get("pageUrl", "")
            full_url = BASE_URL + "/es" + page_url.replace("/es", "").replace("/matches", "/matches") if not page_url.startswith("http") else page_url

            # Construir URL correctamente
            if page_url:
                full_url = f"https://www.fotmob.com{page_url}"

            fecha = utc_str[:10] if utc_str else ""

            apertura_matches.append({
                "id": m.get("id"),
                "fecha": fecha,
                "rival": rival,
                "local": is_home,
                "resultado": score,
                "url": full_url,
                "page_url": page_url
            })

apertura_matches.sort(key=lambda x: x["fecha"])

print(f"Partidos Liga Profesional Apertura 2026 (jugados): {len(apertura_matches)}\n")
for m in apertura_matches:
    local_visit = "L" if m["local"] else "V"
    print(f"  {m['fecha']}  [{local_visit}]  vs {m['rival']:35s}  {m['resultado']:8s}  {m['url']}")

with open("partidos.json", "w", encoding="utf-8") as f:
    json.dump(apertura_matches, f, ensure_ascii=False, indent=2)
print(f"\nPartidos guardados en partidos.json")
