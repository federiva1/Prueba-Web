"""
Intentar obtener datos del partido desde:
1. window.__NEXT_DATA__ (Next.js SSR)
2. endpoint /api/data/ltc
3. endpoint /api/data/leagueDataForMatch
"""
import json
import time
import re
from playwright.sync_api import sync_playwright

MATCH_URL = "https://www.fotmob.com/matches/argentinos-juniors-vs-sarmiento/aem1p1z#5101880"
MATCH_ID = 5101880

ltc_data = {}
league_match_data = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="es-AR",
        viewport={"width": 1280, "height": 900}
    )
    page = context.new_page()

    def on_resp(response):
        url = response.url
        if "ltc" in url and str(MATCH_ID) in url and response.status == 200:
            try:
                ltc_data["data"] = response.json()
                ltc_data["url"] = url
                print(f"LTC capturado: {url}")
            except Exception as e:
                print(f"LTC parse error: {e}")
        if "leagueDataForMatch" in url and response.status == 200:
            try:
                league_match_data["data"] = response.json()
                print(f"leagueDataForMatch capturado: {url}")
            except Exception as e:
                print(f"leagueDataForMatch error: {e}")

    page.on("response", on_resp)
    page.goto(MATCH_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(8)

    # Intentar extraer __NEXT_DATA__
    print("\nBuscando __NEXT_DATA__...")
    next_data = page.evaluate("() => { try { return window.__NEXT_DATA__; } catch(e) { return null; } }")
    if next_data:
        with open("next_data.json", "w", encoding="utf-8") as f:
            json.dump(next_data, f, ensure_ascii=False, indent=2)
        print(f"__NEXT_DATA__ encontrado! Keys: {list(next_data.keys())[:10]}")
    else:
        print("No hay __NEXT_DATA__")

    # Intentar extraer desde script tags
    print("\nBuscando datos en script tags...")
    scripts = page.locator("script[type='application/json']").all()
    print(f"Scripts JSON encontrados: {len(scripts)}")
    for j, script in enumerate(scripts[:3]):
        try:
            content = script.inner_text()[:200]
            print(f"  Script {j}: {content[:100]}...")
        except:
            pass

    # Intentar extraer el estado inicial desde el HTML
    html = page.content()
    # Buscar patrones de datos embebidos
    match_patterns = [
        r'"matchDetails":\s*\{',
        r'"playerStats":\s*\{',
        r'"lineup":\s*\{',
    ]
    for pat in match_patterns:
        m = re.search(pat, html)
        if m:
            print(f"Patrón encontrado en HTML: {pat} (pos {m.start()})")

    browser.close()

# Guardar lo que se capturó
if ltc_data:
    with open("ltc_data.json", "w", encoding="utf-8") as f:
        json.dump(ltc_data, f, ensure_ascii=False, indent=2)
    print(f"\nLTC data guardado. Keys: {list(ltc_data['data'].keys())[:10]}")
else:
    print("\nNo se capturó LTC data")

if league_match_data:
    with open("league_match_data.json", "w", encoding="utf-8") as f:
        json.dump(league_match_data, f, ensure_ascii=False, indent=2)
    print(f"leagueDataForMatch guardado. Keys: {list(league_match_data['data'].keys())[:10]}")
