from django.db import migrations


COPY_UPDATES = {
    2: (
        "Toca la muestra que tiene el mismo azul del faro.",
        "Mueve las barras para igualar el azul del faro.",
    ),
    15: (
        "Toca la muestra que tiene el mismo color que la linterna.",
        "Mueve las barras para igualar el color de la linterna.",
    ),
    23: (
        "Toca la muestra que tiene el mismo azul de la piedra.",
        "Mueve las barras para igualar el azul de la piedra.",
    ),
}


def update_instructions(apps, schema_editor):
    Level = apps.get_model("niveles", "Level")
    levels = Level.objects.using(schema_editor.connection.alias)
    for number, (old_instruction, new_instruction) in COPY_UPDATES.items():
        level = levels.filter(number=number, kind="rgb").first()
        if level and level.instruction == old_instruction:
            level.instruction = new_instruction
            level.save(update_fields=["instruction"])


def restore_instructions(apps, schema_editor):
    Level = apps.get_model("niveles", "Level")
    levels = Level.objects.using(schema_editor.connection.alias)
    for number, (old_instruction, new_instruction) in COPY_UPDATES.items():
        level = levels.filter(number=number, kind="rgb").first()
        if level and level.instruction == new_instruction:
            level.instruction = old_instruction
            level.save(update_fields=["instruction"])


class Migration(migrations.Migration):
    dependencies = [
        ("niveles", "0007_simplify_child_level_copy"),
    ]

    operations = [
        migrations.RunPython(update_instructions, restore_instructions),
    ]
