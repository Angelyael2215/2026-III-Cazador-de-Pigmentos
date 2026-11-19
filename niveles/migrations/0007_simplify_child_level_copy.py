from django.db import migrations


PLAYER_COPY = {
    1: (
        ("La primera mezcla", "Mezcla azul y rojo para descubrir el violeta. Selecciona los dos pigmentos."),
        ("Mezcla azul y rojo", "Toca azul y rojo para descubrir qué color forman."),
    ),
    2: (
        ("El faro RGB", "Ajusta los canales RGB hasta aproximarte al azul brillante de la señal."),
        ("Busca el azul", "Toca la muestra que tiene el mismo azul del faro."),
    ),
    3: (
        ("La brújula complementaria", "El azul del mapa necesita su color complementario para destacar."),
        ("Un color que resalta", "Toca el color que más resalta junto al azul."),
    ),
    4: (
        ("El código del cofre", "Lee el código del pigmento y elige la muestra que coincide exactamente."),
        ("Busca el mismo color", "Mira el color del cofre y toca la muestra igual."),
    ),
    5: (
        ("Escala de saturación", "Ordena los pigmentos de menor a mayor saturación usando las flechas."),
        ("Colores suaves y fuertes", "Ordena tres colores del más suave al más fuerte."),
    ),
    6: (
        ("La cámara térmica", "Clasifica cada pigmento según la sensación de temperatura que transmite."),
        ("Fuego o hielo", "Para cada color, elige si parece de fuego o de hielo."),
    ),
    7: (
        ("Verde de explorador", "Selecciona los pigmentos que se combinan para formar verde."),
        ("Haz verde", "Toca amarillo y azul para formar verde."),
    ),
    8: (
        ("Texto legible en la bitácora", "Sobre el fondo claro de la bitácora, elige el color de texto con mayor contraste."),
        ("Elige la tinta", "Toca la tinta que mejor se ve sobre el papel claro."),
    ),
    9: (
        ("El puente de tonos", "Encuentra el tono que continúa la transición entre coral y naranja."),
        ("Completa el camino de colores", "Toca el color que va entre coral y naranja."),
    ),
    10: (
        ("Emblema de la tripulación", "Elige el color que mejor representa una expedición confiable y aventurera."),
        ("El color del emblema", "Toca el color verde del emblema."),
    ),
    11: (
        ("Naranja de atardecer", "Selecciona los pigmentos necesarios para crear naranja."),
        ("Haz naranja", "Toca rojo y amarillo para formar naranja."),
    ),
    12: (
        ("Tríada del arrecife", "Escoge la tríada equilibrada que acompaña al turquesa."),
        ("Colores del arrecife", "Toca la paleta que combina con el color turquesa."),
    ),
    13: (
        ("Señal para todas las miradas", "Elige la combinación con mayor diferencia de luminosidad, además del cambio de color."),
        ("Colores fáciles de ver", "Toca la combinación en la que los colores se distinguen mejor."),
    ),
    14: (
        ("Contraste del mapa nocturno", "El mapa usa un fondo azul oscuro. Selecciona el texto más legible."),
        ("Texto en el mapa nocturno", "Elige el color de texto que se ve mejor sobre el fondo oscuro."),
    ),
    15: (
        ("Linterna de coral", "Ajusta los canales para reproducir el tono coral de la linterna."),
        ("Busca el coral", "Toca la muestra que tiene el mismo color que la linterna."),
    ),
    16: (
        ("Colores vecinos del bosque", "Encuentra la armonía análoga que acompaña al verde del bosque."),
        ("Colores del bosque", "Toca los colores que mejor acompañan al verde del bosque."),
    ),
    17: (
        ("El sello sobre pergamino", "Sobre pergamino dorado, selecciona la tinta que conserva mejor la legibilidad."),
        ("Tinta sobre el pergamino", "Toca la tinta que se lee mejor sobre el papel dorado."),
    ),
    18: (
        ("Gradiente de hielo", "Completa el viaje de azul cielo a azul profundo con el tono intermedio."),
        ("Completa los colores del hielo", "Toca el azul que está entre el claro y el oscuro."),
    ),
    19: (
        ("Violeta de medianoche", "Elige los dos pigmentos que producen violeta."),
        ("Haz violeta", "Toca azul y rosa para formar violeta."),
    ),
    20: (
        ("Brisa y lava", "Separa los tonos que se sienten cálidos de los que se sienten fríos."),
        ("Fuego o hielo", "Separa los colores que parecen de fuego y los que parecen de hielo."),
    ),
    21: (
        ("La ilusión del tesoro", "Elige el centro que parece más brillante por el contraste con su entorno."),
        ("El centro más claro", "Toca el centro que se ve más brillante."),
    ),
    22: (
        ("La clave esmeralda", "Busca en las muestras el pigmento que corresponde al código indicado."),
        ("Busca el verde", "Mira el verde del cofre y toca la muestra igual."),
    ),
    23: (
        ("Destello de zafiro", "Ajusta los cañones rojo, verde y azul para igualar el zafiro."),
        ("Busca el azul", "Toca la muestra que tiene el mismo azul de la piedra."),
    ),
    24: (
        ("Atmósfera de aurora", "Selecciona la paleta que evoca una aurora sobre el océano."),
        ("Colores de la aurora", "Toca la paleta que usarías para pintar una aurora."),
    ),
    25: (
        ("El tesoro cromático", "Ordena la última serie desde el pigmento más apagado hasta el más intenso."),
        ("El color más fuerte", "Ordena tres colores del más suave al más fuerte."),
    ),
}

SATURATION_DATA = {
    5: (
        (
            {"colors": ["#E57373", "#B71C1C", "#F5C6C6", "#D32F2F"]},
            {"order": ["#F5C6C6", "#E57373", "#D32F2F", "#B71C1C"]},
        ),
        (
            {"colors": ["#E57373", "#B71C1C", "#F5C6C6"]},
            {"order": ["#F5C6C6", "#E57373", "#B71C1C"]},
        ),
    ),
    25: (
        (
            {"colors": ["#C62828", "#F3C4C4", "#E57373", "#8E0000"]},
            {"order": ["#F3C4C4", "#E57373", "#C62828", "#8E0000"]},
        ),
        (
            {"colors": ["#F3C4C4", "#E57373", "#8E0000"]},
            {"order": ["#F3C4C4", "#E57373", "#8E0000"]},
        ),
    ),
}


def update_levels(apps, schema_editor, reverse=False):
    Level = apps.get_model("niveles", "Level")
    levels = Level.objects.using(schema_editor.connection.alias)

    for number, (old_copy, new_copy) in PLAYER_COPY.items():
        source, target = (new_copy, old_copy) if reverse else (old_copy, new_copy)
        level = levels.filter(number=number).first()
        if (
            level
            and level.title == source[0]
            and level.instruction == source[1]
        ):
            level.title, level.instruction = target
            level.save(update_fields=["title", "instruction"])

    for number, (old_config, new_config) in SATURATION_DATA.items():
        source, target = (new_config, old_config) if reverse else (old_config, new_config)
        level = levels.filter(number=number, kind="saturation").first()
        if level and level.data == source[0] and level.solution == source[1]:
            level.data, level.solution = target
            level.save(update_fields=["data", "solution"])


def simplify_levels(apps, schema_editor):
    update_levels(apps, schema_editor)


def restore_levels(apps, schema_editor):
    update_levels(apps, schema_editor, reverse=True)


class Migration(migrations.Migration):
    dependencies = [
        ("niveles", "0006_seed_initial_game_levels"),
    ]

    operations = [
        migrations.RunPython(simplify_levels, restore_levels),
    ]
