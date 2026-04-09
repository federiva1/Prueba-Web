# keys_fotmob.py
# Mapeo universal: nombre en español → key interno de FotMob API
# No depende del equipo. Aplica para cualquier club.

KEY_MAP = {
    "Minutos jugados":                "Minutes played",
    "Goles":                          "Goals",
    "Asistencias":                    "Assists",
    "xG":                             "Expected goals (xG)",
    "xA":                             "Expected assists (xA)",
    "xG + xA":                        "xG + xA",
    "Acciones defensivas":            "Defensive actions",
    "xGOT":                           "Expected goals on target (xGOT)",
    "Disparos a puerta":              "Shots on target",
    "Regates realizados":             "Successful dribbles",
    "Grandes oportunidades perdidas": "Big chances missed",
    "Toques en el área rival":        "Touches in opposition box",
    "Fueras de juego":                "Offsides",
    "Toques":                         "Touches",
    "Pases precisos":                 "Accurate passes",
    "Oportunidades creadas":          "Chances created",
    "Pases en el último tercio":      "Passes into final third",
    "Centros precisos":               "Accurate crosses",
    "Tiros largos precisos":          "Accurate long balls",
    "Entradas":                       "Tackles",
    "Interceptaciones":               "Interceptions",
    "Bloqueos":                       "Blocks",
    "Recuperaciones":                 "Recoveries",
    "Despejes":                       "Clearances",
    "Despeje de cabeza":              "Headed clearance",
    "Regateado":                      "Dribbled past",
    "Duelos ganados":                 "Duels won",
    "Duelos perdidos":                "Duels lost",
    "Duelo terrestre ganado":         "Ground duels won",
    "Aéreo ganado":                   "Aerial duels won",
    "Faltas":                         "Fouls committed",
    "Faltas recibidas":               "Was fouled",
    "Paradas":                        "Saves",
    "Goles en contra":                "Goals conceded",
    "xGOT recibidos":                 "xGOT faced",
    "Goles evitados":                 "Goals prevented",
    "El portero actuó como líbero":   "Acted as sweeper",
    "Salida por alto":                "High claim",
}

# Secciones y columnas — respetan el orden de FotMob "Estad. Jugador"
# Formato: (nombre_seccion, color_oscuro, color_claro, [columnas_en_español])
SECTIONS = [
    ("Top Estadísticas", "1F4E79", "2E75B6", [
        "Minutos jugados", "Goles", "Asistencias",
        "xG", "xA", "xG + xA", "Acciones defensivas",
    ]),
    ("Ataque", "833C00", "C55A11", [
        "Goles", "xG", "xGOT", "Disparos a puerta",
        "Regates realizados", "Grandes oportunidades perdidas",
        "Toques en el área rival", "Fueras de juego",
    ]),
    ("Pases", "1F6B3B", "2E8B57", [
        "Toques", "Pases precisos", "Asistencias", "xA",
        "Oportunidades creadas", "Pases en el último tercio",
        "Centros precisos", "Tiros largos precisos",
    ]),
    ("Defensa", "375623", "548235", [
        "Acciones defensivas", "Entradas", "Interceptaciones", "Bloqueos",
        "Recuperaciones", "Despejes", "Despeje de cabeza", "Regateado",
    ]),
    ("Duelos", "4B2B6B", "7030A0", [
        "Duelos ganados", "Duelos perdidos", "Duelo terrestre ganado",
        "Aéreo ganado", "Faltas", "Faltas recibidas",
        "Regates realizados", "Entradas",
    ]),
    ("Portero", "1C3A5C", "2F5496", [
        "Paradas", "Goles en contra", "xGOT recibidos", "Goles evitados",
        "El portero actuó como líbero", "Salida por alto",
        "Tiros largos precisos", "Pases precisos",
    ]),
]
