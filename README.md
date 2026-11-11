# Cazador de Pigmentos - Backend 

juego interactivo de combinacion de colores

## Tecnologías usadas
* Django
* Python

## Instalación Local
1. Clona el repositorio y crea un entorno virtual: `python -m venv venv`
2. En Debian/Ubuntu, instala las dependencias de compilación de MySQL: `sudo apt install build-essential pkg-config default-libmysqlclient-dev`
3. Activa el entorno virtual e instala los requerimientos: `pip install -r requirements.txt`
4. Copia `.env.example` a `.env` y configura la clave, el nombre de la base de datos y las credenciales de MySQL.
5. Crea en MySQL la base de datos indicada en `DB_NAME`.
6. Aplica las migraciones: `python manage.py migrate`
7. Levanta el servidor: `python manage.py runserver`

En desarrollo, `runserver` activa la recarga automática al detectar cambios. `runserver --noreload` solo desactiva esa recarga; normalmente no es necesario y no corrige errores de configuración o dependencias. Para seguir ejecutando SQLite, establece `DB_ENGINE=sqlite3` (o elimina esa variable); el valor predeterminado también es SQLite.

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
      {"id": "a", "color": "#1E88E5"},
      {"id": "b", "color": "#E53935"}
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
* **Jugador:** Almacena la información de los usuarios registrados.
* **Mapa:** (Describe aquí lo que hará tu modelo de mapas).