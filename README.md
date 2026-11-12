# Cazador de Pigmentos - Backend

juego interactivo de combinacion de colores

## Tecnologías usadas

- Django
- Python

## Instalación local

### Requisitos

- Python 3.12 o posterior.
- Git.
- Docker Engine con el complemento `docker compose` para usar MySQL en un contenedor. También se puede usar SQLite sin instalar un servidor de base de datos.
- En Debian/Ubuntu, las herramientas necesarias para compilar `mysqlclient`:

```bash
sudo apt update
sudo apt install -y build-essential pkg-config default-libmysqlclient-dev
```

### Obtener el proyecto e instalar dependencias

```bash
git clone <URL_DEL_REPOSITORIO>
cd 2026-III-Cazador-de-Pigmentos
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

En Windows, activa el entorno con `.venv\\Scripts\\activate` en CMD o `.venv\\Scripts\\Activate.ps1` en PowerShell. Ejecuta los comandos `python` y `pip` siguientes con el entorno activado.
Linux/macOS: source .venv/bin/activate

Edita `.env` y define `DJANGO_SECRET_KEY` con una clave aleatoria privada.

### Usar MySQL con Docker

Arranca un servidor MySQL 8.4 con una base y usuario de desarrollo. Reemplaza las contraseñas de ejemplo por valores locales propios; usa los mismos valores en `.env`:

```bash
docker run -d \\
  --name cazadores-mysql \\
  --restart unless-stopped \\
  -p 3306:3306 \\
  -e MYSQL_DATABASE=cazadores \\
  -e MYSQL_USER=cazadores \\
  -e MYSQL_PASSWORD=cazadores_local_password \\
  -e MYSQL_ROOT_PASSWORD=mysql_root_local_password \\
  -v cazadores_mysql_data:/var/lib/mysql \\
  mysql:8.4
```

La primera inicialización puede tardar unos segundos. Comprueba que el contenedor esté activo con `docker ps` y revisa sus mensajes con `docker logs cazadores-mysql`.

En `.env`, configura la conexión:

```dotenv
DB_ENGINE=django.db.backends.mysql
DB_NAME=cazadores
DB_USER=cazadores
DB_PASSWORD=cazadores_local_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

El contenedor crea la base de datos al inicializarse. Si ya existe un contenedor con el nombre `cazadores-mysql`, no lo crees de nuevo: puedes volver a iniciarlo con `docker start cazadores-mysql`.

### Usar SQLite en vez de MySQL

No hace falta instalar ni arrancar Docker. En `.env`, configura `DB_ENGINE=sqlite3` o deja la variable vacía. Django usará `db.local.sqlite3` en la raíz del proyecto y las migraciones crearán sus tablas.

### Inicializar Django y arrancar

