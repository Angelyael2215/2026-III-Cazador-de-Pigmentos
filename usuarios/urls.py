from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('jugador/', views.bienvenida_jugador, name='bienvenida_jugador'),
    path('', views.dashboard_admin, name='dashboard_admin'),
    path('permisos/', views.gestion_permisos, name='gestion_permisos'),
    path('roles/', views.gestion_roles, name='gestion_roles'),
    path('roles/<int:role_id>/editar/', views.editar_rol, name='editar_rol'),
    path('usuarios/', views.gestion_usuarios_roles, name='gestion_usuarios_roles'),
    path('usuarios/<int:user_id>/roles/', views.asignar_roles_usuario, name='asignar_roles_usuario'),
]