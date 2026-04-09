"""
Visitar un partido en el browser e interceptar qué endpoint usa FotMob
para datos de partido y estadísticas de jugadores.
"""
import time
from playwright.sync_api import sync_playwright

TEST_MATCH_URL = "https://www.fotmob.com/matches/argentinos-juniors-vs-sarmiento/aem1p1z#5101880"

captured = []

def handle_response(response):
    url = response.url
    if "fotmob.com/api" in url:
        captured.append(url)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        locale="es-AR",
        viewport={"width": 1280, "height": 900}
    )
    page = context.new_page()
    page.on("response", handle_response)

    print(f"Navegando a: {TEST_MATCH_URL}")
    page.goto(TEST_MATCH_URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(8)

    # Intentar hacer clic en "Estadísticas" o "Stats"
    for text in ["Estadísticas", "Estad.", "Stats", "Player Stats", "Estad. Jugador"]:
        try:
            tab = page.locator(f"text={text}").first
            if tab.is_visible(timeout=2000):
                tab.click()
                time.sleep(3)
                print(f"Clic en: {text}")
                break
        except:
            pass

    browser.close()

print("\n=== APIs capturadas ===")
for url in sorted(set(captured)):
    print(f"  {url}")
