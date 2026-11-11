def options(correct, *distractors):
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


GAME_LEVELS = (
    {
        "number": 1,
        "kind": "mix",
        "title": "La primera mezcla",
        "instruction": "Mezcla azul y rojo para descubrir el violeta. Selecciona los dos pigmentos.",
        "data": {"colors": ["#1E88E5", "#E53935", "#FDD835", "#FFFFFF"]},
        "solution": {"colors": ["#1E88E5", "#E53935"]},
    },
    {
        "number": 2,
        "kind": "rgb",
        "title": "El faro RGB",
        "instruction": "Ajusta los canales RGB hasta aproximarte al azul brillante de la señal.",
        "data": {"reference_color": "#1E88E5"},
        "solution": {"rgb": [30, 136, 229]},
    },
    {
        "number": 3,
        "kind": "harmony",
        "title": "La brújula complementaria",
        "instruction": "El azul del mapa necesita su color complementario para destacar.",
        "data": {
            "target_color": "#1976D2",
            **options("#F9A825", "#29B6F6", "#5E35B1"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 4,
        "kind": "hex",
        "title": "El código del cofre",
        "instruction": "Lee el código del pigmento y elige la muestra que coincide exactamente.",
        "data": {
            "target_hex": "#8B4513",
            **options("#8B4513", "#D2691E", "#A0522D", "#704214"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 5,
        "kind": "saturation",
        "title": "Escala de saturación",
        "instruction": "Ordena los pigmentos de menor a mayor saturación usando las flechas.",
        "data": {"colors": ["#E57373", "#B71C1C", "#F5C6C6", "#D32F2F"]},
        "solution": {"order": ["#F5C6C6", "#E57373", "#D32F2F", "#B71C1C"]},
    },
    {
        "number": 6,
        "kind": "temperature",
        "title": "La cámara térmica",
        "instruction": "Clasifica cada pigmento según la sensación de temperatura que transmite.",
        "data": {"colors": ["#F4511E", "#26C6DA", "#FFB300", "#3949AB"]},
        "solution": {
            "warm": ["#F4511E", "#FFB300"],
            "cold": ["#26C6DA", "#3949AB"],
        },
    },
    {
        "number": 7,
        "kind": "mix",
        "title": "Verde de explorador",
        "instruction": "Selecciona los pigmentos que se combinan para formar verde.",
        "data": {"colors": ["#FFEB3B", "#1565C0", "#F44336", "#9E9E9E"]},
        "solution": {"colors": ["#FFEB3B", "#1565C0"]},
    },
    {
        "number": 8,
        "kind": "contrast",
        "title": "Texto legible en la bitácora",
        "instruction": "Sobre el fondo claro de la bitácora, elige el color de texto con mayor contraste.",
        "data": {
            "target_background": "#FFF8E1",
            **options("#263238", "#B0BEC5", "#FBC02D", "#90A4AE"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 9,
        "kind": "gradient",
        "title": "El puente de tonos",
        "instruction": "Encuentra el tono que continúa la transición entre coral y naranja.",
        "data": {
            "colors": ["#EF5350", "#FF7043"],
            **options("#F4511E", "#3949AB", "#43A047"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 10,
        "kind": "branding",
        "title": "Emblema de la tripulación",
        "instruction": "Elige el color que mejor representa una expedición confiable y aventurera.",
        "data": {
            "brand_name": "Brújula del Mar",
            **options("#176B5B", "#D84343", "#E5A52B", "#795548"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 11,
        "kind": "mix",
        "title": "Naranja de atardecer",
        "instruction": "Selecciona los pigmentos necesarios para crear naranja.",
        "data": {"colors": ["#F44336", "#FDD835", "#3F51B5", "#FFFFFF"]},
        "solution": {"colors": ["#F44336", "#FDD835"]},
    },
    {
        "number": 12,
        "kind": "harmony",
        "title": "Tríada del arrecife",
        "instruction": "Escoge la tríada equilibrada que acompaña al turquesa.",
        "data": {
            "target_color": "#26A69A",
            "palette_options": [
                {"id": "a", "label": "Tríada oceánica", "colors": ["#26A69A", "#AB47BC", "#FFCA28"]},
                {"id": "b", "label": "Tonos vecinos", "colors": ["#26A69A", "#4DB6AC", "#80CBC4"]},
                {"id": "c", "label": "Escala neutra", "colors": ["#263238", "#78909C", "#ECEFF1"]},
            ],
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 13,
        "kind": "color_blindness",
        "title": "Señal para todas las miradas",
        "instruction": "Elige la combinación con mayor diferencia de luminosidad, además del cambio de color.",
        "data": {
            "target_color": "#D32F2F",
            **options("#263238", "#C62828", "#EF5350", "#8D6E63"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 14,
        "kind": "contrast",
        "title": "Contraste del mapa nocturno",
        "instruction": "El mapa usa un fondo azul oscuro. Selecciona el texto más legible.",
        "data": {
            "target_background": "#17324D",
            **options("#FFFFFF", "#45657D", "#24485F", "#8BA3B5"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 15,
        "kind": "rgb",
        "title": "Linterna de coral",
        "instruction": "Ajusta los canales para reproducir el tono coral de la linterna.",
        "data": {"reference_color": "#FF6F61"},
        "solution": {"rgb": [255, 111, 97]},
    },
    {
        "number": 16,
        "kind": "harmony",
        "title": "Colores vecinos del bosque",
        "instruction": "Encuentra la armonía análoga que acompaña al verde del bosque.",
        "data": {
            "target_color": "#388E3C",
            "palette_options": [
                {"id": "a", "label": "Bosque análogo", "colors": ["#8BC34A", "#4CAF50", "#388E3C"]},
                {"id": "b", "label": "Contraste opuesto", "colors": ["#388E3C", "#D32F2F", "#F44336"]},
                {"id": "c", "label": "Neutros", "colors": ["#263238", "#90A4AE", "#ECEFF1"]},
            ],
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 17,
        "kind": "contrast",
        "title": "El sello sobre pergamino",
        "instruction": "Sobre pergamino dorado, selecciona la tinta que conserva mejor la legibilidad.",
        "data": {
            "target_background": "#E8C987",
            **options("#33251B", "#FFF8E1", "#D9A441", "#BCAAA4"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 18,
        "kind": "gradient",
        "title": "Gradiente de hielo",
        "instruction": "Completa el viaje de azul cielo a azul profundo con el tono intermedio.",
        "data": {
            "colors": ["#81D4FA", "#0D47A1"],
            **options("#1976D2", "#EF6C00", "#7B1FA2"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 19,
        "kind": "mix",
        "title": "Violeta de medianoche",
        "instruction": "Elige los dos pigmentos que producen violeta.",
        "data": {"colors": ["#3949AB", "#D81B60", "#43A047", "#FDD835"]},
        "solution": {"colors": ["#3949AB", "#D81B60"]},
    },
    {
        "number": 20,
        "kind": "temperature",
        "title": "Brisa y lava",
        "instruction": "Separa los tonos que se sienten cálidos de los que se sienten fríos.",
        "data": {"colors": ["#FF5722", "#03A9F4", "#F9A825", "#5C6BC0"]},
        "solution": {
            "warm": ["#FF5722", "#F9A825"],
            "cold": ["#03A9F4", "#5C6BC0"],
        },
    },
    {
        "number": 21,
        "kind": "albers",
        "title": "La ilusión del tesoro",
        "instruction": "Elige el centro que parece más brillante por el contraste con su entorno.",
        "data": {
            "target_color": "#E6B84A",
            **options("#E6B84A", "#72521E", "#F3D889", "#B7872F"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 22,
        "kind": "hex",
        "title": "La clave esmeralda",
        "instruction": "Busca en las muestras el pigmento que corresponde al código indicado.",
        "data": {
            "target_hex": "#2E7D32",
            **options("#2E7D32", "#388E3C", "#1B5E20", "#66BB6A"),
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 23,
        "kind": "rgb",
        "title": "Destello de zafiro",
        "instruction": "Ajusta los cañones rojo, verde y azul para igualar el zafiro.",
        "data": {"reference_color": "#3949AB"},
        "solution": {"rgb": [57, 73, 171]},
    },
    {
        "number": 24,
        "kind": "atmosphere",
        "title": "Atmósfera de aurora",
        "instruction": "Selecciona la paleta que evoca una aurora sobre el océano.",
        "data": {
            "palette_options": [
                {"id": "a", "label": "Aurora oceánica", "colors": ["#00BFA5", "#80DEEA", "#5E35B1", "#172A46"]},
                {"id": "b", "label": "Desierto", "colors": ["#8D4A2F", "#C18443", "#E6C28B", "#F7E7C1"]},
                {"id": "c", "label": "Cosecha", "colors": ["#B71C1C", "#E65100", "#F9A825", "#795548"]},
            ],
        },
        "solution": {"option_id": "a"},
    },
    {
        "number": 25,
        "kind": "saturation",
        "title": "El tesoro cromático",
        "instruction": "Ordena la última serie desde el pigmento más apagado hasta el más intenso.",
        "data": {"colors": ["#C62828", "#F3C4C4", "#E57373", "#8E0000"]},
        "solution": {"order": ["#F3C4C4", "#E57373", "#C62828", "#8E0000"]},
    },
)
