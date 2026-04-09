import json
import pandas as pd

TEAM_ID = 10086
OUTPUT_FILE = r"C:\Users\feder\OneDrive\Escritorio\argentinos_vs_sarmiento.xlsx"

with open("next_data.json", encoding="utf-8") as f:
    nd = json.load(f)

ps = nd["props"]["pageProps"]["content"]["playerStats"]

rows = []
for pid, p in ps.items():
    if str(p.get("teamId", "")) != str(TEAM_ID):
        continue

    row = {
        "Fecha": "2026-01-26",
        "Rival": "Sarmiento",
        "Local_Visitante": "Local",
        "Resultado": "1 - 0",
        "Jugador": p.get("name", ""),
        "Camiseta": p.get("shirtNumber", ""),
        "Jugador_ID": pid,
    }

    for section in p.get("stats", []):
        for stat_name, stat_obj in section.get("stats", {}).items():
            if stat_name == "Shotmap":
                continue
            stat = stat_obj.get("stat", {})
            value = stat.get("value", "")
            total = stat.get("total", None)
            row[stat_name] = f"{value}/{total}" if total is not None else value

    rows.append(row)

print(f"Jugadores AJ encontrados: {len(rows)}")

df = pd.DataFrame(rows)
id_cols = ["Fecha", "Rival", "Local_Visitante", "Resultado", "Jugador", "Camiseta", "Jugador_ID"]
stat_cols = [c for c in df.columns if c not in id_cols]
df = df[id_cols + stat_cols].sort_values("Jugador").reset_index(drop=True)

df.to_excel(OUTPUT_FILE, index=False, sheet_name="vs Sarmiento")
print(f"Excel guardado: {OUTPUT_FILE}")
print(f"Columnas de estadísticas ({len(stat_cols)}):")
for c in stat_cols:
    print(f"  - {c}")
print()
print(df[["Jugador", "Camiseta", "FotMob rating", "Minutes played", "Goals", "Assists"]].to_string(index=False))
