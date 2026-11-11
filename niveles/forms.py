from django import forms

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
                'Objeto JSON visible para el jugador. Ejemplo: '
                '{"options": [{"id": "a", "color": "#1E88E5"}]}'
            ),
            "solution": (
                'Objeto JSON privado de validación. Ejemplo: {"option_id": "a"}'
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
