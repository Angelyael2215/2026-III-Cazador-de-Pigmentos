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


class PermisoLimpioField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return describe_permission(obj)["label"]


# FORMULARIO DE REGISTRO DE USUARIOS 
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta:
        model = User
        fields = ['username', 'email']


# FORMULARIO DE PERMISOS 
class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'content_type']
        labels = {
            'name': 'Nombre Descriptivo',
            'codename': 'Código del Permiso',
            'content_type': 'Modelo Asociado',
        }


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission_categories = group_permissions_by_action(
            self.fields["user_permissions"].queryset
        )
        self.selected_permissions = {
            str(permission_id)
            for permission_id in self["user_permissions"].value() or []
        }
