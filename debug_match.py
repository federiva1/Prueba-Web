"""Debug: navegar a un partido y ver todos los eventos de response."""
import json
import time
from playwright.sync_api import sync_playwright

MATCH_URL = "https://www.fotmob.com/matches/argentinos-juniors-vs-sarmiento/aem1p1z#5101880"
MATCH_ID = 5101880

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="es-AR",
        viewport={"width": 1280, "height": 900}
    )
    page = context.new_page()

    captured = {}

    def on_resp(response):
        url = response.url
        if "fotmob.com/api" in url:
            status = response.status
            print(f"  API [{status}]: {url}")
            if f"matchDetails?matchId={MATCH_ID}" in url and status == 200:
                try:
                    captured["data"] = response.json()
                    print(f"  >>> JSON capturado! Keys: {list(captured['data'].keys())[:5]}")
                except Exception as e:
                    print(f"  >>> Error parseando JSON: {e}")

    page.on("response", on_resp)

    print(f"Navegando a: {MATCH_URL}\n")
    page.goto(MATCH_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(8)

    browser.close()

print(f"\nCapturado: {'SÍ' if 'data' in captured else 'NO'}")
if "data" in captured:
    with open("match_debug.json", "w", encoding="utf-8") as f:
        json.dump(captured["data"], f, ensure_ascii=False, indent=2)
    print("Guardado en match_debug.json")
    print("Top-level keys:", list(captured["data"].keys()))
