from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import PermissionRequiredMixin


MANAGEMENT_SECTIONS = (
    {
        "label": "Permisos",
        "view_permission": "auth.view_permission",
        "list_url": "gestion_permisos",
        "add_permission": "auth.add_permission",
        "create_url": "gestion_permisos",
        "active_url_names": ("gestion_permisos",),
    },
    {
        "label": "Roles",
        "view_permission": "auth.view_group",
        "list_url": "gestion_roles",
        "add_permission": "auth.add_group",
        "create_url": "gestion_roles",
        "active_url_names": ("gestion_roles", "editar_rol", "eliminar_rol"),
    },
    {
        "label": "Usuarios",
        "view_permission": "auth.view_user",
        "list_url": "gestion_usuarios_roles",
        "add_permission": "auth.add_user",
        "create_url": "crear_usuario",
        "active_url_names": (
            "gestion_usuarios_roles",
            "asignar_roles_usuario",
            "asignar_permisos_usuario",
            "estado_usuario",
            "cambiar_contrasena_usuario",
            "crear_usuario",
            "editar_usuario",
            "eliminar_usuario",
        ),
    },
    {
        "label": "Perfiles",
        "view_permission": "usuarios.view_perfilusuario",
        "list_url": "perfil_lista",
        "add_permission": "usuarios.add_perfilusuario",
        "create_url": "perfil_crear",
        "active_url_names": (
            "perfil_lista",
            "perfil_crear",
            "perfil_editar",
            "perfil_eliminar",
        ),
    },
    {
        "label": "Evaluaciones de accesibilidad",
        "view_permission": "usuarios.view_evaluacionaccesibilidad",
        "list_url": "evaluacion_lista",
        "add_permission": "usuarios.add_evaluacionaccesibilidad",
        "create_url": "evaluacion_crear",
        "active_url_names": (
            "evaluacion_lista",
            "evaluacion_crear",
            "evaluacion_editar",
            "evaluacion_eliminar",
        ),
    },
    {
        "label": "Niveles del juego",
        "view_permission": "niveles.view_level",
        "list_url": "niveles_juego_lista",
        "add_permission": "niveles.add_level",
        "create_url": "niveles_juego_crear",
        "active_url_names": (
            "niveles_juego_lista",
            "niveles_juego_crear",
            "niveles_juego_editar",
            "niveles_juego_eliminar",
        ),
    },
    {
        "label": "Niveles",
        "view_permission": "niveles.view_nivel",
        "list_url": "nivel_lista",
        "add_permission": "niveles.add_nivel",
        "create_url": "nivel_crear",
        "active_url_names": (
            "nivel_lista",
            "nivel_crear",
            "nivel_editar",
            "nivel_eliminar",
        ),
    },
    {
        "label": "Progresos",
        "view_permission": "niveles.view_progreso",
        "list_url": "progreso_lista",
        "add_permission": "niveles.add_progreso",
        "create_url": "progreso_crear",
        "active_url_names": (
            "progreso_lista",
            "progreso_crear",
            "progreso_editar",
            "progreso_eliminar",
        ),
    },
    {
        "label": "Logros",
        "view_permission": "niveles.view_logro",
        "list_url": "logro_lista",
        "add_permission": "niveles.add_logro",
        "create_url": "logro_crear",
        "active_url_names": (
            "logro_lista",
            "logro_crear",
            "logro_editar",
            "logro_eliminar",
        ),
    },
    {
        "label": "Logros de usuarios",
        "view_permission": "niveles.view_usuariologro",
        "list_url": "usuariologro_lista",
        "add_permission": "niveles.add_usuariologro",
        "create_url": "usuariologro_crear",
        "active_url_names": (
            "usuariologro_lista",
            "usuariologro_crear",
            "usuariologro_editar",
            "usuariologro_eliminar",
        ),
    },
)


def user_has_permission(user, permission):
    return user.is_authenticated and user.is_active and (
        user.is_staff or user.is_superuser or user.has_perm(permission)
    )


def get_management_sections(user):
    sections = []
    for section in MANAGEMENT_SECTIONS:
        can_view = user_has_permission(user, section["view_permission"])
        can_add = user_has_permission(user, section["add_permission"])
        if can_view or can_add:
            sections.append({**section, "can_view": can_view, "can_add": can_add})
    return sections


def has_management_access(user):
    return user.is_authenticated and user.is_active and (
        user.is_staff or user.is_superuser or bool(get_management_sections(user))
    )


class AppPermissionRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        return all(
            user_has_permission(self.request.user, permission)
            for permission in self.get_permission_required()
        )


def app_permission_required(permission, login_url="login"):
    return user_passes_test(
        lambda user: user_has_permission(user, permission),
        login_url=login_url,
    )
