from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.permissions import app_permission_required, user_has_permission

from .forms import LevelForm
from .models import Level


@app_permission_required("niveles.view_level")
def level_list(request):
    return render(
        request,
        "niveles/management/level_list.html",
        {
            "levels": Level.objects.all(),
            "can_add": user_has_permission(request.user, "niveles.add_level"),
            "can_change": user_has_permission(request.user, "niveles.change_level"),
            "can_delete": user_has_permission(request.user, "niveles.delete_level"),
        },
    )


@app_permission_required("niveles.add_level")
def level_create(request):
    form = LevelForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        level = form.save()
        messages.success(request, f"Se creó el nivel {level.number}: {level.title}.")
        return redirect("niveles_juego_lista")
    return render(
        request,
        "niveles/management/level_form.html",
        {"form": form, "page_title": "Crear nivel"},
    )


@app_permission_required("niveles.change_level")
def level_update(request, pk):
    level = get_object_or_404(Level, pk=pk)
    form = LevelForm(request.POST or None, instance=level)
    if request.method == "POST" and form.is_valid():
        level = form.save()
        messages.success(request, f"Se actualizaron los datos del nivel {level.number}.")
        return redirect("niveles_juego_lista")
    return render(
        request,
        "niveles/management/level_form.html",
        {"form": form, "page_title": f"Editar nivel {level.number}", "level": level},
    )


@app_permission_required("niveles.delete_level")
def level_delete(request, pk):
    level = get_object_or_404(Level, pk=pk)
    if request.method == "POST":
        number = level.number
        level.delete()
        messages.success(request, f"Se eliminó el nivel {number}.")
        return redirect("niveles_juego_lista")
    return render(
        request,
        "niveles/management/level_confirm_delete.html",
        {"level": level},
    )
