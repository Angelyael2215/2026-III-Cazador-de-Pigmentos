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
    if not isinstance(solution, dict):
        raise ValueError("La configuración privada de este nivel no es válida.")

    if level.kind == "mix":
        correct_combination = solution.get("correct_combination")
        if correct_combination is not None:
            options = level_options(level.data)
            available_ids = {option["id"] for option in options}
            if (
                not isinstance(correct_combination, list)
                or not correct_combination
                or any(not isinstance(option_id, str) for option_id in correct_combination)
                or len(set(correct_combination)) != len(correct_combination)
                or not set(correct_combination).issubset(available_ids)
            ):
                raise ValueError("La combinación correcta de este nivel no está configurada.")

            selected = answer.get("colors")
            if not isinstance(selected, list) or any(
                not isinstance(option_id, str) for option_id in selected
            ) or len(set(selected)) != len(selected):
                raise ValueError("Selecciona una combinación válida de pigmentos.")

            option_by_color = {
                option["colors"][0].upper(): option["id"]
                for option in options
                if option["colors"]
            }
            selected_ids = {
                option_id
                if option_id in available_ids
                else option_by_color.get(option_id.upper(), option_id)
                for option_id in selected
            }
            if not selected_ids.issubset(available_ids):
                raise ValueError("Un pigmento seleccionado no pertenece a este nivel.")
            return selected_ids == set(correct_combination)

        if not isinstance(solution.get("colors"), list):
            raise ValueError("La mezcla correcta de este nivel no está configurada.")
        selected = sorted(normalize_color_list(answer.get("colors")))
        correct = sorted(normalize_color_list(solution["colors"]))
        return selected == correct

    if level.kind == "rgb":
        rgb = answer.get("rgb")
        target = solution.get("rgb")

        if (
            not isinstance(rgb, list)
            or len(rgb) != 3
            or any(type(channel) is not int or not 0 <= channel <= 255 for channel in rgb)
        ):
            raise ValueError("rgb debe contener tres enteros entre 0 y 255.")
        if (
            not isinstance(target, list)
            or len(target) != 3
            or any(
                type(channel) is not int or not 0 <= channel <= 255
                for channel in target
            )
        ):
            raise ValueError("El color RGB objetivo de este nivel no está configurado.")

        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, target)))
        return distance < 55

    if level.kind == "temperature":
        if not isinstance(solution.get("warm"), list) or not isinstance(
            solution.get("cold"), list
        ):
            raise ValueError("La clasificación térmica de este nivel no está configurada.")
        warm = set(normalize_color_list(answer.get("warm")))
        cold = set(normalize_color_list(answer.get("cold")))
        expected_warm = set(normalize_color_list(solution["warm"]))
        expected_cold = set(normalize_color_list(solution["cold"]))
        return warm == expected_warm and cold == expected_cold

    if level.kind == "saturation":
        if not isinstance(solution.get("order"), list):
            raise ValueError("El orden de saturación de este nivel no está configurado.")
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
