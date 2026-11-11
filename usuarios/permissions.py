from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import PermissionRequiredMixin


MANAGEMENT_SECTIONS = (
    {
        "label": "Permisos",
        "view_permission": "auth.view_permission",
        "list_url": "gestion_permisos",
        "add_permission": "auth.add_permission",
        "create_url": "gestion_permisos",
    },
    {
        "label": "Roles",
        "view_permission": "auth.view_group",
        "list_url": "gestion_roles",
        "add_permission": "auth.add_group",
        "create_url": "gestion_roles",
    },
    {
        "label": "Usuarios",
        "view_permission": "auth.view_user",
        "list_url": "gestion_usuarios_roles",
        "add_permission": "auth.add_user",
        "create_url": "crear_usuario",
    },
    {
        "label": "Perfiles",
        "view_permission": "usuarios.view_perfilusuario",
        "list_url": "perfil_lista",
        "add_permission": "usuarios.add_perfilusuario",
        "create_url": "perfil_crear",
    },
    {
        "label": "Evaluaciones de accesibilidad",
        "view_permission": "usuarios.view_evaluacionaccesibilidad",
        "list_url": "evaluacion_lista",
        "add_permission": "usuarios.add_evaluacionaccesibilidad",
        "create_url": "evaluacion_crear",
    },
    {
        "label": "Niveles del juego",
        "view_permission": "niveles.view_level",
        "list_url": "niveles_juego_lista",
        "add_permission": "niveles.add_level",
        "create_url": "niveles_juego_crear",
    },
    {
        "label": "Niveles",
        "view_permission": "niveles.view_nivel",
        "list_url": "nivel_lista",
        "add_permission": "niveles.add_nivel",
        "create_url": "nivel_crear",
    },
    {
        "label": "Progresos",
        "view_permission": "niveles.view_progreso",
        "list_url": "progreso_lista",
        "add_permission": "niveles.add_progreso",
        "create_url": "progreso_crear",
    },
    {
        "label": "Logros",
        "view_permission": "niveles.view_logro",
        "list_url": "logro_lista",
        "add_permission": "niveles.add_logro",
        "create_url": "logro_crear",
    },
    {
        "label": "Logros de usuarios",
        "view_permission": "niveles.view_usuariologro",
        "list_url": "usuariologro_lista",
        "add_permission": "niveles.add_usuariologro",
        "create_url": "usuariologro_crear",
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
