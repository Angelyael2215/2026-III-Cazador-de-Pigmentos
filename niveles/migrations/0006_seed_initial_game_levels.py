from django.db import migrations

from niveles.level_seed_data import GAME_LEVELS


def load_initial_levels(apps, schema_editor):
    Level = apps.get_model("niveles", "Level")
    database = schema_editor.connection.alias

    for definition in GAME_LEVELS:
        defaults = {
            field: value
            for field, value in definition.items()
            if field != "number"
        }
        Level.objects.using(database).get_or_create(
            number=definition["number"],
            defaults=defaults,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("niveles", "0005_moduloteorico_sesionnivel"),
    ]

    operations = [
        migrations.RunPython(load_initial_levels, migrations.RunPython.noop),
    ]
