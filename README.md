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

## Modelos Principales (ORM)
* **Jugador:** Almacena la información de los usuarios registrados.
* **Mapa:** (Describe aquí lo que hará tu modelo de mapas).