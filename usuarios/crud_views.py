from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .models import EvaluacionAccesibilidad, PerfilUsuario


class CrudAccessMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True
    route_prefix = ""

    def get_queryset(self):
        queryset = super().get_queryset()
        has_usuario_field = any(
            field.name == "usuario" for field in self.model._meta.fields
        )

        if has_usuario_field and not (
            self.request.user.is_staff or self.request.user.is_superuser
        ):
            queryset = queryset.filter(usuario=self.request.user)

        return queryset

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        has_usuario_field = any(
            field.name == "usuario" for field in self.model._meta.fields
        )

        if has_usuario_field and not (
            self.request.user.is_staff or self.request.user.is_superuser
        ):
            form.fields.pop("usuario", None)

        return form

    def form_valid(self, form):
        has_usuario_field = any(
            field.name == "usuario" for field in self.model._meta.fields
        )

        if has_usuario_field and not (
            self.request.user.is_staff or self.request.user.is_superuser
        ):
            form.instance.usuario = self.request.user

        return super().form_valid(form)


class CrudListContextMixin(CrudAccessMixin):
    template_name = "usuarios/crud/model_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [
            field for field in self.model._meta.fields
            if not field.primary_key
        ]

        context["model_label"] = self.model._meta.verbose_name_plural.title()
        context["headers"] = [field.verbose_name.title() for field in fields]
        context["rows"] = [
            {
                "object": obj,
                "values": [getattr(obj, field.name) for field in fields],
            }
            for obj in context["object_list"]
        ]

        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        user = self.request.user

        context["create_url"] = f"{self.route_prefix}_crear"
        context["update_url"] = f"{self.route_prefix}_editar"
        context["delete_url"] = f"{self.route_prefix}_eliminar"
        context["can_add"] = user.has_perm(f"{app_label}.add_{model_name}")
        context["can_change"] = user.has_perm(f"{app_label}.change_{model_name}")
        context["can_delete"] = user.has_perm(f"{app_label}.delete_{model_name}")

        return context


class CrudFormMixin(CrudAccessMixin):
    template_name = "usuarios/crud/model_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_label"] = self.model._meta.verbose_name.title()
        context["list_url"] = f"{self.route_prefix}_lista"
        return context


class CrudDeleteMixin(CrudAccessMixin):
    template_name = "usuarios/crud/model_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_label"] = self.model._meta.verbose_name.title()
        context["list_url"] = f"{self.route_prefix}_lista"
        return context


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