from django import forms

from .level_data import correct_option_id, level_options
from .models import Level


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
        if not data or not solution or kind in {
            "mix",
            "rgb",
            "temperature",
            "saturation",
        }:
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
