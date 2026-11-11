from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .crud_mixins import (
    CrudDeleteMixin,
    CrudFormMixin,
    CrudListContextMixin,
)
from .permissions import user_has_permission
from .models import EvaluacionAccesibilidad, PerfilUsuario


class PerfilListView(CrudListContextMixin, ListView):
    model = PerfilUsuario
    permission_required = "usuarios.view_perfilusuario"
    route_prefix = "perfil"


class PerfilCreateView(CrudFormMixin, CreateView):
    model = PerfilUsuario
    fields = "__all__"
    permission_required = "usuarios.add_perfilusuario"
    route_prefix = "perfil"
    success_url = reverse_lazy("perfil_lista")


class PerfilUpdateView(CrudFormMixin, UpdateView):
    model = PerfilUsuario
    fields = "__all__"
    permission_required = "usuarios.change_perfilusuario"
    route_prefix = "perfil"
    success_url = reverse_lazy("perfil_lista")


class PerfilDeleteView(CrudDeleteMixin, DeleteView):
    model = PerfilUsuario
    permission_required = "usuarios.delete_perfilusuario"
    route_prefix = "perfil"
    success_url = reverse_lazy("perfil_lista")


class EvaluacionListView(CrudListContextMixin, ListView):
    model = EvaluacionAccesibilidad
    permission_required = "usuarios.view_evaluacionaccesibilidad"
    route_prefix = "evaluacion"


class EvaluacionCreateView(CrudFormMixin, CreateView):
    model = EvaluacionAccesibilidad
    fields = "__all__"
    permission_required = "usuarios.add_evaluacionaccesibilidad"
    route_prefix = "evaluacion"
    success_url = reverse_lazy("evaluacion_lista")


class EvaluacionUpdateView(CrudFormMixin, UpdateView):
    model = EvaluacionAccesibilidad
    fields = "__all__"
    permission_required = "usuarios.change_evaluacionaccesibilidad"
    route_prefix = "evaluacion"
    success_url = reverse_lazy("evaluacion_lista")


class EvaluacionDeleteView(CrudDeleteMixin, DeleteView):
    model = EvaluacionAccesibilidad
    permission_required = "usuarios.delete_evaluacionaccesibilidad"
    route_prefix = "evaluacion"
    success_url = reverse_lazy("evaluacion_lista")