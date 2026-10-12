from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group, Permission

# --- FORMULARIO DE REGISTRO DE USUARIOS ---
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta:
        model = User
        fields = ['username', 'email']


# --- FORMULARIO DE PERMISOS ---
class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'content_type']
        labels = {
            'name': 'Nombre Descriptivo',
            'codename': 'Código del Permiso',
            'content_type': 'Modelo Asociado',
        }


# --- FORMULARIO DE ROLES ---
class RolForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Permisos asignados a este rol"
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        labels = {
            'name': 'Nombre del Rol',
        }


# --- FORMULARIO DE ASIGNACIÓN DE ROLES ---
class AsignarRolUsuarioForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Roles del Usuario"
    )

    class Meta:
        model = User
        fields = ['groups']