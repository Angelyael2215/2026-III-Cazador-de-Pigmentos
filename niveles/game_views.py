import json
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.models import PerfilUsuario
from .level_data import level_options
from .models import Level, LevelProgress, Player
from .services import submit_level_answer


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
            {"id": color, "label": color, "color": color}
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
            "label": option.get("name") or option.get("label") or option["id"],
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
        for key in ("reference_color", "target_color", "target_hex", "target_background")
        if isinstance((value := data.get(key)), str)
        and re.fullmatch(r"#[0-9a-fA-F]{6}", value)
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
        else:
            if correct:
                if earned_xp:
                    messages.success(request, "¡Correcto! Ganaste 10 XP y 1 gema.")
                else:
                    messages.success(request, "¡Correcto! Ya habías completado este nivel.")
            else:
                messages.warning(request, "Respuesta incorrecta. Inténtalo de nuevo.")
            return redirect("jugar_nivel", number=number)

    progress = LevelProgress.objects.filter(player=player, level=level).first()
    discovered_result = discovered_mix_result(level, progress)
    return render(
        request,
        "niveles/jugar_nivel.html",
        {
            "level": level,
            "progress": progress,
            "discovered_result": discovered_result,
            "colors": level_colors(level),
            "mix_options": level_mix_options(level),
            "options": level_options(level.data),
            "visual_data": level_visual_data(level),
            "brand_name": (
                level.data.get("brand_name")
                if isinstance(level.data, dict)
                else None
            ),
        },
    )
