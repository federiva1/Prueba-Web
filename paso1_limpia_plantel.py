import json
import time
from playwright.sync_api import sync_playwright

def get_squad_via_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            locale="es-AR",
            viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()

        team_id = 10086
        squad_api_data = {}

        def handle_response(response):
            if f"teams?id={team_id}" in response.url:
                try:
                    squad_api_data["raw"] = response.json()
                    print(f"API capturada: {response.url}")
                except:
                    pass

        page.on("response", handle_response)
        url = f"https://www.fotmob.com/es/teams/{team_id}/squad/argentinos-juniors"
        print(f"Navegando a: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)
        browser.close()

        return squad_api_data.get("raw", {})

def parse_squad(api_data):
    players = []
    seen_ids = set()

    squad_list = api_data.get("squad", [])
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
                "shirt": member.get("shirt", "")
            })

    return players

if __name__ == "__main__":
    print("=== Paso 1: Plantel de Argentinos Juniors ===\n")
    raw = get_squad_via_api()

    if not raw:
        print("No se capturó la API. Cargando desde plantel.json previo...")
        with open("plantel.json", encoding="utf-8") as f:
            prev = json.load(f)
        # Deduplicar por ID
        seen = set()
        players = []
        for p in prev["players"]:
            if p["id"] not in seen and p["id"]:
                seen.add(p["id"])
                players.append({"id": p["id"], "name": p["name"], "position": p.get("position", "")})
    else:
        players = parse_squad(raw)

    print(f"\nPlantel limpio: {len(players)} jugadores\n")
    for p in players:
        print(f"  [{p.get('shirt','?'):>2}] [{p.get('position',''):>10}] {p['name']} (ID: {p['id']})")

    result = {
        "team_id": 10086,
        "team_name": "Argentinos Juniors",
        "players": players
    }
    with open("plantel.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nPlantel guardado en plantel.json")
