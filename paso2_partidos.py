import json
import urllib.request

TEAM_ID = 10086

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.fotmob.com/",
}

# La API del equipo ya incluye fixtures
url = f"https://www.fotmob.com/api/data/teams?id={TEAM_ID}&ccode3=ARG"
print(f"Consultando fixtures de Argentinos Juniors...")

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode("utf-8"))

fixtures = data.get("fixtures", {})

# Guardar raw para inspección
with open("fixtures_raw.json", "w", encoding="utf-8") as f:
    json.dump(fixtures, f, ensure_ascii=False, indent=2)

# Inspeccionar estructura
print("Fixtures keys:", list(fixtures.keys())[:10])

# Buscar partidos de Liga Profesional Apertura 2026
matches = []

# Los fixtures generalmente tienen una lista de "allFixtures" o similar
all_fixtures = fixtures.get("allFixtures", {})
if not all_fixtures:
    all_fixtures = fixtures

# Intentar diferentes estructuras
def find_matches(obj, depth=0):
    if depth > 5:
        return []
    found = []
    if isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                # Verificar si es un partido
                if "id" in item and ("home" in item or "homeTeam" in item):
                    found.append(item)
                else:
                    found.extend(find_matches(item, depth+1))
    elif isinstance(obj, dict):
        for v in obj.values():
            found.extend(find_matches(v, depth+1))
    return found

raw_matches = find_matches(fixtures)
print(f"\nPartidos encontrados en fixtures: {len(raw_matches)}")

# Filtrar por Liga Profesional
lp_matches = []
for m in raw_matches:
    league_name = ""
    # Buscar nombre de liga
    for key in ["leagueName", "league", "tournamentName", "competition"]:
        if key in m:
            league_name = str(m[key])
            break
    # Buscar en estructura anidada
    if not league_name:
        league_info = m.get("leagueId", "")
        parent_league = m.get("parentLeagueId", "")

    # Filtrar por liga profesional argentina (ID 112 o nombre)
    if "profesional" in league_name.lower() or "argentina" in league_name.lower() or \
       m.get("leagueId") == 112 or m.get("parentLeagueId") == 112:
        lp_matches.append(m)

print(f"Partidos de Liga Profesional: {len(lp_matches)}")

# Si no se filtró correctamente, mostrar muestra de los datos
if not lp_matches and raw_matches:
    print("\nMuestra de un partido para inspección:")
    print(json.dumps(raw_matches[0], indent=2, ensure_ascii=False)[:1000])
