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

## Modelos Principales (ORM)
* **Jugador:** Almacena la información de los usuarios registrados.
* **Mapa:** (Describe aquí lo que hará tu modelo de mapas).