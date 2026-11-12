from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotAllowed
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.db.models import Count, Q
from .forms import (
    AsignarPermisosUsuarioForm,
    RolForm,
    AsignarRolUsuarioForm,

    RegistroUsuarioForm,
    describe_permission,
    group_permissions_by_action,
    group_permissions_by_app_model_action,
    search_permissions,
)
from .models import PerfilUsuario, EvaluacionAccesibilidad
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .permissions import (
    AppPermissionRequiredMixin,
    get_management_sections,
    has_management_access,
    user_has_permission,
)
from niveles.models import Level, LevelProgress, Nivel, Player
from django.db import models

# FUNCIÓN DE VERIFICACIÓN
def es_administrador(user):
    return (
        user.is_authenticated
        and user.is_active
        and (user.is_superuser or user.is_staff)
    )


#  VISTA DE REGISTRO
def registro_view(request):
    if request.user.is_authenticated:
        if es_administrador(request.user):
            return redirect('dashboard_admin')
        return redirect('bienvenida_jugador')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            PerfilUsuario.objects.get_or_create(usuario=usuario)
            EvaluacionAccesibilidad.objects.get_or_create(
                usuario=usuario,
                defaults={
                    "color_fondo_hex": "#FFFFFF",
                    "color_texto_hex": "#000000",
                    "ratio_contraste": 21.00,
                    "cumple_wcag_aa": True,
                    "cumple_wcag_aaa": True,
                },
            )
            Player.objects.get_or_create(user=usuario)
            return redirect('login')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'usuarios/registro.html', {'form': form})


# VISTA PARA JUGADORES NORMALES
@login_required
def bienvenida_jugador(request):
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=request.user)
    player, _ = Player.objects.get_or_create(user=request.user)
    progress = {
        item.level_id: item
        for item in LevelProgress.objects.filter(player=player)
    }
    levels = [
        {
            "level": level,
            "unlocked": level.number <= player.current_level_reached,
            "completed": (
                progress[level.id].completed if level.id in progress else False
            ),
        }
        for level in Level.objects.filter(active=True).order_by("number")
    ]
    return render(
        request,
        "usuarios/bienvenida_jugador.html",
        {"perfil": perfil, "player": player, "levels": levels},
    )

@login_required
def mapa_niveles(request):
    player, _ = Player.objects.get_or_create(user=request.user)
    progress_by_level = {
        item.level_id: item
        for item in LevelProgress.objects.filter(player=player)
    }
    levels = [
        {
            "level": level,
            "unlocked": level.number <= player.current_level_reached,
            "completed": (
                progress_by_level[level.pk].completed
                if level.pk in progress_by_level
                else False
            ),
        }
        for level in Level.objects.filter(active=True, number__lte=25).order_by("number")
    ]
    return render(request, "usuarios/mapa.html", {"levels": levels})

def is_admin(user):
    return es_administrador(user)
@login_required
def ajustes_jugador(request):
    ajustes, _ = EvaluacionAccesibilidad.objects.get_or_create(
        usuario=request.user,
        defaults={
            "color_fondo_hex": "#FFFFFF",
            "color_texto_hex": "#000000",
            "ratio_contraste": 21.00,
            "cumple_wcag_aa": True,
            "cumple_wcag_aaa": True,
        },
    )
    if request.method == "POST":
        ajustes.color_fondo_hex = request.POST.get("color_fondo_hex", "#FFFFFF")
        ajustes.color_texto_hex = request.POST.get("color_texto_hex", "#000000")
        ajustes.save()
        return redirect("bienvenida_jugador")

    return render(request, "usuarios/ajustes.html", {"ajustes": ajustes})


# VISTAS PROTEGIDAS (SOLO ADMINISTRADORES)

@user_passes_test(has_management_access, login_url='login')
def dashboard_admin(request):
    is_administrator = es_administrador(request.user)
    context = {
        'is_administrator': is_administrator,
        'management_sections': (
            [] if is_administrator else get_management_sections(request.user)
        ),
    }
    if is_administrator:
        context.update({
            'total_usuarios': User.objects.count(),
            'total_roles': Group.objects.count(),
            'total_permisos': Permission.objects.count(),
            'total_niveles': Level.objects.count(),
        })
    return render(request, 'usuarios/dashboard.html', context)


@user_passes_test(
    lambda user: user_has_permission(user, "auth.view_permission"),
    login_url='login',
)
@require_GET
def gestion_permisos(request):
    permisos = Permission.objects.select_related("content_type").order_by(
        "content_type__app_label",
        "content_type__model",
        "codename",
    )
    query = request.GET.get('q', '').strip()
    permisos = search_permissions(permisos, query)

    return render(
        request,
        'usuarios/gestion_permisos.html',
        {
            'permisos': permisos,
            'permission_action_categories': group_permissions_by_action(permisos),
            'query': query,
        },
    )


