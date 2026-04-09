import json
import urllib.request

TEAM_ID = 10086

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.fotmob.com/",
}

url = f"https://www.fotmob.com/api/data/teams?id={TEAM_ID}&ccode3=ARG"
print(f"Consultando: {url}")

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode("utf-8"))

# Guardar raw para inspección
with open("team_api_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Guardado team_api_raw.json")

# Parsear squad
players = []
seen_ids = set()
squad_list = data.get("squad", {}).get("squad", [])
for group in squad_list:
    role = group.get("title", "")
    for member in group.get("members", []):
        pid = str(member.get("id", ""))
        if pid in seen_ids:
            continue
        seen_ids.add(pid)
        players.append({
            "id": pid,
            "name": member.get("name", ""),
            "position": role,
            "nationality": member.get("ccode", ""),
            "age": member.get("age", ""),
            "shirt": str(member.get("shirt", ""))
        })

print(f"\nPlantel limpio: {len(players)} jugadores\n")
for p in players:
    print(f"  [{p['shirt']:>2}] [{p['position']:>12}] {p['name']}")

result = {
    "team_id": TEAM_ID,
    "team_name": "Argentinos Juniors",
    "players": players
}
with open("plantel.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"\nPlantel guardado en plantel.json")
