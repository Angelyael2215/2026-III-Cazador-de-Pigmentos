from django.urls import path

from . import views
from .auth_views import AppLoginView, AppLogoutView
from .crud_views import (
    EvaluacionCreateView,
    EvaluacionDeleteView,
    EvaluacionListView,
    EvaluacionUpdateView,
    PerfilCreateView,
    PerfilDeleteView,
    PerfilListView,
    PerfilUpdateView,
)


urlpatterns = [
    path("registro/", views.registro_view, name="registro"),
    path("login/", AppLoginView.as_view(), name="login"),
    path("logout/", AppLogoutView.as_view(), name="logout"),
    path("jugador/", views.bienvenida_jugador, name="bienvenida_jugador"),
    path("", views.dashboard_admin, name="dashboard_admin"),

    path("permisos/", views.gestion_permisos, name="gestion_permisos"),
    path("roles/", views.gestion_roles, name="gestion_roles"),
    path("roles/<int:role_id>/editar/", views.editar_rol, name="editar_rol"),
    path("usuarios/", views.gestion_usuarios_roles, name="gestion_usuarios_roles"),
    path(
        "usuarios/<int:user_id>/roles/",
        views.asignar_roles_usuario,
        name="asignar_roles_usuario",
    ),
    path(
        "usuarios/<int:user_id>/permisos/",
        views.asignar_permisos_usuario,
        name="asignar_permisos_usuario",
    ),
    path("roles/<int:role_id>/eliminar/", views.eliminar_rol, name="eliminar_rol"),

    path("perfiles/", PerfilListView.as_view(), name="perfil_lista"),
    path("perfiles/nuevo/", PerfilCreateView.as_view(), name="perfil_crear"),
    path(
        "perfiles/<int:pk>/editar/",
        PerfilUpdateView.as_view(),
        name="perfil_editar",
    ),
    path(
        "perfiles/<int:pk>/eliminar/",
        PerfilDeleteView.as_view(),
        name="perfil_eliminar",
    ),

    path(
        "evaluaciones/",
        EvaluacionListView.as_view(),
        name="evaluacion_lista",
    ),
    path(
        "evaluaciones/nueva/",
        EvaluacionCreateView.as_view(),
        name="evaluacion_crear",
    ),
    path(
        "evaluaciones/<int:pk>/editar/",
        EvaluacionUpdateView.as_view(),
        name="evaluacion_editar",
    ),
    path(
        "evaluaciones/<int:pk>/eliminar/",
        EvaluacionDeleteView.as_view(),
        name="evaluacion_eliminar",
    ),
    path('jugador/mapa/', views.mapa_niveles, name='mapa_niveles'),
    path('jugador/ajustes/', views.ajustes_jugador, name='ajustes_jugador'),
    path('gestion/jugador/nivel/<int:numero_nivel>/', views.detalle_nivel, name='detalle_nivel'),
    path('crear/', views.UsuarioCreateView.as_view(), name='crear_usuario'),
    path('editar/<int:pk>/', views.UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('eliminar/<int:pk>/', views.UsuarioDeleteView.as_view(), name='eliminar_usuario'),
]