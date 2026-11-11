from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from usuarios.crud_mixins import (
    CrudDeleteMixin,
    CrudFormMixin,
    CrudListContextMixin,
)
from usuarios.permissions import user_has_permission

from .models import Logro, Nivel, Progreso, UsuarioLogro

class NivelListView(CrudListContextMixin, ListView):
    model = Nivel
    permission_required = "niveles.view_nivel"
    route_prefix = "nivel"


class NivelCreateView(CrudFormMixin, CreateView):
    model = Nivel
    fields = "__all__"
    permission_required = "niveles.add_nivel"
    route_prefix = "nivel"
    success_url = reverse_lazy("nivel_lista")


class NivelUpdateView(CrudFormMixin, UpdateView):
    model = Nivel
    fields = "__all__"
    permission_required = "niveles.change_nivel"
    route_prefix = "nivel"
    success_url = reverse_lazy("nivel_lista")


class NivelDeleteView(CrudDeleteMixin, DeleteView):
    model = Nivel
    permission_required = "niveles.delete_nivel"
    route_prefix = "nivel"
    success_url = reverse_lazy("nivel_lista")


class ProgresoListView(CrudListContextMixin, ListView):
    model = Progreso
    permission_required = "niveles.view_progreso"
    route_prefix = "progreso"


class ProgresoCreateView(CrudFormMixin, CreateView):
    model = Progreso
    fields = "__all__"
    permission_required = "niveles.add_progreso"
    route_prefix = "progreso"
    success_url = reverse_lazy("progreso_lista")


class ProgresoUpdateView(CrudFormMixin, UpdateView):
    model = Progreso
    fields = "__all__"
    permission_required = "niveles.change_progreso"
    route_prefix = "progreso"
    success_url = reverse_lazy("progreso_lista")


class ProgresoDeleteView(CrudDeleteMixin, DeleteView):
    model = Progreso
    permission_required = "niveles.delete_progreso"
    route_prefix = "progreso"
    success_url = reverse_lazy("progreso_lista")


class LogroListView(CrudListContextMixin, ListView):
    model = Logro
    permission_required = "niveles.view_logro"
    route_prefix = "logro"


class LogroCreateView(CrudFormMixin, CreateView):
    model = Logro
    fields = "__all__"
    permission_required = "niveles.add_logro"
    route_prefix = "logro"
    success_url = reverse_lazy("logro_lista")


class LogroUpdateView(CrudFormMixin, UpdateView):
    model = Logro
    fields = "__all__"
    permission_required = "niveles.change_logro"
    route_prefix = "logro"
    success_url = reverse_lazy("logro_lista")


class LogroDeleteView(CrudDeleteMixin, DeleteView):
    model = Logro
    permission_required = "niveles.delete_logro"
    route_prefix = "logro"
    success_url = reverse_lazy("logro_lista")


class UsuarioLogroListView(CrudListContextMixin, ListView):
    model = UsuarioLogro
    permission_required = "niveles.view_usuariologro"
    route_prefix = "usuariologro"


class UsuarioLogroCreateView(CrudFormMixin, CreateView):
    model = UsuarioLogro
    fields = "__all__"
    permission_required = "niveles.add_usuariologro"
    route_prefix = "usuariologro"
    success_url = reverse_lazy("usuariologro_lista")


class UsuarioLogroUpdateView(CrudFormMixin, UpdateView):
    model = UsuarioLogro
    fields = "__all__"
    permission_required = "niveles.change_usuariologro"
    route_prefix = "usuariologro"
    success_url = reverse_lazy("usuariologro_lista")


class UsuarioLogroDeleteView(CrudDeleteMixin, DeleteView):
    model = UsuarioLogro
    permission_required = "niveles.delete_usuariologro"
    route_prefix = "usuariologro"
    success_url = reverse_lazy("usuariologro_lista")