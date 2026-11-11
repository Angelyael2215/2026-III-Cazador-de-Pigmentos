import os

from .base import *

DEBUG = True
ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1"
).split(",")

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite3").strip()

if DB_ENGINE in ("sqlite3", "django.db.backends.sqlite3"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.local.sqlite3",
        }
    }
elif DB_ENGINE in ("mysql", "django.db.backends.mysql"):
    required_db_settings = ("DB_NAME", "DB_USER", "DB_HOST", "DB_PORT")
    missing_db_settings = [
        setting for setting in required_db_settings if not os.getenv(setting)
    ]
    if missing_db_settings:
        raise RuntimeError(
            "Define estas variables en el archivo .env para usar MySQL: "
            + ", ".join(missing_db_settings)
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["DB_NAME"],
            "USER": os.environ["DB_USER"],
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.environ["DB_HOST"],
            "PORT": os.environ["DB_PORT"],
        }
    }
else:
    raise RuntimeError(
        "DB_ENGINE debe ser sqlite3 o django.db.backends.mysql"
    )

if not SECRET_KEY:
    raise RuntimeError("Define DJANGO_SECRET_KEY en el archivo .env")