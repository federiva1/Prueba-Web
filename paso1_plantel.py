import json
import time
from playwright.sync_api import sync_playwright

def get_squad():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="es-AR",
            viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()

        # --- Interceptar API de la liga para obtener el ID de Argentinos Juniors ---
        print("Consultando API de la liga...")
        api_data = {}
        def handle_response(response):
            if "api/leagues" in response.url and "id=112" in response.url:
                try:
                    api_data["league"] = response.json()
                except:
                    pass

        page.on("response", handle_response)
        page.goto("https://www.fotmob.com/es/leagues/112/overview/liga-profesional",
                  wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        team_id = None
        team_name = None

        if "league" in api_data:
            league = api_data["league"]
            # Buscar Argentinos Juniors en los datos de la liga
            try:
                for team in league.get("table", [{}])[0].get("data", {}).get("table", {}).get("all", []):
                    if "argentinos" in team.get("name", "").lower():
                        team_id = team.get("id")
                        team_name = team.get("name")
                        print(f"Encontrado via tabla: {team_name} (ID: {team_id})")
                        break
            except Exception as e:
                print(f"Error buscando en tabla: {e}")

            if not team_id:
                # Buscar en otra estructura
                try:
                    for item in str(league).split("argentinos"):
                        # buscar id cerca de "argentinos"
                        pass
                except:
                    pass

        # Fallback: buscar link de equipo en la página
        if not team_id:
            print("Buscando link del equipo en la página...")
            team_links = page.locator("a[href*='/teams/']").all()
            for link in team_links:
                href = link.get_attribute("href") or ""
                text = link.inner_text().strip()
                if "argentinos" in href.lower() or "argentinos" in text.lower():
                    team_id_from_href = href.split("/teams/")[1].split("/")[0] if "/teams/" in href else None
                    print(f"Link encontrado: {href} | Texto: {text}")
                    if team_id_from_href:
                        team_id = team_id_from_href
                        team_name = "Argentinos Juniors"
                        break

        if not team_id:
            # Buscar directamente en el HTML
            html = page.content()
            import re
            # Buscar patrón /teams/XXXX/argentinos
            matches = re.findall(r'/teams/(\d+)/argentinos', html)
            if matches:
                team_id = matches[0]
                team_name = "Argentinos Juniors"
                print(f"ID encontrado en HTML: {team_id}")

        if not team_id:
            print("ERROR: No se pudo encontrar el ID de Argentinos Juniors")
            browser.close()
            return [], ""

        print(f"\nEquipo: {team_name} | ID: {team_id}")

        # --- Navegar a la página del equipo ---
        team_url = f"https://www.fotmob.com/es/teams/{team_id}/squad/argentinos-juniors"
        print(f"Navegando a: {team_url}")

        squad_data = {}
        def handle_squad_response(response):
            if f"teams?id={team_id}" in response.url or f"/teams/{team_id}" in response.url:
                try:
                    squad_data["data"] = response.json()
                    print(f"  API de equipo capturada: {response.url}")
                except:
                    pass

        page.on("response", handle_squad_response)
        page.goto(team_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        players = []

        # Intentar extraer de la API
        if "data" in squad_data:
            data = squad_data["data"]
            try:
                squad_section = data.get("squad", [])
                for group in squad_section:
                    for member in group.get("members", []):
                        players.append({
                            "name": member.get("name", ""),
                            "id": str(member.get("id", "")),
                            "position": member.get("role", {}).get("fallback", "")
                        })
                print(f"Jugadores extraídos de API: {len(players)}")
            except Exception as e:
                print(f"Error parseando API de squad: {e}")

        # Fallback: extraer del DOM
        if not players:
            print("Extrayendo jugadores del DOM...")
            player_links = page.locator("a[href*='/players/']").all()
            seen = set()
            for el in player_links:
                name = el.inner_text().strip()
                href = el.get_attribute("href") or ""
                if name and "/players/" in href and name not in seen:
                    parts = href.split("/")
                    try:
                        pid = parts[parts.index("players") + 1]
                    except (ValueError, IndexError):
                        pid = ""
                    players.append({"name": name, "id": pid, "position": "", "href": href})
                    seen.add(name)

        actual_url = page.url
        browser.close()
        return players, actual_url

if __name__ == "__main__":
    players, team_url = get_squad()
    print(f"\n{'='*50}")
    print(f"Jugadores encontrados: {len(players)}")
    for p in players:
        pos = p.get('position', '')
        print(f"  [{pos}] {p['name']} (ID: {p['id']})")

    with open("plantel.json", "w", encoding="utf-8") as f:
        json.dump({"players": players, "team_url": team_url}, f, ensure_ascii=False, indent=2)
    print(f"\nPlantel guardado en plantel.json")
