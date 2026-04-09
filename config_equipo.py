# config_equipo.py
# Cambiá estos valores para usar el scraper con cualquier equipo de FotMob.

# ── Datos del equipo ──────────────────────────────────────────────────────────

TEAM_ID   = 10086              # ID numérico del equipo en FotMob
TEAM_NAME = "Argentinos Juniors"

# Cómo encontrar el TEAM_ID de cualquier equipo:
#   1. Entrá a fotmob.com y navegá al perfil del equipo
#   2. La URL tiene el formato: /teams/TEAM_ID/overview/nombre-del-equipo
#   3. Copiá el número que aparece en esa posición
#   Ejemplo: /teams/10086/overview/argentinos-juniors  →  TEAM_ID = 10086

# ── Liga ─────────────────────────────────────────────────────────────────────

LEAGUE_ID   = 112              # ID de la liga en FotMob (Liga Profesional Argentina)
LEAGUE_NAME = "Liga Profesional"
SEASON_NAME = "Apertura 2026"  # Nombre del torneo a filtrar en fixtures

# Cómo encontrar el LEAGUE_ID:
#   La URL de la liga tiene el formato: /leagues/LEAGUE_ID/overview/nombre-liga
#   Ejemplo: /leagues/112/overview/liga-profesional  →  LEAGUE_ID = 112
