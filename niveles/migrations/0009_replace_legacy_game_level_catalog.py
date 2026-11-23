from django.db import migrations

from niveles.level_seed_data import GAME_LEVELS


def replace_level_catalog(apps, schema_editor):
    Level = apps.get_model("niveles", "Level")
    database = schema_editor.connection.alias

    for definition in GAME_LEVELS:
        defaults = {
            field: value
            for field, value in definition.items()
            if field != "number"
        }
        level = Level.objects.using(database).filter(number=definition["number"]).first()
        if level is None:
            Level.objects.using(database).create(
                number=definition["number"],
                **defaults,
            )
            continue

        changed_fields = []
        for field, value in defaults.items():
            if getattr(level, field) != value:
                setattr(level, field, value)
                changed_fields.append(field)
        if changed_fields:
            level.save(update_fields=changed_fields)


class Migration(migrations.Migration):
    dependencies = [
        ("niveles", "0008_slider_rgb_level_copy"),
    ]

    operations = [
        migrations.RunPython(replace_level_catalog, migrations.RunPython.noop),
    ]
