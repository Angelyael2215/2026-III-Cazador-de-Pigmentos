from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group, Permission

MODEL_LABELS = {
    "contenttype": "tipo de contenido",
    "evaluacionaccesibilidad": "evaluación de accesibilidad",
    "group": "rol",
    "level": "nivel del juego",
    "levelprogress": "progreso del jugador",
    "logro": "logro",
    "permission": "permiso",
    "perfilusuario": "perfil de usuario",
    "player": "jugador",
    "progreso": "progreso",
    "session": "sesión",
    "user": "usuario",
    "usuariologro": "logro de usuario",
    "nivel": "nivel",
}

APP_LABELS = {
    "admin": "Administración",
    "auth": "Autenticación y autorización",
    "contenttypes": "Tipos de contenido",
    "niveles": "Niveles",
    "sessions": "Sesiones",
    "usuarios": "Usuarios",
}

ACTION_LABELS = {
    "view": ("Ver", "Consultar la información de este tipo de registro."),
    "add": ("Crear", "Agregar registros nuevos de este tipo."),
    "change": ("Editar", "Modificar registros existentes de este tipo."),
    "delete": ("Eliminar", "Borrar registros de este tipo."),
}


def describe_permission(permission):
    action = permission.codename.split("_", 1)[0]
    model = MODEL_LABELS.get(
        permission.content_type.model,
        permission.content_type.name.lower(),
    )
    if action in ACTION_LABELS:
        action_label, action_help = ACTION_LABELS[action]
        return {
            "label": f"{action_label} {model}",
            "category": action_label,
            "description": action_help,
        }

    return {
        "label": permission.name,
        "category": "Especiales",
        "description": permission.name,
    }


def group_permissions_by_action(permissions):
    action_order = ("Ver", "Crear", "Editar", "Eliminar", "Especiales")
    categories = {name: [] for name in action_order}
    for permission in permissions:
        description = describe_permission(permission)
        categories[description["category"]].append(
            {
                "permission": permission,
                **description,
            }
        )
    return [
        {"name": name, "permissions": categories[name]}
        for name in action_order
        if categories[name]
    ]


def group_permissions_by_app_model_action(permissions):
    applications = {}
    for permission in permissions:
        app_label = permission.content_type.app_label
        application = applications.setdefault(
            app_label,
            {
                "name": APP_LABELS.get(app_label, app_label.replace("_", " ").title()),
                "models": {},
            },
        )
        model_name = MODEL_LABELS.get(
            permission.content_type.model,
            permission.content_type.name.lower(),
        )
        model_permissions = application["models"].setdefault(model_name, [])
        model_permissions.append(permission)

    return [
        {
            "name": application["name"],
            "models": [
                {
                    "name": model_name,
                    "categories": group_permissions_by_action(model_permissions),
                }
                for model_name, model_permissions in application["models"].items()
            ],
        }
        for application in applications.values()
    ]


def search_permissions(permissions, query):
    query = query.strip().casefold()
    if not query:
        return list(permissions)

    matches = []
    for permission in permissions:
        description = describe_permission(permission)
        app_label = permission.content_type.app_label
        model_label = MODEL_LABELS.get(
            permission.content_type.model,
            permission.content_type.name.lower(),
        )
        searchable_values = (
            permission.name,
            permission.codename,
            f"{app_label}.{permission.codename}",
            app_label,
            APP_LABELS.get(app_label, app_label.replace("_", " ").title()),
            permission.content_type.model,
            permission.content_type.name,
            model_label,
            description["label"],
            description["category"],
            description["description"],
        )
        if any(query in value.casefold() for value in searchable_values):
            matches.append(permission)
    return matches


class PermisoLimpioField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return describe_permission(obj)["label"]


# FORMULARIO DE REGISTRO DE USUARIOS
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta:
        model = User
        fields = ['username', 'email']


# FORMULARIO DE ROLES
class RolForm(forms.ModelForm):
    permissions = PermisoLimpioField(
        queryset=Permission.objects.select_related("content_type").all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permisos del rol",
    )
    permission_categories = ()

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': 'Nombre del Rol',
        }

    def __init__(self, *args, allow_permissions=True, **kwargs):
        super().__init__(*args, **kwargs)
        if allow_permissions:
            self.permission_categories = group_permissions_by_action(
                self.fields["permissions"].queryset
            )
            self.selected_permissions = {
                str(permission_id)
                for permission_id in self["permissions"].value() or []
            }
        else:
            self.fields.pop("permissions")
            self.permission_categories = ()
            self.selected_permissions = set()


# FORMULARIO DE ASIGNACIÓN DE ROLES
class AsignarRolUsuarioForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Seleccionar los roles "
    )

    class Meta:
        model = User
        fields = ['groups']


class AsignarPermisosUsuarioForm(forms.ModelForm):
    user_permissions = PermisoLimpioField(
        queryset=Permission.objects.select_related("content_type").all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permisos individuales de este usuario",
    )
    permission_categories = ()

    class Meta:
        model = User
        fields = ["user_permissions"]

    def __init__(self, *args, allow_changes=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not allow_changes:
            self.fields["user_permissions"].disabled = True
        self.permission_categories = group_permissions_by_action(
            self.fields["user_permissions"].queryset
        )
        self.selected_permissions = {
            str(permission_id)
            for permission_id in self["user_permissions"].value() or []
        }
