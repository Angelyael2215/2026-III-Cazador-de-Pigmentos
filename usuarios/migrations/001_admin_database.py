from django.conf import settings
from django.db import migrations


def create_development_admin(apps, schema_editor):
    if not settings.DEBUG:
        return

    user_model_label = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(*user_model_label)

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admincool",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_alter_perfilusuario_options_evaluacionaccesibilidad"),
    ]

    operations = [
        migrations.RunPython(
            create_development_admin,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
