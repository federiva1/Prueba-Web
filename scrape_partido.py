# scrape_partido.py
# Navega a la página de un partido en FotMob, extrae los datos embebidos
# en __NEXT_DATA__ (Next.js SSR) y los guarda como JSON.
#
# Uso:
#   python scrape_partido.py <url_partido> <archivo_salida.json>
#
# Ejemplo:
#   python scrape_partido.py "https://www.fotmob.com/matches/aj-vs-sarmiento/xxx#5101880" "nd_sarmiento.json"

import sys
import json
import time
from playwright.sync_api import sync_playwright

if len(sys.argv) != 3:
    print("Uso: python scrape_partido.py <url_partido> <archivo_salida.json>")
    sys.exit(1)

url    = sys.argv[1]
output = sys.argv[2]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=150)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="es-AR",
        viewport={"width": 1280, "height": 900}
    )
    page = context.new_page()
    print(f"Navegando a: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    time.sleep(5)
    nd = page.evaluate("() => window.__NEXT_DATA__")
    browser.close()

if not nd:
    print("ERROR: no se encontró __NEXT_DATA__ en la página")
    sys.exit(1)

with open(output, "w", encoding="utf-8") as f:
    json.dump(nd, f, ensure_ascii=False, indent=2)

try:
    ps = nd["props"]["pageProps"]["content"]["playerStats"]
    print(f"OK — Guardado: {output} | Jugadores en playerStats: {len(ps)}")
except KeyError:
    print(f"WARN — Guardado: {output} | No se encontró playerStats (el partido puede no tener stats)")
