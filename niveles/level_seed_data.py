def color_options(correct, *distractors):
    colors = (correct, *distractors)
    return {
        "options": [
            {
                "id": chr(ord("a") + index),
                "label": f"Muestra {chr(ord('A') + index)}",
                "color": color,
            }
            for index, color in enumerate(colors)
        ]
    }


def palette_option(option_id, label, colors):
    return {"id": option_id, "label": label, "colors": colors}


MIXES = (
    (
        "Mezcla azul y rojo",
        "Toca dos colores del cuenco y observa qué tono forman.",
        ["#1E88E5", "#E53935", "#FDD835", "#FFFFFF"],
        ["#1E88E5", "#E53935"],
        "Morado",
        "#7B1FA2",
    ),
    (
        "La mezcla de la linterna",
        "Prueba cualquier combinación de dos colores.",
        ["#1565C0", "#FDD835", "#43A047", "#F44336"],
        ["#1565C0", "#FDD835"],
        "Verde",
        "#43A047",
    ),
    (
        "Haz naranja",
        "Prueba dos pigmentos y descubre la mezcla naranja.",
        ["#F44336", "#FDD835", "#3F51B5", "#FFFFFF"],
        ["#F44336", "#FDD835"],
        "Naranja",
        "#F4511E",
    ),
    (
        "Haz violeta",
        "Combina dos opciones hasta formar un tono violeta.",
        ["#3949AB", "#D81B60", "#43A047", "#FDD835"],
        ["#3949AB", "#D81B60"],
        "Violeta",
        "#8E24AA",
    ),
)


def mix_level(number, cycle):
    title, instruction, colors, solution, name, result_hex = MIXES[cycle % len(MIXES)]
    return {
        "number": number,
        "kind": "mix",
        "title": title,
        "instruction": instruction,
        "data": {"colors": colors},
        "solution": {
            "colors": solution,
            "result": {"name": name, "hex": result_hex},
        },
    }


