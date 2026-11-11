from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.core.exceptions import PermissionDenied
from .forms import RolForm, AsignarRolUsuarioForm, PermisoForm, RegistroUsuarioForm
from .models import PerfilUsuario, EvaluacionAccesibilidad
from niveles.models import Nivel, Progreso

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
            EvaluacionAccesibilidad.objects.create(usuario=usuario)
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
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    return render(request, 'usuarios/bienvenida_jugador.html', {'perfil': perfil})

@login_required
def mapa_niveles(request):
    # Obtenemos todos los niveles ordenados por su número
    niveles = Nivel.objects.all().order_by('numero')
    
    context = {
        'niveles': niveles,
    }
    return render(request, 'usuarios/mapa.html', context)


@login_required
def ajustes_jugador(request):
  # Buscamos de forma segura los ajustes existentes
    ajustes = EvaluacionAccesibilidad.objects.filter(usuario=request.user).first()
    
    # Si no existen, los creamos pasando todos los campos requeridos por el modelo
    if not ajustes:
        ajustes = EvaluacionAccesibilidad.objects.create(
            usuario=request.user,
            color_fondo_hex='#FFFFFF',
            color_texto_hex='#000000',
            ratio_contraste=21.00,
            cumple_wcag_aa=True,
            cumple_wcag_aaa=True
        )
    
    if request.method == 'POST':
        color_fondo = request.POST.get('color_fondo_hex', '#FFFFFF')
        color_texto = request.POST.get('color_texto_hex', '#000000')
        
        ajustes.color_fondo_hex = color_fondo
        ajustes.color_texto_hex = color_texto
        ajustes.save()
        return redirect('bienvenida_jugador')
        
    context = {
        'ajustes': ajustes,
    }
    return render(request, 'usuarios/ajustes.html', context)

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


@login_required
def detalle_nivel(request, numero_nivel):
    # Alterna entre la plantilla de mezcla o degradado según el número de nivel
    if numero_nivel % 2 == 0:
        template_name = 'niveles/plantilla_degradado.html'
    else:
        template_name = 'niveles/plantilla_mezcla.html'
        
    context = {
        'numero_nivel': numero_nivel,
    }
    return render(request, template_name, context)


@login_required
def detalle_nivel(request, numero_nivel):
    # Asignar plantilla específica según el tipo de mecánica del nivel
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