Con el entorno virtual activado, ejecuta desde la raíz del proyecto:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`. El servidor de desarrollo recarga automáticamente los cambios de código; `runserver --noreload` solo desactiva esa función y no corrige problemas de dependencias o configuración.

Para cargar contenido inicial del juego, ejecuta `python manage.py seed_game_levels`. Para preparar las cuentas y roles demostrativos documentados más abajo, ejecuta `python manage.py demo_data load`. Estos datos se crean en la base configurada en `.env`.

### Datos y copias de seguridad

Las bases locales SQLite y `.env` están excluidos de Git. Clonar el repositorio e instalar dependencias no descarga los datos existentes: `migrate` crea el esquema, y los comandos de carga anteriores crean contenido inicial. Para trasladar una base poblada, exporta y restaura una copia de MySQL por separado, o transfiere de forma segura el archivo SQLite correspondiente. No subas copias de bases con datos privados, contraseñas ni secretos al repositorio.

## Datos ficticios para demostrar el panel

Después de aplicar las migraciones, cada integrante puede preparar los mismos
datos ficticios sin depender de una base de datos personal:

```bash
python manage.py demo_data load
```

El comando crea `demo_admin`, `demo_auditor` y `demo_jugador`, con los roles
`DEMO | Administradores`, `DEMO | Solo lectura` y `DEMO | Jugadores`. También
crea perfiles, niveles, progresos, logros y asignaciones identificados como
DEMO. El rol de administración usa permisos de Django pero no convierte la
cuenta en `staff` o superusuario. Las cuentas se crean sin contraseña utilizable;
para iniciar sesión, configura una contraseña local e interactiva, por ejemplo:

```bash
python manage.py changepassword demo_admin
```

No se guarda ninguna contraseña en el repositorio. Repite `demo_data load` con
seguridad: no duplica registros ni reemplaza datos. Si un nombre de cuenta DEMO
ya pertenece a una cuenta distinta, el comando cancela la carga sin modificarla.

Para limpiar los datos identificados por los nombres DEMO y los números de nivel
reservados `9001`-`9003`, ejecuta:

```bash
python manage.py demo_data clean
```

La limpieza conserva grupos con integrantes ajenos a DEMO y niveles/logros que
hayan adquirido relaciones con datos ajenos o cuyo contenido haya cambiado.
También conserva una cuenta DEMO y sus datos relacionados si se reutilizó y
acumuló actividad, permisos o grupos fuera del estado preparado por el comando.

## API de niveles para Flutter

La API usa Firebase Authentication. Configura Application Default Credentials
para Firebase Admin SDK (por ejemplo, con `GOOGLE_APPLICATION_CREDENTIALS`
apuntando a un archivo de cuenta de servicio fuera del repositorio).
Flutter debe enviar el ID token como `Authorization: Bearer <token>`.

- `GET /api/levels/`: devuelve niveles activos, disponibilidad
  y progreso del jugador autenticado.
- `POST /api/levels/<numero>/submit/`: valida la respuesta y,
  al completar un nivel por primera vez, agrega 10 XP y 1 pigmento.

Los niveles pueden administrarse desde el panel propio en
`/gestion/niveles/juego/` (también hay un enlace desde el dashboard de
administración). `data` contiene
solo información pública para Flutter y `solution` permanece en el servidor.
El perfil web de jugador (`/gestion/jugador/`) también lista los niveles activos
y permite jugar desde el navegador. El formulario del nivel debe guardarse con
`data.options` para preguntas de opción múltiple; para mezclas, temperatura y
saturación se usa `data.colors` (una lista de colores HEX). En estos tipos la
respuesta se compara con el formato esperado por su validador.
Por ejemplo, un nivel de opción múltiple puede guardar:

```json
{
  "data": {
    "options": [
      { "id": "a", "color": "#1E88E5" },
      { "id": "b", "color": "#E53935" }
    ]
  },
  "solution": {
    "option_id": "a"
  }
}
```

La app ya cuenta con modelos `Nivel` y `Progreso` para su gestión actual. Los
modelos `Level`, `Player` y `LevelProgress` se mantienen separados para esta
API autenticada con Firebase y no alteran esos flujos existentes.

## Cargar la ruta jugable

Después de aplicar las migraciones, carga las 25 pruebas iniciales:

```bash
python manage.py seed_game_levels
```

El comando es idempotente y no reemplaza niveles existentes. Si alguno de los
números reservados del 1 al 25 ya tiene contenido diferente, la carga normal se
cancela completa. Para conservar ese nivel y cargar los demás, ejecuta:

```bash
python manage.py seed_game_levels --skip-conflicts
```

Cada nivel nuevo incluye su propio enunciado, colores/opciones y solución
privada. Las respuestas se validan en el servidor y los intentos, completados,
XP y pigmentos se guardan por jugador.

Los jugadores pueden entrar desde el mapa o su perfil. Las rutas antiguas de
nivel redirigen al nuevo flujo basado en la base de datos. Para crear o editar
retos después de la carga, usa el panel **Niveles del juego**; no se necesita
una migración de esquema para cambiar preguntas o colores.

## Modelos Principales (ORM)

- **Jugador:** Almacena la información de los usuarios registrados.
- **Mapa:** (Describe aquí lo que hará tu modelo de mapas).