@user_passes_test(
    lambda user: user_has_permission(user, "auth.view_group")
    or user_has_permission(user, "auth.add_group"),
    login_url='login',
)
def gestion_roles(request):
    can_view = user_has_permission(request.user, "auth.view_group")
    roles = Group.objects.none()
    search_query = request.GET.get("q", "").strip()
    if can_view:
        roles = (
            Group.objects.annotate(user_count=Count("user", distinct=True))
            .prefetch_related('permissions__content_type')
            .order_by("name")
        )
        if search_query:
            roles = roles.filter(name__icontains=search_query)
        unfiltered_count = Group.objects.count()
        paginator = Paginator(roles, 20)
        page_obj = paginator.get_page(request.GET.get("page"))
        roles = page_obj.object_list
        for role in roles:
            role.permission_groups = group_permissions_by_app_model_action(
                role.permissions.all()
            )
    else:
        unfiltered_count = 0
        paginator = Paginator([], 20)
        page_obj = paginator.get_page(1)
    role_query_params = request.GET.copy()
    role_query_params.pop("page", None)
    can_add = user_has_permission(request.user, "auth.add_group")
    if request.method == 'POST' and not can_add:
        raise PermissionDenied
    can_change = user_has_permission(request.user, "auth.change_group")
    form = (
        RolForm(
            request.POST or None,
            allow_permissions=can_change,
        )
        if can_add
        else None
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_roles')
    return render(
        request,
        'usuarios/gestion_roles.html',
        {
            'roles': roles,
            'form': form,
            'can_add': can_add,
            'can_view': can_view,
            'can_change': can_change,
            'can_delete': user_has_permission(request.user, "auth.delete_group"),
            'search_query': search_query,
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': page_obj.has_other_pages(),
            'has_role_filters': bool(search_query),
            'has_unfiltered_roles': unfiltered_count > 0,
            'total_results': paginator.count,
            'query_string': role_query_params.urlencode(),
        },
    )


@user_passes_test(
    lambda user: user_has_permission(user, "auth.change_group"),
    login_url='login',
)
def editar_rol(request, role_id):
    rol = get_object_or_404(Group, id=role_id)
    form = RolForm(request.POST or None, instance=rol)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_roles')
    return render(request, 'usuarios/editar_rol.html', {'form': form, 'rol': rol})


@user_passes_test(
    lambda user: user_has_permission(user, "auth.view_user")
    or user_has_permission(user, "auth.add_user"),
    login_url='login',
)
def gestion_usuarios_roles(request):
    can_view = user_has_permission(request.user, "auth.view_user")
    usuarios = User.objects.none()
    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("estado", "")
    role_filter = request.GET.get("rol", "")
    unfiltered_count = 0
    if can_view:
        usuarios = User.objects.all().prefetch_related(
            'groups__permissions__content_type',
            'user_permissions__content_type',
        )
        unfiltered_count = usuarios.count()
        if search_query:
            usuarios = usuarios.filter(
                Q(username__icontains=search_query)
                | Q(email__icontains=search_query)
            )
        if status_filter == "activo":
            usuarios = usuarios.filter(is_active=True)
        elif status_filter == "inactivo":
            usuarios = usuarios.filter(is_active=False)
        else:
            status_filter = ""
        if role_filter.isdecimal() and Group.objects.filter(pk=role_filter).exists():
            usuarios = usuarios.filter(groups__pk=role_filter).distinct()
        else:
            role_filter = ""

        paginator = Paginator(usuarios.order_by("username", "pk"), 20)
        page_obj = paginator.get_page(request.GET.get("page"))
        usuarios = page_obj.object_list
        for usuario in usuarios:
            effective_permissions = {}
            for role in usuario.groups.all():
                for permission in role.permissions.all():
                    item = effective_permissions.setdefault(
                        permission.pk,
                        {
                            **describe_permission(permission),
                            "codename": permission.codename,
                            "sources": set(),
                        },
                    )
                    item["sources"].add(f"Rol: {role.name}")
            for permission in usuario.user_permissions.all():
                item = effective_permissions.setdefault(
                    permission.pk,
                    {
                        **describe_permission(permission),
                        "codename": permission.codename,
                        "sources": set(),
                    },
                )
                item["sources"].add("Individual")
            usuario.effective_permissions = [
                {**item, "sources": ", ".join(sorted(item["sources"]))}
                for item in effective_permissions.values()
            ]
    else:
        paginator = Paginator([], 20)
        page_obj = paginator.get_page(1)
    query_params = request.GET.copy()
    query_params.pop("page", None)
    has_user_filters = bool(
        search_query or status_filter or role_filter
    )
    return render(
        request,
        'usuarios/gestion_usuarios.html',
        {
            'usuarios': usuarios,
            'roles': Group.objects.order_by("name"),
            'search_query': search_query,
            'status_filter': status_filter,
            'role_filter': role_filter,
            'can_view_user': can_view,
            'can_add_user': user_has_permission(request.user, "auth.add_user"),
            'can_change_user': user_has_permission(request.user, "auth.change_user"),
            'can_delete_user': user_has_permission(request.user, "auth.delete_user"),
            'can_assign_roles': es_administrador(request.user),
            'can_view_user_permissions': (
                user_has_permission(request.user, "auth.view_user")
                or user_has_permission(request.user, "auth.change_user")
            ),
            'page_obj': page_obj,
            'paginator': paginator,
            'is_paginated': page_obj.has_other_pages(),
            'has_user_filters': has_user_filters,
            'has_unfiltered_users': unfiltered_count > 0,
            'total_results': paginator.count,
            'query_string': query_params.urlencode(),
        },
    )


@user_passes_test(
    lambda user: user_has_permission(user, "auth.change_user")
    and user_has_permission(user, "auth.change_group"),
    login_url='login',
)
def asignar_roles_usuario(request, user_id):
    usuario_obj = get_object_or_404(User, id=user_id)
    form = AsignarRolUsuarioForm(request.POST or None, instance=usuario_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_usuarios_roles')
    return render(request, 'usuarios/asignar_roles.html', {'form': form, 'usuario_obj': usuario_obj})


@login_required
def detalle_nivel(request, numero_nivel):
    get_object_or_404(Level, number=numero_nivel, active=True)
    return redirect("jugar_nivel", number=numero_nivel)


@user_passes_test(
    lambda user: user_has_permission(user, "auth.view_user")
    or user_has_permission(user, "auth.change_user"),
    login_url='login',
)
def asignar_permisos_usuario(request, user_id):
    can_change = user_has_permission(request.user, "auth.change_user")
    if request.method == 'POST' and not can_change:
        raise PermissionDenied

    usuario_obj = get_object_or_404(User, id=user_id)
    form = AsignarPermisosUsuarioForm(
        request.POST or None,
        instance=usuario_obj,
        allow_changes=can_change,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_usuarios_roles')
    return render(
        request,
        'usuarios/asignar_permisos_usuario.html',
        {
            'form': form,
            'usuario_obj': usuario_obj,
            'can_change': can_change,
        },
    )

@user_passes_test(
    lambda user: user_has_permission(user, "auth.delete_group"),
    login_url='login',
)
def eliminar_rol(request, role_id):
    rol = get_object_or_404(Group, id=role_id)
    if request.method == 'POST':
        rol.delete()
        return redirect('gestion_roles')
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(
        request,
        "usuarios/confirmar_eliminar_rol.html",
        {"rol": rol},
    )


@user_passes_test(
    lambda user: user_has_permission(user, "auth.change_user"),
    login_url='login',
)
def estado_usuario(request, user_id, accion):
    if accion not in {"activar", "desactivar"}:
        raise PermissionDenied

    usuario_obj = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        usuario_obj.is_active = accion == "activar"
        usuario_obj.save(update_fields=["is_active"])
        return redirect("gestion_usuarios_roles")

    return render(
        request,
        "usuarios/confirmar_estado_usuario.html",
        {"usuario_obj": usuario_obj, "accion": accion},
    )


@user_passes_test(
    lambda user: user_has_permission(user, "auth.change_user"),
    login_url='login',
)
def cambiar_contrasena_usuario(request, user_id):
    usuario_obj = get_object_or_404(User, pk=user_id)
    form = SetPasswordForm(usuario_obj, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("gestion_usuarios_roles")
    return render(
        request,
        "usuarios/cambiar_contrasena_usuario.html",
        {"form": form, "usuario_obj": usuario_obj},
    )


class UsuarioUpdateView(LoginRequiredMixin, AppPermissionRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email']
    permission_required = "auth.change_user"
    template_name = 'usuarios/crud/model_form.html'
    success_url = reverse_lazy('gestion_usuarios_roles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_usuarios_roles'
        context['model_label'] = 'Editar usuario'
        return context

class UsuarioDeleteView(LoginRequiredMixin, AppPermissionRequiredMixin, DeleteView):
    model = User
    permission_required = "auth.delete_user"
    template_name = 'usuarios/confirmar_eliminar_usuario.html'
    success_url = reverse_lazy('gestion_usuarios_roles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["usuario_obj"] = self.object
        return context


class UsuarioCreateView(LoginRequiredMixin, AppPermissionRequiredMixin, CreateView):
    model = User
    form_class = RegistroUsuarioForm
    permission_required = "auth.add_user"
    template_name = 'usuarios/crud/model_form.html'
    success_url = reverse_lazy('gestion_usuarios_roles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_usuarios_roles'
        context['model_label'] = 'Crear usuario'
        return context