GAME_LEVELS = (
    mix_level(1, 0),
    {
        "number": 2,
        "kind": "branding",
        "title": "El emblema del explorador",
        "instruction": "Lee la situación y elige el color que mejor representa la marca.",
        "data": {
            "situation": "Una marca ecológica quiere transmitir confianza, naturaleza y aventura.",
            "brand_name": "Bosque Vivo",
            **color_options("#2E7D32", "#D32F2F", "#F9A825", "#5E35B1"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 3,
        "kind": "gradient",
        "title": "Completa la escala cromática",
        "instruction": "Coloca el color correcto en el espacio central.",
        "data": {
            "colors": ["#EF5350", "#FF7043"],
            "fixed_slots": ["#EF5350", None, "#FF7043"],
            **color_options("#F4511E", "#3949AB", "#43A047"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 4,
        "kind": "contrast",
        "title": "Contraste para leer",
        "instruction": "Elige el color que hace más visible la palabra sobre el recuadro.",
        "data": {
            "contrast_word": "PIGMENTO",
            "target_background": "#FFF8E1",
            **color_options("#263238", "#B0BEC5", "#FBC02D", "#90A4AE"),
        },
        "solution": {"option_id": "a"},
    },
    mix_level(5, 1),
    {
        "number": 6,
        "kind": "color_blindness",
        "title": "Daltonismo: protanopia",
        "instruction": "Elige la opción de color que más se parezca al modelo.",
        "data": {
            "deficiency_type": "Protanopia",
            "target_color": "#D32F2F",
            **color_options("#263238", "#C62828", "#EF5350", "#8D6E63"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 7,
        "kind": "rgb",
        "title": "Laberinto RGB",
        "instruction": "Mueve rojo, verde y azul hasta lograr al menos 90% del color fijo.",
        "data": {"reference_color": "#1E88E5"},
        "solution": {"rgb": [30, 136, 229]},
    },
    {
        "number": 8,
        "kind": "temperature",
        "title": "Temperatura del color",
        "instruction": "Coloca cada color en el rectángulo frío o caliente.",
        "data": {"colors": ["#F4511E", "#26C6DA", "#FFB300", "#3949AB"]},
        "solution": {
            "warm": ["#F4511E", "#FFB300"],
            "cold": ["#26C6DA", "#3949AB"],
        },
    },
    {
        "number": 9,
        "kind": "hex",
        "title": "Adivina el HEX",
        "instruction": "Compara el código hexadecimal y elige el color que creas que corresponde.",
        "data": {
            "target_hex": "#8B4513",
            **color_options("#8B4513", "#D2691E", "#A0522D", "#704214"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 10,
        "kind": "branding",
        "title": "La marca de una aventura",
        "instruction": "Lee la situación y elige el color que encaje mejor.",
        "data": {
            "situation": "Una agencia de viajes busca emoción, calor humano y energía para anunciar expediciones.",
            "brand_name": "Ruta Dorada",
            **color_options("#F9A825", "#176B5B", "#3949AB", "#795548"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 11,
        "kind": "atmosphere",
        "title": "La paleta de la situación",
        "instruction": "Lee la situación y elige la paleta que mejor construya esa atmósfera.",
        "data": {
            "situation": "Un faro ilumina una costa tranquila durante una noche de tormenta.",
            "palette_options": [
                palette_option("a", "Costa nocturna", ["#17324D", "#1E88E5", "#80DEEA", "#ECEFF1"]),
                palette_option("b", "Desierto cálido", ["#8D4A2F", "#C18443", "#E6C28B", "#FFF3D6"]),
                palette_option("c", "Primavera", ["#66BB6A", "#AED581", "#F48FB1", "#FFF59D"]),
                palette_option("d", "Cosecha", ["#B71C1C", "#E65100", "#F9A825", "#795548"]),
            ],
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 12,
        "kind": "saturation",
        "title": "De suave a fuerte",
        "instruction": "Acomoda los cuatro tonos de rosa de menor a mayor saturación.",
        "data": {"colors": ["#F8D7DA", "#EFAAB0", "#D95C73", "#9C1F3D"]},
        "solution": {"order": ["#F8D7DA", "#EFAAB0", "#D95C73", "#9C1F3D"]},
    },
    mix_level(13, 2),
    {
        "number": 14,
        "kind": "branding",
        "title": "El emblema del océano",
        "instruction": "Lee la situación y elige el color apropiado para la marca.",
        "data": {
            "situation": "Una escuela de buceo necesita un color que transmita frescura, limpieza y profundidad.",
            "brand_name": "Azul Profundo",
            **color_options("#1565C0", "#F4511E", "#43A047", "#FDD835"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 15,
        "kind": "gradient",
        "title": "Escala del atardecer",
        "instruction": "Completa el segundo espacio con la opción que continúe la escala.",
        "data": {
            "fixed_slots": ["#F8BBD0", None, "#D81B60"],
            "colors": ["#F8BBD0", "#D81B60"],
            **color_options("#EC407A", "#3949AB", "#66BB6A"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 16,
        "kind": "contrast",
        "title": "Palabra sobre fondo oscuro",
        "instruction": "Elige el color de texto que tenga mejor contraste.",
        "data": {
            "contrast_word": "NOCHE",
            "target_background": "#17324D",
            **color_options("#FFFFFF", "#45657D", "#24485F", "#8BA3B5"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 17,
        "kind": "color_blindness",
        "title": "Daltonismo: deuteranopia",
        "instruction": "Elige el tono que más se parezca al color fijo.",
        "data": {
            "deficiency_type": "Deuteranopia",
            "target_color": "#2E7D32",
            **color_options("#1B5E20", "#66BB6A", "#388E3C", "#8D6E63"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 18,
        "kind": "rgb",
        "title": "Laberinto RGB coral",
        "instruction": "Combina los canales hasta alcanzar al menos 90% del color coral fijo.",
        "data": {"reference_color": "#FF6F61"},
        "solution": {"rgb": [255, 111, 97]},
    },
    {
        "number": 19,
        "kind": "temperature",
        "title": "Fuego y hielo",
        "instruction": "Separa los colores calientes de los fríos.",
        "data": {"colors": ["#FF5722", "#03A9F4", "#F9A825", "#5C6BC0"]},
        "solution": {
            "warm": ["#FF5722", "#F9A825"],
            "cold": ["#03A9F4", "#5C6BC0"],
        },
    },
    {
        "number": 20,
        "kind": "hex",
        "title": "Adivina el verde HEX",
        "instruction": "Usa el código mostrado y elige la opción más cercana.",
        "data": {
            "target_hex": "#2E7D32",
            **color_options("#2E7D32", "#388E3C", "#1B5E20", "#66BB6A"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 21,
        "kind": "atmosphere",
        "title": "Una aurora nocturna",
        "instruction": "Lee la escena y selecciona la paleta que produzca esa atmósfera.",
        "data": {
            "situation": "Una aurora verde cruza un cielo profundo sobre montañas nevadas.",
            "palette_options": [
                palette_option("a", "Aurora polar", ["#172A46", "#00BFA5", "#80DEEA", "#DCE775"]),
                palette_option("b", "Desierto", ["#8D4A2F", "#C18443", "#E6C28B", "#F7E7C1"]),
                palette_option("c", "Cosecha", ["#B71C1C", "#E65100", "#F9A825", "#795548"]),
                palette_option("d", "Jardín", ["#66BB6A", "#F48FB1", "#FFD54F", "#FFFFFF"]),
            ],
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 22,
        "kind": "saturation",
        "title": "Azules de menor a mayor",
        "instruction": "Acomoda los cuatro azules del más claro al más fuerte.",
        "data": {"colors": ["#BBDEFB", "#64B5F6", "#1976D2", "#0D47A1"]},
        "solution": {"order": ["#BBDEFB", "#64B5F6", "#1976D2", "#0D47A1"]},
    },
    mix_level(23, 3),
    {
        "number": 24,
        "kind": "branding",
        "title": "Marca de energía solar",
        "instruction": "Una marca deportiva quiere proyectar energía y movimiento. Elige el color principal.",
        "data": {
            "brand_name": "Sol Activo",
            **color_options("#F9A825", "#26C6DA", "#8E24AA", "#263238"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 25,
        "kind": "gradient",
        "title": "Escala fría final",
        "instruction": "Completa el lugar central de la escala cromática.",
        "data": {
            "fixed_slots": ["#81D4FA", None, "#0D47A1"],
            "colors": ["#81D4FA", "#0D47A1"],
            **color_options("#1976D2", "#EF6C00", "#7B1FA2"),
        },
        "solution": {"option_id": "a"},
    },
)


ANSWER_POSITIONS = {
    2: 1,
    3: 2,
    4: 3,
    6: 1,
    9: 3,
    10: 2,
    11: 2,
    14: 1,
    15: 2,
    16: 3,
    17: 2,
    20: 1,
    21: 3,
    24: 1,
    25: 2,
}


def vary_correct_answers(levels):
    for level in levels:
        position = ANSWER_POSITIONS.get(level["number"])
        if position is None:
            continue

        data = level.get("data", {})
        source_key = "palette_options" if isinstance(data.get("palette_options"), list) else "options"
        options = data.get(source_key)
        if not isinstance(options, list) or not options:
            continue

        correct = options.pop(0)
        position = min(position, len(options))
        options.insert(position, correct)
        for index, option in enumerate(options):
            option["id"] = chr(ord("a") + index)
        level["solution"]["option_id"] = chr(ord("a") + position)


vary_correct_answers(GAME_LEVELS)
