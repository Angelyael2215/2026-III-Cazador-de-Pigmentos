import math
import re

from django.utils import timezone

from .level_data import correct_option_id, level_options
from .models import LevelProgress


def normalize_color(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError("Cada color debe tener formato #RRGGBB.")
    return value.upper()


def normalize_color_list(value):
    if not isinstance(value, list):
        raise ValueError("Se esperaba una lista de colores.")
    return [normalize_color(color) for color in value]


def validate_answer(level, answer):
    solution = level.solution

    if level.kind == "mix":
        selected = sorted(normalize_color_list(answer.get("colors")))
        correct = sorted(normalize_color_list(solution["colors"]))
        return selected == correct

    if level.kind == "rgb":
        rgb = answer.get("rgb")
        target = solution["rgb"]

        if (
            not isinstance(rgb, list)
            or len(rgb) != 3
            or any(type(channel) is not int or not 0 <= channel <= 255 for channel in rgb)
        ):
            raise ValueError("rgb debe contener tres enteros entre 0 y 255.")

        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, target)))
        return distance < 55

    if level.kind == "temperature":
        warm = set(normalize_color_list(answer.get("warm")))
        cold = set(normalize_color_list(answer.get("cold")))
        expected_warm = set(normalize_color_list(solution["warm"]))
        expected_cold = set(normalize_color_list(solution["cold"]))
        return warm == expected_warm and cold == expected_cold

    if level.kind == "saturation":
        selected = normalize_color_list(answer.get("order"))
        correct = normalize_color_list(solution["order"])
        return selected == correct

    option_id = answer.get("option_id")
    expected_option_id = correct_option_id(solution)
    available_option_ids = {
        option["id"] for option in level_options(level.data)
    }
    if not available_option_ids or expected_option_id not in available_option_ids:
        raise ValueError("La estructura de opciones de este nivel no es válida.")
    if not isinstance(option_id, str):
        raise ValueError("Se requiere option_id.")
    if option_id not in available_option_ids:
        raise ValueError("La opción seleccionada no pertenece a este nivel.")
    return option_id == expected_option_id


def submit_level_answer(player, level, answer):
    correct = validate_answer(level, answer)
    progress, _ = LevelProgress.objects.get_or_create(player=player, level=level)
    progress = LevelProgress.objects.select_for_update().get(pk=progress.pk)
    progress.attempts += 1

    earned_xp = 0
    earned_pigments = 0
    if correct and not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()
        earned_xp = 10
        earned_pigments = 1
        player.xp += earned_xp
        player.pigments += earned_pigments
        player.current_level_reached = max(
            player.current_level_reached,
            level.number + 1,
        )
        player.save()

    progress.save()
    return progress, correct, earned_xp, earned_pigments
