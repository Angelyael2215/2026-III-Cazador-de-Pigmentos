from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from .forms import (
    AsignarPermisosUsuarioForm,
    RolForm,
    AsignarRolUsuarioForm,
    PermisoForm,
    RegistroUsuarioForm,
    describe_permission,
    group_permissions_by_action,
)
from .models import PerfilUsuario, EvaluacionAccesibilidad
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from .permissions import (
    AppPermissionRequiredMixin,
    get_management_sections,
    has_management_access,
    user_has_permission,
)
from niveles.models import Level, LevelProgress, Nivel, Player

# FUNCIÓN DE VERIFICACIÓN
def es_administrador(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


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
    niveles = Nivel.objects.all().order_by("numero")
    return render(request, "usuarios/mapa.html", {"niveles": niveles})

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
    lambda user: user_has_permission(user, "auth.view_permission")
    or user_has_permission(user, "auth.add_permission"),
    login_url='login',
)
def gestion_permisos(request):
    can_view = user_has_permission(request.user, "auth.view_permission")
    permisos = Permission.objects.none()
    if can_view:
        permisos = Permission.objects.all().select_related('content_type').order_by('content_type__app_label', 'id')
    can_add = user_has_permission(request.user, "auth.add_permission")
    if request.method == 'POST' and not can_add:
        raise PermissionDenied
    form = PermisoForm(request.POST or None) if can_add else None
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_permisos')
    return render(
        request,
        'usuarios/gestion_permisos.html',
        {
            'permisos': permisos,
            'permission_categories': group_permissions_by_action(permisos),
            'form': form,
            'can_add': can_add,
            'can_view': can_view,
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
    if can_view:
        roles = Group.objects.all().prefetch_related('permissions__content_type')
        for role in roles:
            role.permission_descriptions = [
                describe_permission(permission)
                for permission in role.permissions.all()
            ]
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
    if can_view:
        usuarios = User.objects.all().prefetch_related(
            'groups__permissions__content_type',
            'user_permissions__content_type',
        )
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
    return render(
        request,
        'usuarios/gestion_usuarios.html',
        {
            'usuarios': usuarios,
            'can_view_user': can_view,
            'can_add_user': user_has_permission(request.user, "auth.add_user"),
            'can_change_user': user_has_permission(request.user, "auth.change_user"),
            'can_delete_user': user_has_permission(request.user, "auth.delete_user"),
            'can_assign_roles': es_administrador(request.user),
        },
    )


@user_passes_test(es_administrador, login_url='login')
def asignar_roles_usuario(request, user_id):
    usuario_obj = get_object_or_404(User, id=user_id)
    form = AsignarRolUsuarioForm(request.POST or None, instance=usuario_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_usuarios_roles')
    return render(request, 'usuarios/asignar_roles.html', {'form': form, 'usuario_obj': usuario_obj})


@login_required
def detalle_nivel(request, numero_nivel):
    if numero_nivel in [1]:
        template_name = 'niveles/nivel_arrastrar.html'
    elif numero_nivel in [2, 5, 6, 15, 20]:
        template_name = 'niveles/nivel_deslizadores.html'
    elif numero_nivel in [3, 7, 16]:
        template_name = 'niveles/nivel_rueda.html'
    elif numero_nivel in [4, 8, 12, 17, 23]:
        template_name = 'niveles/nivel_seleccion.html'
    elif numero_nivel in [9, 13, 18]:
        template_name = 'niveles/nivel_simulador.html'
    else:  # Niveles 10, 11, 14, 19, 21, 22, 24, 25 (Jefe final / Alquimia / WCAG)
        template_name = 'niveles/nivel_auditor.html'

    context = {
        'numero_nivel': numero_nivel,
    }
    return render(request, template_name, context)


@user_passes_test(es_administrador, login_url='login')
def asignar_permisos_usuario(request, user_id):
    usuario_obj = get_object_or_404(User, id=user_id)
    form = AsignarPermisosUsuarioForm(
        request.POST or None,
        instance=usuario_obj,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_usuarios_roles')
    return render(
        request,
        'usuarios/asignar_permisos_usuario.html',
        {'form': form, 'usuario_obj': usuario_obj},
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
    return render(request, 'usuarios/eliminar.html', {'objeto': rol})

class UsuarioUpdateView(LoginRequiredMixin, AppPermissionRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email']
    permission_required = "auth.change_user"
    template_name = 'usuarios/crud/model_form.html'
    success_url = reverse_lazy('gestion_usuarios_roles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_usuarios_roles'
        return context

class UsuarioDeleteView(LoginRequiredMixin, AppPermissionRequiredMixin, DeleteView):
    model = User
    permission_required = "auth.delete_user"
    template_name = 'usuarios/eliminar.html'
    success_url = reverse_lazy('gestion_usuarios_roles')

class UsuarioCreateView(LoginRequiredMixin, AppPermissionRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    permission_required = "auth.add_user"
    template_name = 'usuarios/crud/model_form.html'
    success_url = reverse_lazy('gestion_usuarios_roles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_url'] = 'gestion_usuarios_roles'
        return context
