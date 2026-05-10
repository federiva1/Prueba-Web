# Guía para adaptar este proyecto a un nuevo equipo

Este proyecto es una **SPA (Single Page App)** de fan engagement para un club de fútbol.  
Todo el código vive en un solo archivo `index.html` con CSS y JS inline.

---

## Qué hace la app

| Sección | Descripción |
|---|---|
| **Arma tu formación** | El usuario arrastra jugadores del plantel a la cancha, envía su formación a Supabase y puede descargarla como imagen |
| **Ver la cancha rival** | Muestra el 11 del rival posicionado en una cancha espejo |
| **Equipos de la gente** | Feed con todas las formaciones enviadas, con likes/dislikes |
| **Puntuá el partido** | El usuario puntúa del 1 al 10 a cada jugador que jugó; se guarda en Supabase y se muestran los promedios en formato podio |
| **Fechas** | Panel lateral con el historial de fechas; las anteriores son solo lectura |
| **Tabla** | Botón flotante que abre la tabla de posiciones de la liga (iframe embed o link) |

---

## Stack técnico

- **Frontend:** HTML + CSS + JS puro (sin frameworks), todo en un solo `index.html`
- **Base de datos:** [Supabase](https://supabase.com) (PostgreSQL con REST API)
- **Hosting:** GitHub Pages (repo público, rama `main`, carpeta raíz)
- **Fotos de jugadores:** PNGs locales en carpetas dentro del repo, nombrados por FotMob ID
- **Imágenes de descarga:** `html2canvas` vía CDN
- **Fuentes:** Google Fonts (Bebas Neue, Barlow Condensed, DM Sans)
- **Analytics:** Google Analytics (gtag.js) — opcional

---

## Estructura de archivos del repo

```
/
├── index.html                        ← toda la app
├── fotos/                            ← fotos del equipo local (nombre: {fotmob_id}.png)
├── fotos{NombreRival}/               ← fotos del rival (ej: fotosIndependienteRivadavia/)
├── escudos/                          ← escudos de equipos (nombre: {slug}.png)
│     ├── independienterivadavia.png
│     ├── banfield.png
│     └── ...
├── fotosDTs/                         ← imágenes para el carrusel del panel izquierdo (dt1.png ... dtN.png)
└── fotosPuntajes/                    ← imágenes para el carrusel del panel derecho (p1.png ... pN.png)
```

> **Los escudos se referencian así:** `/escudos/{escudoFile}.png`  
> donde `escudoFile` es el campo del array `FECHAS` (sin espacios, sin tildes, todo minúscula).

---

## Supabase: tablas necesarias

### Tabla `formaciones`
Guarda las formaciones enviadas por los usuarios.

```sql
CREATE TABLE formaciones (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  jugadores jsonb,        -- array de {num, name, fid, x, y}
  rival text,             -- nombre del rival (filtra por fecha)
  device_id text,         -- identificador único del dispositivo
  likes integer DEFAULT 0,
  dislikes integer DEFAULT 0
);
```

### Tabla `puntajes`
Guarda los puntajes que cada usuario le pone a los jugadores.

```sql
CREATE TABLE puntajes (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now(),
  rival text,             -- nombre del rival (filtra por fecha)
  puntajes jsonb          -- objeto {num_jugador: puntaje} ej: {"25": 8, "10": 6}
);
```

> **RLS:** Ambas tablas deben tener RLS habilitado con política de `INSERT` y `SELECT` públicos (anon key).  
> La `anon key` de Supabase se usa directamente en el JS (es pública por diseño).

---

## Constantes a cambiar en `index.html`

### 1. Conexión a Supabase
```js
const SUPABASE_URL = 'https://TU_PROYECTO.supabase.co';
const SUPABASE_KEY = 'TU_ANON_KEY';
```

### 2. Fecha actual (actualizar cada partido)
```js
const RIVAL = 'Nombre del Rival';          // exacto, se usa como filtro en DB
const LS_KEY = 'club_vs_rival';            // clave única por partido en localStorage
const LS_FORMATION_KEY = 'club_vs_rival_formacion';
const LS_SCORES_KEY = 'club_vs_rival_puntajes';
const SCORES_ENABLED = false;              // → true cuando termina el partido
```

> ⚠️ El `LS_KEY` debe ser **único por partido**. Si se reutiliza, el usuario no puede votar de nuevo.

### 3. Plantel que jugó (llenar después del partido)
```js
const playedSquad = [
  {num:10, name:'Jugador', fid:123456, tipo:'titular'},
  {num:9,  name:'Suplente', fid:654321, tipo:'suplente'},
  // ...
];
```
- `fid` = FotMob player ID (se usa para la foto: `/fotos/{fid}.png`)
- `tipo` = `'titular'` o `'suplente'` (define la sección en el podio)

### 4. Historial de fechas
```js
const FECHAS = [
  {
    num: 15,                              // número de fecha
    rival: 'Nombre del Rival',            // debe coincidir con RIVAL
    escudoFile: 'nombrErival',            // slug para /escudos/{slug}.png
    isCurrent: true                       // solo una fecha tiene true
  },
  {
    num: 14,
    rival: 'Rival Anterior',
    escudoFile: 'rivalanterior',
    isCurrent: false,
    playedSquad: [ /* misma estructura que arriba */ ]
  }
];
```

### 5. Plantel del equipo local
```js
const squad = [
  {num:1, name:'Arquero', fid:123456},
  // ... todos los jugadores disponibles para armar la formación
];
```

### 6. Plantel del rival (para "Ver rival")
```js
const banfieldSquad = [   // renombrarlo si querés, es solo una variable
  {num:1, name:'Arquero', fid:999999, x:49.8, y:5.8},
  // x e y son porcentajes de posición en la cancha (0-100)
  // x=50 es el centro horizontal, y=5 es cerca del arco propio
];
```

### 7. Arqueros, lesionados y suspendidos
```js
const GOALKEEPERS = [1, 12, 32];     // números de arqueros (no se pueden poner de campo)
const INJURED    = [9, 22];           // aparecen con 🏥, no se pueden arrastrar
const SUSPENDED  = [16];              // aparecen con 🟨, no se pueden arrastrar
```

### 8. Rutas de fotos
```js
const FOTO   = id => `/fotos/${id}.png`;                      // fotos del equipo local
const FOTO_B = id => `/fotosNombreRival/${id}.png`;           // fotos del rival
```

### 9. Carrusel de imágenes en el home
```js
const dtSlides = ['/fotosDTs/dt1.png', ...];     // panel izquierdo (ej: fotos del DT/cuerpo técnico)
const pSlides  = ['/fotosPuntajes/p1.png', ...]; // panel derecho (ej: fotos de jugadores/estadio)
```

### 10. Colores del equipo rival
```css
:root {
  --rojo: #e53935;           /* color principal del club local */
  --azul-rival: #1565c0;     /* color del botón "Ver rival" — cambiar por el del rival */
}
```

---

## Flujo por partido (checklist semanal)

### Antes del partido
- [ ] Actualizar `RIVAL`, `LS_KEY`, `LS_FORMATION_KEY`, `LS_SCORES_KEY`
- [ ] Mover la fecha anterior al array `FECHAS` con `isCurrent: false` y su `playedSquad`
- [ ] Agregar la fecha nueva al tope de `FECHAS` con `isCurrent: true`
- [ ] Actualizar `banfieldSquad` con el 11 probable del rival (y sus posiciones en cancha)
- [ ] Subir fotos del rival a `/fotosNombreRival/` y actualizar `FOTO_B`
- [ ] Agregar el escudo del rival a `/escudos/` con el slug correcto
- [ ] Actualizar `INJURED` y `SUSPENDED` con el estado del plantel
- [ ] Mantener `SCORES_ENABLED = false`
- [ ] Limpiar los votos de la fecha anterior en Supabase: `DELETE FROM puntajes WHERE rival = 'Rival Anterior';` *(solo si querés resetear — normalmente los datos viejos quedan como historial)*
- [ ] Push a GitHub → producción actualizada

### Después del partido
- [ ] Llenar `playedSquad` con los jugadores que efectivamente jugaron
- [ ] Cambiar `SCORES_ENABLED = true`
- [ ] Push a GitHub

---

## Cómo encontrar los FotMob IDs

1. Entrá a `fotmob.com` y buscá el jugador
2. La URL del perfil tiene el formato: `/players/{FID}/overview/nombre`
3. Ese número es el `fid` a usar para la foto

Las fotos se descargan desde `fotmob.com` (los archivos PNG del perfil del jugador) o se generan con un scraper.

---

## Cómo encontrar el Team ID y League ID (para el scraper de estadísticas)

- **Team ID:** URL del equipo en FotMob → `/teams/{TEAM_ID}/overview/nombre`
- **League ID:** URL de la liga → `/leagues/{LEAGUE_ID}/overview/nombre`

---

## Cómo funciona la identificación de usuario

- Al primer acceso se genera un `device_id` (UUID v4) y se guarda en `localStorage` con la clave `aaaj_device_id` *(cambiar el prefijo para el nuevo club)*
- Este ID se envía con cada formación para identificar la propia en el feed
- **No es un sistema de login** — el usuario puede borrar su localStorage y votar de nuevo

---

## Consideraciones al adaptar a otro club

| Qué cambiar | Dónde |
|---|---|
| Nombre del club en el `<title>` y encabezados | HTML, principio del `<head>` y `#header` |
| Color principal (`--rojo`) | `:root` en el CSS |
| Prefijo de localStorage (`aaaj_`) | Todas las constantes `LS_*` y `aaaj_device_id` |
| Google Analytics ID | `gtag('config', 'G-XXXXXX')` |
| Carpeta de fotos del equipo (`/fotos/`) | Constante `FOTO` y la carpeta física |
| Textos en la UI | Buscar "Argentinos", "AAAJ", "Bicho" en el HTML |
