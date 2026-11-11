from django import forms

from .level_data import correct_option_id, level_options
from .models import Level
from .services import normalize_color_list


class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = (
            "number",
            "kind",
            "title",
            "instruction",
            "data",
            "solution",
            "active",
        )
        labels = {
            "number": "Número de nivel",
            "kind": "Tipo de reto",
            "title": "Título",
            "instruction": "Instrucciones para el jugador",
            "data": "Datos visibles del nivel (JSON)",
            "solution": "Respuesta correcta privada (JSON)",
            "active": "Nivel activo",
        }
        widgets = {
            "instruction": forms.Textarea(attrs={"rows": 3}),
            "data": forms.Textarea(attrs={"rows": 10, "spellcheck": "false"}),
            "solution": forms.Textarea(attrs={"rows": 6, "spellcheck": "false"}),
        }
        help_texts = {
            "data": (
                'Objeto JSON visible. Ejemplo de opciones: '
                '{"options": [{"id": "a", "color": "#1E88E5"}]}. '
                "Para paletas: usa palette_options con id y colors."
            ),
            "solution": (
                'Objeto JSON privado. Ejemplo: {"option_id": "a"}; '
                "también se acepta correct_option_id."
            ),
            "active": "Solo los niveles activos aparecen en el perfil del jugador.",
        }

    def clean_data(self):
        data = self.cleaned_data["data"]
        if not isinstance(data, dict):
            raise forms.ValidationError("Los datos del nivel deben ser un objeto JSON.")
        return data

    def clean_solution(self):
        solution = self.cleaned_data["solution"]
        if not isinstance(solution, dict):
            raise forms.ValidationError("La solución debe ser un objeto JSON.")
        return solution

    def clean(self):
        cleaned_data = super().clean()
        kind = cleaned_data.get("kind")
        data = cleaned_data.get("data")
        solution = cleaned_data.get("solution")
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
