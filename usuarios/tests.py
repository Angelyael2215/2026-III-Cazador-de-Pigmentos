from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase

from .models import PerfilUsuario


class ProfilePermissionTests(TestCase):
    def setUp(self):
        self.profile = PerfilUsuario.objects.create(
            usuario=get_user_model().objects.create_user(
                username="profile-owner",
                password="test-password",
            )
        )

    def test_view_permission_shows_only_the_profile_list(self):
        user = get_user_model().objects.create_user(
            username="profile-reader",
            password="test-password",
        )
        role = Group.objects.create(name="profile-reader")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="usuarios",
                codename="view_perfilusuario",
            )
        )
        user.groups.add(role)
        PerfilUsuario.objects.create(usuario=user)
        self.client.force_login(user)

        response = self.client.get("/gestion/perfiles/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile-reader")
        self.assertNotContains(response, "href=\"/gestion/perfiles/nuevo/\"")

    def test_login_sends_permission_user_to_available_views(self):
        user = get_user_model().objects.create_user(
            username="profile-login-reader",
            password="test-password",
        )
        role = Group.objects.create(name="profile-login-reader")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="usuarios",
                codename="view_perfilusuario",
            )
        )
        user.groups.add(role)

        response = self.client.post(
            "/gestion/login/",
            {"username": user.username, "password": "test-password"},
        )

        self.assertRedirects(response, "/gestion/")

    def test_add_permission_shows_create_button(self):
        user = get_user_model().objects.create_user(
            username="profile-creator",
            password="test-password",
        )
        role = Group.objects.create(name="profile-creator")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="usuarios",
                codename="view_perfilusuario",
            ),
            Permission.objects.get(
                content_type__app_label="usuarios",
                codename="add_perfilusuario",
            ),
        )
        user.groups.add(role)
        self.client.force_login(user)

        response = self.client.get("/gestion/perfiles/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "href=\"/gestion/perfiles/nuevo/\"")

    def test_view_user_permission_is_read_only(self):
        user = get_user_model().objects.create_user(
            username="user-reader",
            password="test-password",
        )
        role = Group.objects.create(name="user-reader")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="auth",
                codename="view_user",
            )
        )
        user.groups.add(role)
        self.client.force_login(user)

        response = self.client.get("/gestion/usuarios/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile-owner")
        self.assertNotContains(response, "Asignar Roles")
        self.assertNotContains(response, "Nuevo Usuario")

    def test_view_group_permission_hides_create_and_edit_actions(self):
        role_reader = Group.objects.create(name="role-reader")
        role = Group.objects.create(name="visible-role")
        role_reader.permissions.add(
            Permission.objects.get(
                content_type__app_label="auth",
                codename="view_group",
            )
        )
        user = get_user_model().objects.create_user(
            username="role-reader",
            password="test-password",
        )
        user.groups.add(role_reader)
        self.client.force_login(user)

        response = self.client.get("/gestion/roles/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, role.name)
        self.assertNotContains(response, "Crear Rol")
        self.assertNotContains(response, "Editar Permisos")

        denied = self.client.post("/gestion/roles/", {"name": "new-role"})
        self.assertEqual(denied.status_code, 403)

    def test_add_group_cannot_assign_permissions_without_change_group(self):
        user = get_user_model().objects.create_user(
            username="group-creator",
            password="test-password",
        )
        creator_role = Group.objects.create(name="group-creator-role")
        creator_role.permissions.add(
            Permission.objects.get(
                content_type__app_label="auth",
                codename="add_group",
            )
        )
        user.groups.add(creator_role)
        protected_permission = Permission.objects.get(
            content_type__app_label="usuarios",
            codename="delete_perfilusuario",
        )
        self.client.force_login(user)

        response = self.client.post(
            "/gestion/roles/",
            {
                "name": "new-limited-role",
                "permissions": [protected_permission.pk],
            },
        )

        self.assertRedirects(response, "/gestion/roles/")
        new_role = Group.objects.get(name="new-limited-role")
        self.assertFalse(new_role.permissions.filter(pk=protected_permission.pk).exists())

    def test_role_management_page_renders_delete_action(self):
        admin = get_user_model().objects.create_user(
            username="role-admin",
            password="test-password",
            is_staff=True,
        )
        Group.objects.create(name="existing-role")
        self.client.force_login(admin)

        response = self.client.get("/gestion/roles/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "eliminar")
        self.assertContains(response, "Crear")
        self.assertContains(response, "Ver")

    def test_individual_permissions_do_not_change_user_roles(self):
        admin = get_user_model().objects.create_user(
            username="permissions-admin",
            password="test-password",
            is_staff=True,
        )
        user = get_user_model().objects.create_user(
            username="individual-reader",
            password="test-password",
        )
        role = Group.objects.create(name="shared-read-only")
        group_permission = Permission.objects.get(
            content_type__app_label="usuarios",
            codename="view_perfilusuario",
        )
        individual_permission = Permission.objects.get(
            content_type__app_label="auth",
            codename="view_user",
        )
        role.permissions.add(group_permission)
        user.groups.add(role)
        self.client.force_login(admin)

        response = self.client.get(
            f"/gestion/usuarios/{user.pk}/permisos/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear")
        self.assertContains(response, "Código:")

        response = self.client.post(
            f"/gestion/usuarios/{user.pk}/permisos/",
            {"user_permissions": [individual_permission.pk]},
        )
        self.assertRedirects(response, "/gestion/usuarios/")

        user.refresh_from_db()
        self.assertQuerySetEqual(user.groups.all(), [role])
        self.assertQuerySetEqual(
            user.user_permissions.all(),
            [individual_permission],
        )
        self.assertTrue(user.has_perm("usuarios.view_perfilusuario"))
        self.assertTrue(user.has_perm("auth.view_user"))

    def test_role_permissions_are_translated_and_action_grouped(self):
        admin = get_user_model().objects.create_user(
            username="permission-admin",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(admin)

        response = self.client.get("/gestion/permisos/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ver")
        self.assertContains(response, "Crear")
        self.assertContains(response, "Editar")
        self.assertContains(response, "Eliminar")
        self.assertContains(response, "Ver perfil de usuario")
