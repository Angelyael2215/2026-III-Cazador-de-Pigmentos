from django import forms

from .level_data import correct_option_id, level_options
from .models import Level
from .services import normalize_color_list


class LevelForm(forms.ModelForm):
    colors = forms.CharField(
        label="Colores disponibles",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "#1E88E5\n#E53935"}),
        help_text="Escribe un color HEX por línea. También puedes separarlos con comas.",
    )
    answer_colors = forms.CharField(
        label="Respuesta de colores",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "#1E88E5"}),
        help_text="Para mezclas, indica los pigmentos correctos; para saturación, el orden correcto.",
    )
    warm_colors = forms.CharField(
        label="Colores cálidos",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "#F4511E"}),
    )
    cold_colors = forms.CharField(
        label="Colores fríos",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "#26C6DA"}),
    )
    reference_color = forms.CharField(
        label="Color de referencia",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "#1E88E5", "autocomplete": "off"}),
        help_text="Usa el formato HEX #RRGGBB.",
    )
    brand_name = forms.CharField(
        label="Nombre de marca",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Brújula del Mar"}),
    )
    options_text = forms.CharField(
        label="Opciones de respuesta",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "Opción azul | #1E88E5\nOpción roja | #E53935",
            }
        ),
        help_text=(
            "Una opción por línea, con formato Nombre | #COLOR. "
            "Para paletas, separa sus colores con comas."
        ),
    )
    correct_option = forms.ChoiceField(
        label="Respuesta correcta",
        required=False,
        choices=(),
    )

    class Meta:
        model = Level
        fields = (
            "number",
            "kind",
            "title",
            "instruction",
            "active",
            "colors",
            "answer_colors",
            "warm_colors",
            "cold_colors",
            "reference_color",
            "brand_name",
            "options_text",
            "correct_option",
            "data",
            "solution",
        )
        labels = {
            "number": "Número de nivel",
            "kind": "Tipo de reto",
            "title": "Título",
            "instruction": "Instrucciones para el jugador",
            "active": "Nivel activo",
            "data": "Datos visibles (JSON avanzado)",
            "solution": "Respuesta correcta (JSON avanzado)",
        }
        widgets = {
            "instruction": forms.Textarea(attrs={"rows": 3}),
            "data": forms.Textarea(attrs={"rows": 6, "spellcheck": "false"}),
            "solution": forms.Textarea(attrs={"rows": 4, "spellcheck": "false"}),
        }
        help_texts = {
            "active": "Solo los niveles activos aparecen en el perfil del jugador.",
            "data": "Solo para configuraciones avanzadas. El formulario guiado suele ser suficiente.",
            "solution": "Solo para configuraciones avanzadas. No se muestra a los jugadores.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["data"].required = False
        self.fields["solution"].required = False
        if not self.instance.pk:
            self.initial.setdefault("data", "")
            self.initial.setdefault("solution", "")
        self.fields["correct_option"].choices = self._option_choices(
            self._option_text_value()
        )
        self._set_guided_initials()

    def _option_text_value(self):
        if self.is_bound:
            return self.data.get("options_text", "")
        return self.initial.get("options_text", "")

    @staticmethod
    def _option_choices(value):
        lines = [line.strip() for line in value.splitlines() if line.strip()]
        return [
            ("", "Selecciona la respuesta correcta"),
            *(
                (chr(ord("a") + index), line.split("|", 1)[0].strip())
                for index, line in enumerate(lines)
            ),
        ]

    def _set_guided_initials(self):
        if not self.instance.pk:
            return

        data = self.instance.data if isinstance(self.instance.data, dict) else {}
        solution = self.instance.solution if isinstance(self.instance.solution, dict) else {}
        colors = data.get("colors", [])
        if self.instance.kind == "mix" and not colors:
            colors = [
                option.get("color")
                for option in data.get("options", [])
                if isinstance(option, dict) and option.get("color")
            ]
        if isinstance(colors, list):
            self.initial["colors"] = "\n".join(colors)

        if self.instance.kind == "mix":
            answers = solution.get("colors", [])
            if not answers and isinstance(solution.get("correct_combination"), list):
                by_id = {
                    option.get("id"): option.get("color")
                    for option in data.get("options", [])
                    if isinstance(option, dict)
                }
                answers = [
                    by_id[option_id]
                    for option_id in solution["correct_combination"]
                    if option_id in by_id
                ]
        elif self.instance.kind == "saturation":
            answers = solution.get("order", [])
        else:
            answers = []
        if isinstance(answers, list):
            self.initial["answer_colors"] = "\n".join(answers)

        for field_name, key in (("warm_colors", "warm"), ("cold_colors", "cold")):
            values = solution.get(key, [])
            if isinstance(values, list):
                self.initial[field_name] = "\n".join(values)

        reference = next(
            (
                data[key]
                for key in (
                    "reference_color",
                    "target_hex",
                    "target_color",
                    "target_background",
                )
                if isinstance(data.get(key), str)
            ),
            "",
        )
        self.initial["reference_color"] = reference
        self.initial["brand_name"] = data.get("brand_name", "")

        options = data.get("palette_options") or data.get("options") or []
        option_lines = []
        correct_id = correct_option_id(solution)
        correct_index = None
        for index, option in enumerate(options):
            if not isinstance(option, dict):
                continue
            if option.get("id") == correct_id:
                correct_index = index
            colors = option.get("colors", [])
            if option.get("color"):
                colors = [option["color"], *colors]
            if not isinstance(colors, list):
                continue
            label = option.get("label") or option.get("name") or f"Opción {index + 1}"
            option_lines.append(f"{label} | {', '.join(colors)}")
        self.initial["options_text"] = "\n".join(option_lines)
        if correct_index is not None:
            self.initial["correct_option"] = chr(ord("a") + correct_index)
        self.fields["correct_option"].choices = self._option_choices(
            self.initial["options_text"]
        )

    def clean_data(self):
        data = self.cleaned_data.get("data")
        if data in (None, ""):
            return {}
        if not isinstance(data, dict):
            raise forms.ValidationError("Los datos del nivel deben ser un objeto JSON.")
        return data

    def clean_solution(self):
        solution = self.cleaned_data.get("solution")
        if solution in (None, ""):
            return {}
        if not isinstance(solution, dict):
            raise forms.ValidationError("La solución debe ser un objeto JSON.")
        return solution

    def _has_guided_input(self):
        fields = (
            "colors",
            "answer_colors",
            "warm_colors",
            "cold_colors",
            "reference_color",
            "brand_name",
            "options_text",
            "correct_option",
        )
        return any(str(self.data.get(name, "")).strip() for name in fields)

    def _colors_from(self, field_name, *, required=False):
        value = self.cleaned_data.get(field_name, "")
        colors = [
            color.strip()
            for line in value.splitlines()
            for color in line.split(",")
            if color.strip()
        ]
        if not colors:
            if required:
                self.add_error(field_name, "Agrega al menos un color.")
            return []
        try:
            colors = normalize_color_list(colors)
        except ValueError as error:
            self.add_error(field_name, str(error))
            return []
        if len(set(colors)) != len(colors):
            self.add_error(field_name, "No repitas colores.")
        return colors

    def _build_guided_configuration(self, kind):
        data = {}
        solution = {}

        if kind in {"mix", "temperature", "saturation", "gradient"}:
            colors = self._colors_from("colors", required=True)
            if kind == "gradient" and len(colors) != 2:
                self.add_error("colors", "Un degradado necesita exactamente dos colores.")
            data["colors"] = colors

        if kind == "mix":
            solution["colors"] = self._colors_from("answer_colors", required=True)
            return data, solution

        if kind == "rgb":
            color = self._colors_from("reference_color", required=True)
            if color:
                data["reference_color"] = color[0]
                solution["rgb"] = [
                    int(color[0][index:index + 2], 16)
                    for index in (1, 3, 5)
                ]
            return data, solution

        if kind == "temperature":
            solution["warm"] = self._colors_from("warm_colors", required=True)
            solution["cold"] = self._colors_from("cold_colors", required=True)
            return data, solution

        if kind == "saturation":
            solution["order"] = self._colors_from("answer_colors", required=True)
            return data, solution

        target_keys = {
            "hex": "target_hex",
            "harmony": "target_color",
            "contrast": "target_background",
            "color_blindness": "target_color",
            "albers": "target_color",
        }
        target_key = target_keys.get(kind)
        if target_key:
            color = self._colors_from("reference_color", required=True)
            if color:
                data[target_key] = color[0]
        if kind == "branding":
            brand_name = self.cleaned_data.get("brand_name", "").strip()
            if not brand_name:
                self.add_error("brand_name", "Escribe el nombre de la marca.")
            else:
                data["brand_name"] = brand_name

        option_lines = [
            line.strip()
            for line in self.cleaned_data.get("options_text", "").splitlines()
            if line.strip()
        ]
        options = []
        for index, line in enumerate(option_lines):
            if "|" not in line:
                self.add_error(
                    "options_text",
                    "Cada opción debe tener el formato Nombre | #RRGGBB.",
                )
                continue
            label, color_text = (part.strip() for part in line.split("|", 1))
            colors = self._colors_from_value(color_text)
            if not label or not colors:
                self.add_error(
                    "options_text",
                    "Cada opción necesita un nombre y al menos un color HEX.",
                )
                continue
            option = {
                "id": chr(ord("a") + index),
                "label": label,
            }
            if kind in {"harmony", "atmosphere"}:
                option["colors"] = colors
            else:
                option["color"] = colors[0]
                if len(colors) > 1:
                    option["colors"] = colors[1:]
            options.append(option)

        if len(options) < 2:
            self.add_error("options_text", "Agrega al menos dos opciones.")
        option_id = self.cleaned_data.get("correct_option")
        option_ids = {option["id"] for option in options}
        if option_id not in option_ids:
            self.add_error("correct_option", "Selecciona una de las opciones disponibles.")

        if kind in {"harmony", "atmosphere"}:
            data["palette_options"] = options
        else:
            data["options"] = options
        solution["option_id"] = option_id
        return data, solution

    def _validate_guided_configuration(self, kind, data, solution):
        if kind == "mix":
            available = set(data.get("colors", []))
            answer = set(solution.get("colors", []))
            if not answer or not answer.issubset(available):
                self.add_error(
                    "answer_colors",
                    "La respuesta debe usar pigmentos disponibles en la prueba.",
                )
        elif kind == "temperature":
            available = set(data.get("colors", []))
            warm = set(solution.get("warm", []))
            cold = set(solution.get("cold", []))
            if warm & cold or warm | cold != available:
                self.add_error(
                    "warm_colors",
                    "Clasifica cada color una sola vez, como cálido o frío.",
                )
        elif kind == "saturation":
            available = data.get("colors", [])
            answer = solution.get("order", [])
            if len(available) != len(answer) or set(available) != set(answer):
                self.add_error(
                    "answer_colors",
                    "El orden correcto debe incluir todos los colores disponibles.",
                )

    def _colors_from_value(self, value):
        colors = [color.strip() for color in value.split(",") if color.strip()]
        if not colors:
            return []
        try:
            normalized = normalize_color_list(colors)
        except ValueError as error:
            self.add_error("options_text", str(error))
            return []
        if len(set(normalized)) != len(normalized):
            self.add_error("options_text", "No repitas colores dentro de una opción.")
            return []
        return normalized

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get("kind")
        data = cleaned_data.get("data")
        solution = cleaned_data.get("solution")
        raw_configuration = any(
            str(self.data.get(name, "")).strip()
            for name in ("data", "solution")
        )
        if kind and (self._has_guided_input() or not raw_configuration):
            data, solution = self._build_guided_configuration(kind)
            cleaned_data["data"] = data
            cleaned_data["solution"] = solution
            self._validate_guided_configuration(kind, data, solution)
            return cleaned_data
        if not kind or data is None or solution is None:
            return cleaned_data

        if kind == "mix":
            if isinstance(solution.get("correct_combination"), list):
                options = level_options(data)
                correct_combination = solution["correct_combination"]
                option_ids = {option["id"] for option in options}
                if not options:
                    self.add_error("data", "Agrega opciones de pigmentos con id y color.")
                if (
                    not correct_combination
                    or any(not isinstance(option_id, str) for option_id in correct_combination)
                    or len(set(correct_combination)) != len(correct_combination)
                    or not set(correct_combination).issubset(option_ids)
                ):
                    self.add_error(
                        "solution",
                        "correct_combination debe listar ids de pigmentos disponibles.",
                    )
            else:
                self._validate_color_sequence(
                    data.get("colors"),
                    solution.get("colors"),
                    data_message="Agrega los pigmentos disponibles en data.colors.",
                    solution_message="Indica los pigmentos correctos en solution.colors.",
                    allow_subset=True,
                )
            return cleaned_data

        if kind == "rgb":
            reference = data.get("reference_color")
            target = solution.get("rgb")
            if not isinstance(reference, str):
                self.add_error("data", "Indica el color objetivo en reference_color.")
            else:
                try:
                    normalize_color_list([reference])
                except ValueError as error:
                    self.add_error("data", str(error))
            if (
                not isinstance(target, list)
                or len(target) != 3
                or any(type(channel) is not int or not 0 <= channel <= 255 for channel in target)
            ):
                self.add_error(
                    "solution",
                    "solution.rgb debe contener tres enteros entre 0 y 255.",
                )
            return cleaned_data

        if kind == "temperature":
            try:
                colors = normalize_color_list(data.get("colors"))
            except ValueError as error:
                self.add_error("data", str(error))
                return cleaned_data
            try:
                warm = normalize_color_list(solution.get("warm"))
                cold = normalize_color_list(solution.get("cold"))
            except ValueError as error:
                self.add_error("solution", str(error))
                return cleaned_data
            if not colors:
                self.add_error("data", "Agrega los pigmentos disponibles en data.colors.")
            if len(set(colors)) != len(colors):
                self.add_error("data", "No repitas colores en data.colors.")
            if set(warm) & set(cold) or set(warm) | set(cold) != set(colors):
                self.add_error(
                    "solution",
                    "Los colores cálidos y fríos deben clasificar cada pigmento una sola vez.",
                )
            return cleaned_data

        if kind == "saturation":
            self._validate_color_sequence(
                data.get("colors"),
                solution.get("order"),
                data_message="Agrega los pigmentos disponibles en data.colors.",
                solution_message="solution.order debe ordenar todos los pigmentos.",
            )
            return cleaned_data

        options = level_options(data)
        if not options:
            self.add_error(
                "data",
                "Este tipo de nivel necesita opciones o paletas con un identificador.",
            )
            return cleaned_data

        correct_id = correct_option_id(solution)
        if correct_id is None:
            self.add_error(
                "solution",
                "Indica option_id o correct_option_id para la respuesta correcta.",
            )
        elif correct_id not in {option["id"] for option in options}:
            self.add_error(
                "solution",
                "La respuesta correcta debe coincidir con una opción de data.",
            )
        return cleaned_data

    def _validate_color_sequence(
        self,
        available,
        expected,
        *,
        data_message,
        solution_message,
        allow_subset=False,
    ):
        try:
            available_colors = normalize_color_list(available)
        except ValueError:
            self.add_error("data", data_message)
            return
        try:
            expected_colors = normalize_color_list(expected)
        except ValueError:
            self.add_error("solution", solution_message)
            return

        if not available_colors or len(set(available_colors)) != len(available_colors):
            self.add_error("data", data_message)
        if not expected_colors:
            self.add_error("solution", solution_message)
            return

        if len(set(expected_colors)) != len(expected_colors):
            self.add_error("solution", solution_message)
            return

        available_set = set(available_colors)
        expected_set = set(expected_colors)
        if (
            (allow_subset and not expected_set.issubset(available_set))
            or (not allow_subset and expected_set != available_set)
        ):
            self.add_error("solution", solution_message)
