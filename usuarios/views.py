from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied
from .forms import RolForm, AsignarRolUsuarioForm, PermisoForm, RegistroUsuarioForm
from .models import PerfilUsuario

# --- FUNCIÓN DE VERIFICACIÓN: Solo permite Superusuarios o Staff ---
def es_administrador(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


# --- VISTA DE REGISTRO (PÚBLICA) ---
def registro_view(request):
    if request.user.is_authenticated:
        if es_administrador(request.user):
            return redirect('dashboard_admin')
        return render(request, 'usuarios/bienvenida_jugador.html')
        
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            # Se crea automáticamente su perfil de jugador con datos básicos
            PerfilUsuario.objects.create(usuario=usuario)
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
        
    return render(request, 'usuarios/registro.html', {'form': form})


# --- VISTA DE LOGIN ---
def login_view(request):
    if request.user.is_authenticated:
        if es_administrador(request.user):
            return redirect('dashboard_admin')
        return redirect('bienvenida_jugador')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            
            # Si es admin, va al panel de gestión; si es jugador, a su pantalla
            if es_administrador(usuario):
                next_url = request.GET.get('next', 'dashboard_admin')
                return redirect(next_url)
            else:
                return redirect('bienvenida_jugador')
    else:
        form = AuthenticationForm()
        
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# --- VISTA PARA JUGADORES NORMALES ---
@login_required
def bienvenida_jugador(request):
    perfil = request.user.perfilusuario
    return render(request, 'usuarios/bienvenida_jugador.html', {'perfil': perfil})


# --- VISTAS PROTEGIDAS (SOLO ADMINISTRADORES) ---

@user_passes_test(es_administrador, login_url='login')
def dashboard_admin(request):
    total_usuarios = User.objects.count()
    total_roles = Group.objects.count()
    total_permisos = Permission.objects.count()
    
    context = {
        'total_usuarios': total_usuarios,
        'total_roles': total_roles,
        'total_permisos': total_permisos,
    }
    return render(request, 'usuarios/dashboard.html', context)


@user_passes_test(es_administrador, login_url='login')
def gestion_permisos(request):
    permisos = Permission.objects.all().select_related('content_type').order_by('content_type__app_label', 'id')
    form = PermisoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_permisos')
    return render(request, 'usuarios/gestion_permisos.html', {'permisos': permisos, 'form': form})


@user_passes_test(es_administrador, login_url='login')
def gestion_roles(request):
    roles = Group.objects.all().prefetch_related('permissions')
    form = RolForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_roles')
    return render(request, 'usuarios/gestion_roles.html', {'roles': roles, 'form': form})


@user_passes_test(es_administrador, login_url='login')
def editar_rol(request, role_id):
    rol = get_object_or_404(Group, id=role_id)
    form = RolForm(request.POST or None, instance=rol)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_roles')
    return render(request, 'usuarios/editar_rol.html', {'form': form, 'rol': rol})


@user_passes_test(es_administrador, login_url='login')
def gestion_usuarios_roles(request):
    usuarios = User.objects.all().prefetch_related('groups')
    return render(request, 'usuarios/gestion_usuarios.html', {'usuarios': usuarios})


@user_passes_test(es_administrador, login_url='login')
def asignar_roles_usuario(request, user_id):
    usuario_obj = get_object_or_404(User, id=user_id)
    form = AsignarRolUsuarioForm(request.POST or None, instance=usuario_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('gestion_usuarios_roles')
    return render(request, 'usuarios/asignar_roles.html', {'form': form, 'usuario_obj': usuario_obj})