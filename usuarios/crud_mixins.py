from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

from .permissions import AppPermissionRequiredMixin, user_has_permission


class CrudAccessMixin(LoginRequiredMixin, AppPermissionRequiredMixin):
    raise_exception = True
    route_prefix = ""
    paginate_by = 20
    search_fields = ()
    list_filters = {}

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

    def get_list_filters(self):
        return self.list_filters

    def get_queryset(self):
        queryset = super().get_queryset()
        self.unfiltered_count = queryset.count()

        self.search_query = (
            self.request.GET.get("q", "").strip() if self.search_fields else ""
        )
        if self.search_query and self.search_fields:
            search = Q()
            for field in self.search_fields:
                search |= Q(**{f"{field}__icontains": self.search_query})
            queryset = queryset.filter(search)

        self.active_list_filters = {}
        self.list_filter_options = []
        for parameter, config in self.get_list_filters().items():
            lookup, label, choices = config
            selected = self.request.GET.get(parameter, "")
            valid_values = {str(value) for value, _ in choices}
            if selected in valid_values:
                queryset = queryset.filter(**{lookup: selected})
                self.active_list_filters[parameter] = selected
            else:
                selected = ""
            self.list_filter_options.append(
                {
                    "parameter": parameter,
                    "label": label,
                    "choices": choices,
                    "selected": selected,
                }
            )

        self.has_list_filters = bool(
            self.search_query or self.active_list_filters
        )
        if not queryset.ordered:
            queryset = queryset.order_by("pk")
        return queryset

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
        context["list_url"] = f"{self.route_prefix}_lista"
        context["update_url"] = f"{self.route_prefix}_editar"
        context["delete_url"] = f"{self.route_prefix}_eliminar"
        context["can_add"] = user_has_permission(
            user, f"{app_label}.add_{model_name}"
        )
        context["can_change"] = user_has_permission(
            user, f"{app_label}.change_{model_name}"
        )
        context["can_delete"] = user_has_permission(
            user, f"{app_label}.delete_{model_name}"
        )
        context["search_fields_available"] = bool(self.search_fields)
        context["search_query"] = self.search_query
        context["list_filter_options"] = self.list_filter_options
        context["active_list_filters"] = self.active_list_filters
        context["has_list_filters"] = self.has_list_filters
        context["total_results"] = context["paginator"].count
        context["has_unfiltered_records"] = self.unfiltered_count > 0
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["query_string"] = query_params.urlencode()
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
