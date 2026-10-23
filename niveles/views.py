from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .models import Logro, Nivel, Progreso, UsuarioLogro


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