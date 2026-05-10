"""Scrapea la tabla de FotMob (Liga Profesional 112) y genera tabla_data.json
con la estructura que el index.html espera: [zonaA, zonaB, anual, promedios]
donde cada equipo es {rank, team:{id,name}, points, goalsDiff, form, all:{...}}.

Uso:
  1) curl -A "Mozilla/5.0" "https://www.fotmob.com/es/leagues/112/overview/liga-profesional" -o fotmob_tabla.html
  2) python scrape_tabla.py
"""
import json, re, sys

with open('fotmob_tabla.html', 'r', encoding='utf-8') as f:
    html = f.read()
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.DOTALL)
if not m:
    sys.exit('No __NEXT_DATA__ found')
data = json.loads(m.group(1))
table_root = data['props']['pageProps']['table'][0]
tables = table_root['data']['tables']
team_form = table_root.get('teamForm', {})

def team_form_str(team_id):
    raw = team_form.get(str(team_id), [])
    return ''.join(item.get('resultString', '') for item in raw[:5])

def map_team(row):
    gf, ga = (0, 0)
    if row.get('scoresStr'):
        parts = row['scoresStr'].split('-')
        if len(parts) == 2:
            gf, ga = int(parts[0]), int(parts[1])
    return {
        'rank': row['idx'],
        'team': {'id': row['id'], 'name': row['name']},
        'points': row['pts'],
        'goalsDiff': row['goalConDiff'],
        'form': team_form_str(row['id']),
        'all': {
            'played': row['played'],
            'win': row['wins'],
            'draw': row['draws'],
            'lose': row['losses'],
            'goals': {'for': gf, 'against': ga},
        },
    }

# tables[2] = Apertura - Group A, tables[3] = Apertura - Group B
zonaA_raw = tables[2]['table']['all']
zonaB_raw = tables[3]['table']['all']
zonaA = [map_team(r) for r in zonaA_raw]
zonaB = [map_team(r) for r in zonaB_raw]

# Anual = todos los equipos sortados por puntos (descendente)
anual_combined = [map_team(r) for r in zonaA_raw + zonaB_raw]
anual_combined.sort(key=lambda t: (-t['points'], -t['goalsDiff'], -t['all']['goals']['for']))
for i, t in enumerate(anual_combined, start=1):
    t['rank'] = i

# Promedios: lo carga el usuario manualmente desde Promiedos
promedios_placeholder = []

result = [zonaA, zonaB, anual_combined, promedios_placeholder]

with open('tabla_data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'OK: zonaA={len(zonaA)} zonaB={len(zonaB)} anual={len(anual_combined)} promedios={len(promedios_placeholder)}')
print('Top 3 zona B:')
for t in zonaB[:3]:
    print(f'  {t["rank"]}. {t["team"]["name"]} ({t["team"]["id"]}) - {t["points"]} pts - form: {t["form"]}')
