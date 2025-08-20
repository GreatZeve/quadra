# Quadra
Aplicación para ubicar y calificar puestos de comida callejera. Construida con **Python + Flask** y **Supabase** (Auth, Postgres, Storage). Front con HTML/CSS/Leaflet.

## Estructura del proyecto

quadra/
├─ app.py
├─ config.py
├─ supabase_client.py
├─ models.py
├─ requirements.txt
├─ README.md
├─ .env.example
├─ static/
│ ├─ css/
│ │ └─ styles.css
│ └─ js/
│ └─ main.js
└─ templates/
├─ base.html
├─ index_public.html # 1. Inicio (sin sesión)
├─ index_private.html # 2. Inicio (con sesión)
├─ login.html # 3. Inicio de sesión
└─ register.html # 4. Registro de usuario

## Características
- Publicación de puestos con ubicación (mapa Leaflet) y foto (Supabase Storage)
- Listado de últimos puestos
- Calificaciones y comentarios
- Autenticación por email/contraseña (Supabase Auth)

## Stack
- **Backend:** Python 3.11+, Flask 3
- **DB/Auth/Storage:** Supabase
- **Frontend:** HTML, CSS, Leaflet (CDN)
- **Infra:** GitHub (repo), opcional Render/Heroku para deploy

## Requisitos previos
- Python 3.11+
- Cuenta de Supabase con un proyecto creado

## Configuración rápida
1. Clona el repo y entra al directorio
   ```bash
   git clone https://github.com/tu-usuario/quadra.git
   cd quadra
   ```
2. Crea y activa un entorno virtual
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scriptsctivate
   ```
3. Instala dependencias
   ```bash
   pip install -r requirements.txt
   ```
4. Copia `.env.example` a `.env` y coloca tus credenciales de Supabase.
5. Crea en Supabase:
   - Tablas (ver más abajo) y bucket de Storage llamado `places`.

## Ejecutar en desarrollo
```bash
flask --app app run --debug
```
App en: http://127.0.0.1:5000

## Tablas y políticas (Supabase)

### SQL de tablas
```sql
-- Tabla: places
create table if not exists public.places (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  name text not null,
  description text not null,
  lat double precision not null,
  lng double precision not null,
  photo_url text,
  created_at timestamptz not null default now()
);

-- Tabla: ratings
create table if not exists public.ratings (
  id uuid primary key default gen_random_uuid(),
  place_id uuid not null references public.places(id) on delete cascade,
  user_id uuid not null,
  rating int not null check (rating between 1 and 5),
  comment text,
  created_at timestamptz not null default now()
);
```

### RLS (Row Level Security)
```sql
alter table public.places enable row level security;
alter table public.ratings enable row level security;

-- Cualquiera autenticado puede leer todo
create policy "read_places" on public.places for select using (true);
create policy "read_ratings" on public.ratings for select using (true);

-- Solo el usuario autenticado puede insertar sus propios registros
create policy "insert_own_place" on public.places for insert with check (auth.uid() = user_id);
create policy "insert_own_rating" on public.ratings for insert with check (auth.uid() = user_id);

-- (Opcional) permitir update/delete sólo al dueño
create policy "update_own_place" on public.places for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "delete_own_place" on public.places for delete using (auth.uid() = user_id);
```

### Storage
- Crea un bucket público llamado `places`.
- Reglas públicas de lectura y escritura autenticada.

## Variables de entorno
- `SECRET_KEY` — clave para sesiones Flask
- `SUPABASE_URL` y `SUPABASE_ANON_KEY` — desde tu proyecto Supabase

## Licencia
MIT