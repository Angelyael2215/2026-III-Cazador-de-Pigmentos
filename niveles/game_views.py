import json
import re
import random

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from usuarios.models import PerfilUsuario
from .level_data import level_options
from .models import Level, LevelProgress, Player
from .services import submit_level_answer


CHILD_COLOR_NAMES = {
    "#1565C0": "Azul",
    "#1E88E5": "Azul",
    "#3949AB": "Azul",
    "#3F51B5": "Azul",
    "#E53935": "Rojo",
    "#F44336": "Rojo",
    "#D81B60": "Rosa",
    "#FDD835": "Amarillo",
    "#FFEB3B": "Amarillo",
    "#FFFFFF": "Blanco",
    "#9E9E9E": "Gris",
    "#43A047": "Verde",
}


def simple_color_name(color):
    return CHILD_COLOR_NAMES.get(color.upper(), "Color")


def level_colors(level):
    data = level.data
    if not isinstance(data, dict):
        return []
    colors = data.get("colors", [])
    if not colors and isinstance(data.get("options"), list):
        colors = [
            option.get("color") if isinstance(option, dict) else option
            for option in data["options"]
        ]
    return [
        color
        for color in colors
        if isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color)
    ]


def level_mix_options(level):
    data = level.data
    if not isinstance(data, dict):
        return []

    color_list = data.get("colors")
    if isinstance(color_list, list):
        return [
            {"id": color, "label": simple_color_name(color), "color": color}
            for color in color_list
            if isinstance(color, str)
            and re.fullmatch(r"#[0-9a-fA-F]{6}", color)
        ]

    options = data.get("options")
    if not isinstance(options, list):
        return []

    return [
        {
            "id": option["id"],
            "label": (
                option.get("name")
                or option.get("label")
                or simple_color_name(option["color"])
            ),
            "color": option["color"],
        }
        for option in options
        if isinstance(option, dict)
        and isinstance(option.get("id"), str)
        and isinstance(option.get("color"), str)
        and re.fullmatch(r"#[0-9a-fA-F]{6}", option["color"])
    ]


def level_visual_data(level):
    data = level.data
    if not isinstance(data, dict):
        return {}
    return {
        key: value
        for key in (
            "reference_color",
            "target_color",
            "target_hex",
            "target_background",
            "contrast_word",
            "deficiency_type",
        )
        if isinstance((value := data.get(key)), str)
        and (key not in {"reference_color", "target_color", "target_hex", "target_background"}
             or re.fullmatch(r"#[0-9a-fA-F]{6}", value))
    }


def discovered_mix_result(level, progress):
    if level.kind != "mix" or not progress or not progress.completed:
        return None
    solution = level.solution
    result = solution.get("result") if isinstance(solution, dict) else None
    if not isinstance(result, dict):
        return None

    name = result.get("name")
    color = result.get("hex")
    if not isinstance(name, str) or not name.strip():
        return None
    if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        return None
    return {"name": name, "color": color}


@login_required
def play_level(request, number):
    level = get_object_or_404(Level, number=number, active=True)
    player, _ = Player.objects.get_or_create(user=request.user)
    if level.number > player.current_level_reached:
        raise PermissionDenied("Primero completa los niveles anteriores.")

    if request.method == "POST":
        is_ajax_answer = request.POST.get("ajax") == "1"
        try:
            answer = json.loads(request.POST.get("answer", ""))
            if not isinstance(answer, dict):
                raise ValueError("La respuesta debe tener un formato válido.")
            with transaction.atomic():
                player = Player.objects.select_for_update().get(pk=player.pk)
                progress, correct, earned_xp, earned_pigments = submit_level_answer(
                    player,
                    level,
                    answer,
                )
                if earned_pigments:
                    profile, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
                    profile.gemas += earned_pigments
                    profile.nivel_maximo_desbloqueado = max(
                        profile.nivel_maximo_desbloqueado,
                        player.current_level_reached,
                    )
                    profile.save()
        except (json.JSONDecodeError, KeyError, ValueError) as error:
            messages.error(request, str(error))
            if is_ajax_answer:
                return JsonResponse({"correct": False, "error": str(error)}, status=200)
        else:
            if correct:
                next_level = Level.objects.filter(
                    active=True,
                    number=number + 1,
                ).first()
                if is_ajax_answer:
                    next_url = (
                        reverse("jugar_nivel", args=[next_level.number])
                        if next_level
                        else reverse("mapa_niveles")
                    )
                    return JsonResponse({
                        "correct": True,
                        "next_url": next_url,
                        "earned_xp": earned_xp,
                    })
                if next_level:
                    message = (
                        "¡Muy bien! Sigue con el siguiente nivel."
                        if earned_xp
                        else "Este nivel ya estaba completo. Sigue con el siguiente."
                    )
                    messages.success(request, message)
                    return redirect("jugar_nivel", number=next_level.number)

                message = (
                    "¡Muy bien! Llegaste al final de la ruta disponible."
                    if earned_xp
                    else "Este nivel ya estaba completo."
                )
                messages.success(request, message)
                return redirect("mapa_niveles")

            if is_ajax_answer:
                return JsonResponse({"correct": False, "error": "Prueba otra vez."})
            messages.warning(request, "Prueba otra vez.")
            return redirect("jugar_nivel", number=number)

    progress = LevelProgress.objects.filter(player=player, level=level).first()
    discovered_result = discovered_mix_result(level, progress)
    colors = level_colors(level)
    if level.kind == "saturation" and len(colors) > 1:
        random.SystemRandom().shuffle(colors)
    return render(
        request,
        "niveles/jugar_nivel.html",
        {
            "level": level,
            "progress": progress,
            "discovered_result": discovered_result,
            "colors": colors,
            "mix_options": level_mix_options(level),
            "options": level_options(level.data),
            "total_levels": Level.objects.filter(active=True).count(),
            "visual_data": level_visual_data(level),
            "fixed_slots": (
                level.data.get("fixed_slots")
                if isinstance(level.data, dict)
                and isinstance(level.data.get("fixed_slots"), list)
                else None
            ),
            "situation": (
                level.data.get("situation")
                if isinstance(level.data, dict)
                and isinstance(level.data.get("situation"), str)
                else None
            ),
            "brand_name": (
                level.data.get("brand_name")
                if isinstance(level.data, dict)
                else None
            ),
        },
    )
