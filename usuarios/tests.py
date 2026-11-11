from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase

from .forms import (
    group_permissions_by_app_model_action,
    search_permissions,
)
from .models import EvaluacionAccesibilidad, PerfilUsuario
from .permissions import get_management_sections, has_management_access
from .views import es_administrador


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
        self.assertContains(response, ">Perfiles</a>")
        self.assertNotContains(response, ">Roles</a>")
        self.assertNotContains(response, ">Usuarios</a>")

    def test_player_sees_game_navigation_without_administration_links(self):
        user = get_user_model().objects.create_user(
            username="navigation-player",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get("/gestion/jugador/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-label="Navegación principal"')
        self.assertContains(response, 'href="/gestion/jugador/"')
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, "Cerrar sesión")
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertNotContains(response, ">Panel</a>")
        self.assertNotContains(response, ">Usuarios</a>")
        self.assertNotContains(response, ">Roles</a>")

        logout_response = self.client.post("/gestion/logout/")
        self.assertEqual(logout_response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_navigation_includes_game_and_current_section(self):
        admin = get_user_model().objects.create_user(
            username="navigation-admin",
            password="test-password",
            is_staff=True,
        )
        PerfilUsuario.objects.create(usuario=admin)
        self.client.force_login(admin)

        response = self.client.get("/gestion/perfiles/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">Panel</a>")
        self.assertContains(response, ">Juego y perfil</a>")
        self.assertContains(response, 'href="/gestion/perfiles/"')
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, ">Usuarios</a>")
        self.assertContains(response, ">Roles</a>")

    def test_authenticated_user_without_permission_is_denied_direct_list_url(self):
        user = get_user_model().objects.create_user(
            username="no-permissions",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get("/gestion/perfiles/")

        self.assertEqual(response.status_code, 403)

    def test_shared_navigation_supports_keyboard_and_mobile(self):
        user = get_user_model().objects.create_user(
            username="accessible-navigation-player",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get("/gestion/jugador/")

        self.assertContains(response, 'href="#main-content"')
        self.assertContains(response, "Saltar al contenido principal")
        self.assertContains(response, 'href="/static/usuarios/app_navigation.css"')
        stylesheet = (
            Path(__file__).parent / "static" / "usuarios" / "app_navigation.css"
        ).read_text()
        self.assertIn(":focus-visible", stylesheet)
        self.assertIn("@media (max-width: 700px)", stylesheet)

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
        self.assertContains(response, "Aplicación: Usuarios")
        self.assertContains(response, "Modelo: perfil de usuario")
        self.assertContains(response, "usuarios.view_perfilusuario")

    def test_permission_catalog_searches_label_codename_and_application(self):
        admin = get_user_model().objects.create_user(
            username="permission-search-admin",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(admin)

        by_label = self.client.get(
            "/gestion/permisos/",
            {"q": "Ver perfil de usuario"},
        )
        self.assertEqual(by_label.status_code, 200)
        self.assertContains(by_label, "usuarios.view_perfilusuario")
        self.assertNotContains(by_label, "auth.view_user")

        by_codename = self.client.get(
            "/gestion/permisos/",
            {"q": "usuarios.add_perfilusuario"},
        )
        self.assertContains(by_codename, "usuarios.add_perfilusuario")
        self.assertNotContains(by_codename, "usuarios.view_perfilusuario")

        rejected_post = self.client.post(
            "/gestion/permisos/",
            {"name": "permiso-inconsistente"},
        )
        self.assertEqual(rejected_post.status_code, 405)

        by_application = self.client.get(
            "/gestion/permisos/",
            {"q": "Autenticación y autorización"},
        )
        self.assertContains(by_application, "auth.view_user")
        self.assertNotContains(by_application, "usuarios.view_perfilusuario")

    def test_permission_catalog_helpers_group_by_application_model_and_action(self):
        permissions = Permission.objects.filter(
            content_type__app_label="usuarios",
            content_type__model="perfilusuario",
        ).select_related("content_type")

        grouped = group_permissions_by_app_model_action(permissions)

        self.assertEqual(len(grouped), 1)
        self.assertEqual(grouped[0]["name"], "Usuarios")
        self.assertEqual(grouped[0]["models"][0]["name"], "perfil de usuario")
        self.assertEqual(
            [category["name"] for category in grouped[0]["models"][0]["categories"]],
            ["Ver", "Crear", "Editar", "Eliminar", "Especiales"],
        )
        self.assertEqual(
            len(search_permissions(permissions, "Ver perfil de usuario")),
            1,
        )

    def test_view_user_permission_can_read_but_not_change_individual_permissions(self):
        reader = get_user_model().objects.create_user(
            username="individual-permission-reader",
            password="test-password",
        )
        role = Group.objects.create(name="individual-permission-reader-role")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="auth",
                codename="view_user",
            )
        )
        reader.groups.add(role)
        target = get_user_model().objects.create_user(username="permission-target")
        current_permission = Permission.objects.get(
            content_type__app_label="usuarios",
            codename="view_perfilusuario",
        )
        submitted_permission = Permission.objects.get(
            content_type__app_label="auth",
            codename="view_group",
        )
        target.user_permissions.add(current_permission)
        self.client.force_login(reader)

        page = self.client.get(
            f"/gestion/usuarios/{target.pk}/permisos/"
        )
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "solo lectura")
        self.assertContains(page, "disabled")
        self.assertNotContains(page, "Guardar permisos individuales")

        denied = self.client.post(
            f"/gestion/usuarios/{target.pk}/permisos/",
            {"user_permissions": [submitted_permission.pk]},
        )
        self.assertEqual(denied.status_code, 403)
        target.refresh_from_db()
        self.assertQuerySetEqual(
            target.user_permissions.all(),
            [current_permission],
        )

    def test_change_user_permission_can_assign_individual_permissions(self):
        editor = get_user_model().objects.create_user(
            username="individual-permission-editor",
            password="test-password",
        )
        role = Group.objects.create(name="individual-permission-editor-role")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="auth",
                codename="change_user",
            )
        )
        editor.groups.add(role)
        target = get_user_model().objects.create_user(username="permission-edit-target")
        permission = Permission.objects.get(
            content_type__app_label="usuarios",
            codename="view_perfilusuario",
        )
        self.client.force_login(editor)

        response = self.client.post(
            f"/gestion/usuarios/{target.pk}/permisos/",
            {"user_permissions": [permission.pk]},
        )

        self.assertRedirects(
            response,
            "/gestion/usuarios/",
            fetch_redirect_response=False,
        )
        target.refresh_from_db()
        self.assertQuerySetEqual(target.user_permissions.all(), [permission])

    def test_inactive_accounts_never_get_management_access(self):
        inactive_staff = get_user_model().objects.create_user(
            username="inactive-staff",
            is_staff=True,
            is_active=False,
        )
        inactive_superuser = get_user_model().objects.create_superuser(
            username="inactive-superuser",
            email="inactive-superuser@example.com",
            password="test-password",
            is_active=False,
        )
        inactive_reader = get_user_model().objects.create_user(
            username="inactive-reader",
            is_active=False,
        )
        reader_group = Group.objects.create(name="inactive-reader-role")
        reader_group.permissions.add(
            Permission.objects.get(
                content_type__app_label="usuarios",
                codename="view_perfilusuario",
            )
        )
        inactive_reader.groups.add(reader_group)

        for user in (inactive_staff, inactive_superuser, inactive_reader):
            with self.subTest(username=user.username):
                self.assertFalse(es_administrador(user))
                self.assertFalse(has_management_access(user))
                self.assertEqual(get_management_sections(user), [])
                self.client.force_login(user)
                response = self.client.get("/gestion/perfiles/")
                self.assertIn(response.status_code, (302, 403))

        target = get_user_model().objects.create_user(username="role-target")
        self.client.force_login(inactive_staff)
        response = self.client.post(
            f"/gestion/usuarios/{target.pk}/roles/",
            {"groups": [reader_group.pk]},
        )
        self.assertIn(response.status_code, (302, 403))
        target.refresh_from_db()
        self.assertFalse(target.groups.exists())

    def test_no_permission_user_cannot_use_management_urls_or_post_actions(self):
        owner = get_user_model().objects.create_user(username="crud-owner")
        profile = PerfilUsuario.objects.create(usuario=owner)
        evaluation = EvaluacionAccesibilidad.objects.create(
            usuario=owner,
            color_fondo_hex="#FFFFFF",
            color_texto_hex="#000000",
            ratio_contraste="21.00",
        )
        role = Group.objects.create(name="protected-role")
        target = get_user_model().objects.create_user(username="protected-user")
        user = get_user_model().objects.create_user(username="no-management-access")
        self.client.force_login(user)

        paths = (
            "/gestion/permisos/",
            "/gestion/roles/",
            f"/gestion/roles/{role.pk}/editar/",
            f"/gestion/roles/{role.pk}/eliminar/",
            "/gestion/usuarios/",
            f"/gestion/usuarios/{target.pk}/roles/",
            f"/gestion/usuarios/{target.pk}/permisos/",
            "/gestion/perfiles/",
            "/gestion/perfiles/nuevo/",
            f"/gestion/perfiles/{profile.pk}/editar/",
            f"/gestion/perfiles/{profile.pk}/eliminar/",
            "/gestion/evaluaciones/",
            "/gestion/evaluaciones/nueva/",
            f"/gestion/evaluaciones/{evaluation.pk}/editar/",
            f"/gestion/evaluaciones/{evaluation.pk}/eliminar/",
            "/gestion/crear/",
            f"/gestion/editar/{target.pk}/",
            f"/gestion/eliminar/{target.pk}/",
        )
        for path in paths:
            with self.subTest(method="GET", path=path):
                response = self.client.get(path)
                self.assertIn(response.status_code, (302, 403))
            with self.subTest(method="POST", path=path):
                response = self.client.post(path, {})
                self.assertIn(response.status_code, (302, 403))

    def test_group_and_individual_permissions_combine_for_real_actions(self):
        user = get_user_model().objects.create_user(username="mixed-permissions")
        reader_group = Group.objects.create(name="mixed-permissions-reader")
        reader_group.permissions.add(
            Permission.objects.get(
                content_type__app_label="usuarios",
                codename="view_perfilusuario",
            )
        )
        user.groups.add(reader_group)
        user.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="usuarios",
                codename="add_perfilusuario",
            )
        )
        self.client.force_login(user)

        listing = self.client.get("/gestion/perfiles/")
        create_form = self.client.get("/gestion/perfiles/nuevo/")

        self.assertEqual(listing.status_code, 200)
        self.assertEqual(create_form.status_code, 200)
        self.assertContains(listing, 'href="/gestion/perfiles/nuevo/"')


class UserManagementTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username="user-management-admin",
            is_staff=True,
        )
        self.client.force_login(self.admin)

    def test_user_listing_search_and_combined_filters(self):
        selected_role = Group.objects.create(name="selected-role")
        other_role = Group.objects.create(name="other-role")
        selected = get_user_model().objects.create_user(
            username="matching-user",
            email="matching@example.com",
            is_active=False,
        )
        selected.groups.add(selected_role)
        active_match = get_user_model().objects.create_user(
            username="matching-active",
            email="active@example.com",
        )
        active_match.groups.add(selected_role)
        different_role = get_user_model().objects.create_user(
            username="matching-other-role",
            email="other@example.com",
            is_active=False,
        )
        different_role.groups.add(other_role)
        email_match = get_user_model().objects.create_user(
            username="another-name",
            email="lookup@example.com",
            is_active=False,
        )

        response = self.client.get(
            "/gestion/usuarios/",
            {"q": "matching", "estado": "inactivo", "rol": selected_role.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, selected.username)
        self.assertNotContains(response, active_match.username)
        self.assertNotContains(response, different_role.username)
        self.assertContains(response, 'name="q"')
        self.assertContains(response, 'value="matching"')
        self.assertContains(response, 'name="rol"')
        self.assertContains(response, 'name="estado"')
        self.assertContains(response, 'value="inactivo" selected')

        response = self.client.get("/gestion/usuarios/", {"q": "lookup@"})
        self.assertContains(response, email_match.username)
        self.assertContains(response, email_match.email)
        self.assertNotContains(response, selected.username)

    def test_user_listing_paginates_twenty_and_preserves_filters(self):
        for index in range(21):
            get_user_model().objects.create_user(
                username=f"team-member-{index:02}",
                is_active=True,
            )

        response = self.client.get(
            "/gestion/usuarios/",
            {"q": "team-member", "estado": "activo"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_results"], 21)
        self.assertEqual(len(response.context["usuarios"]), 20)
        self.assertContains(
            response,
            "?q=team-member&amp;estado=activo&amp;page=2",
        )

        response = self.client.get(
            "/gestion/usuarios/",
            {"q": "team-member", "estado": "activo", "page": 2},
        )
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["usuarios"]), 1)

    def test_user_listing_empty_results_renders_without_user_actions(self):
        response = self.client.get(
            "/gestion/usuarios/",
            {"q": "no-such-user-or-email"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay usuarios que coincidan con los filtros.")

    def test_user_actions_are_styled_as_separate_buttons(self):
        user = get_user_model().objects.create_user(
            username="action-button-user",
            email="action-buttons@example.com",
        )

        response = self.client.get("/gestion/usuarios/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'class="user-actions" aria-label="Acciones para {self.admin.username}"',
        )
        self.assertContains(response, "user-action--primary")
        self.assertContains(response, "user-action--security")
        self.assertContains(response, "user-action--danger")
        self.assertContains(response, "Cambiar contraseña")
        self.assertContains(response, "Asignar roles")

    def test_user_list_shows_account_metadata_without_password_data(self):
        user = get_user_model().objects.create_user(
            username="visible-account",
            email="visible@example.com",
            password="NeverDisplay-Password-381!",
        )

        response = self.client.get("/gestion/usuarios/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.email)
        self.assertContains(response, "Fecha de alta")
        self.assertContains(response, "Activo")
        self.assertNotContains(response, "NeverDisplay-Password-381!")
        self.assertNotContains(response, user.password)

    def test_create_and_edit_user_use_safe_password_handling(self):
        response = self.client.post(
            "/gestion/crear/",
            {
                "username": "created-account",
                "email": "created@example.com",
                "password1": "Strong-Created-Password-481!",
                "password2": "Strong-Created-Password-481!",
            },
        )

        self.assertRedirects(response, "/gestion/usuarios/")
        created = get_user_model().objects.get(username="created-account")
        self.assertEqual(created.email, "created@example.com")
        self.assertTrue(created.check_password("Strong-Created-Password-481!"))
        self.assertNotEqual(created.password, "Strong-Created-Password-481!")

        response = self.client.post(
            f"/gestion/editar/{created.pk}/",
            {"username": "renamed-account", "email": "renamed@example.com"},
        )
        self.assertRedirects(response, "/gestion/usuarios/")
        created.refresh_from_db()
        self.assertEqual(created.username, "renamed-account")
        self.assertEqual(created.email, "renamed@example.com")
        self.assertTrue(created.check_password("Strong-Created-Password-481!"))

    def test_set_password_form_changes_password_without_exposing_old_password(self):
        target = get_user_model().objects.create_user(
            username="password-target",
            password="Previous-Password-471!",
        )
        response = self.client.get(
            f"/gestion/usuarios/{target.pk}/contrasena/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "new_password1")
        self.assertNotContains(response, "old_password")
        self.assertNotContains(response, target.password)
        self.assertNotContains(response, "Previous-Password-471!")

        response = self.client.post(
            f"/gestion/usuarios/{target.pk}/contrasena/",
            {
                "new_password1": "New-Strong-Password-563!",
                "new_password2": "New-Strong-Password-563!",
            },
        )

        self.assertRedirects(response, "/gestion/usuarios/")
        target.refresh_from_db()
        self.assertTrue(target.check_password("New-Strong-Password-563!"))
        self.assertFalse(target.check_password("Previous-Password-471!"))

    def test_account_activation_requires_confirmation_and_post(self):
        target = get_user_model().objects.create_user(
            username="account-to-deactivate",
        )

        confirmation = self.client.get(
            f"/gestion/usuarios/{target.pk}/estado/desactivar/"
        )
        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, "csrfmiddlewaretoken")
        target.refresh_from_db()
        self.assertTrue(target.is_active)

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.admin)
        response = csrf_client.post(
            f"/gestion/usuarios/{target.pk}/estado/desactivar/"
        )
        self.assertEqual(response.status_code, 403)
        target.refresh_from_db()
        self.assertTrue(target.is_active)

        response = self.client.post(
            f"/gestion/usuarios/{target.pk}/estado/desactivar/"
        )
        self.assertRedirects(response, "/gestion/usuarios/")
        target.refresh_from_db()
        self.assertFalse(target.is_active)

        response = self.client.post(
            f"/gestion/usuarios/{target.pk}/estado/activar/"
        )
        self.assertRedirects(response, "/gestion/usuarios/")
        target.refresh_from_db()
        self.assertTrue(target.is_active)

    def test_delete_requires_confirmation_and_post(self):
        target = get_user_model().objects.create_user(
            username="account-to-delete",
        )

        confirmation = self.client.get(f"/gestion/eliminar/{target.pk}/")
        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, target.username)
        self.assertContains(confirmation, "progresos y logros")
        target.refresh_from_db()

        response = self.client.post(f"/gestion/eliminar/{target.pk}/")
        self.assertRedirects(response, "/gestion/usuarios/")
        self.assertFalse(get_user_model().objects.filter(pk=target.pk).exists())

    def test_read_only_user_cannot_edit_delete_or_change_account_state(self):
        reader = get_user_model().objects.create_user(username="user-list-reader")
        reader_group = Group.objects.create(name="user-list-reader-role")
        reader_group.permissions.add(
            Permission.objects.get(
                content_type__app_label="auth",
                codename="view_user",
            )
        )
        reader.groups.add(reader_group)
        target = get_user_model().objects.create_user(username="protected-account")
        self.client.force_login(reader)

        listing = self.client.get("/gestion/usuarios/")
        self.assertEqual(listing.status_code, 200)
        self.assertContains(listing, target.username)
        self.assertNotContains(listing, "Cambiar contraseña")
        self.assertNotContains(listing, "Desactivar")
        self.assertNotContains(listing, "Eliminar")

        denied_paths = (
            f"/gestion/editar/{target.pk}/",
            f"/gestion/eliminar/{target.pk}/",
            f"/gestion/usuarios/{target.pk}/estado/desactivar/",
            f"/gestion/usuarios/{target.pk}/contrasena/",
        )
        for path in denied_paths:
            with self.subTest(path=path, method="GET"):
                response = self.client.get(path)
                self.assertIn(response.status_code, (302, 403))
            with self.subTest(path=path, method="POST"):
                response = self.client.post(path, {})
                self.assertIn(response.status_code, (302, 403))

        target.refresh_from_db()
        self.assertTrue(target.is_active)


class RoleManagementCrudTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username="role-crud-admin",
            is_staff=True,
        )
        self.client.force_login(self.admin)
        self.profile_view = Permission.objects.get(
            content_type__app_label="usuarios",
            codename="view_perfilusuario",
        )
        self.profile_add = Permission.objects.get(
            content_type__app_label="usuarios",
            codename="add_perfilusuario",
        )

    def test_role_search_counts_assigned_users_and_groups_permissions(self):
        role = Group.objects.create(name="color-reviewers")
        role.permissions.add(self.profile_view, self.profile_add)
        member = get_user_model().objects.create_user(username="role-member")
        member.groups.add(role)
        get_user_model().objects.create_user(username="unrelated-member")
        self.client.force_login(
            get_user_model().objects.create_user(
                username="role-reader",
                is_staff=True,
            )
        )

        response = self.client.get("/gestion/roles/", {"q": "color"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, role.name)
        self.assertContains(response, "Usuarios asignados")
        self.assertContains(response, "Ver perfil de usuario")
        self.assertContains(response, "usuarios")
        self.assertContains(response, 'name="q"')
        self.assertContains(response, 'value="color"')
        self.assertEqual(response.context["roles"].count(), 1)
        self.assertEqual(response.context["roles"][0].user_count, 1)
        self.assertNotContains(response, "unrelated-member")

    def test_role_list_paginates_twenty_and_preserves_search(self):
        for index in range(21):
            Group.objects.create(name=f"palette-role-{index:02}")

        response = self.client.get("/gestion/roles/", {"q": "palette-role"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_results"], 21)
        self.assertEqual(len(response.context["roles"]), 20)
        self.assertContains(
            response,
            "?q=palette-role&amp;page=2",
        )

        response = self.client.get(
            "/gestion/roles/",
            {"q": "palette-role", "page": 2},
        )
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["roles"]), 1)

    def test_create_and_edit_role_persist_and_preselect_permissions(self):
        Group.objects.create(name="taken-role")
        response = self.client.post(
            "/gestion/roles/",
            {
                "name": "taken-role",
                "permissions": [self.profile_view.pk],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{self.profile_view.pk}"')
        self.assertContains(response, "checked")

        response = self.client.post(
            "/gestion/roles/",
            {
                "name": "palette-reviewers",
                "permissions": [self.profile_view.pk],
            },
        )
        self.assertRedirects(response, "/gestion/roles/")
        role = Group.objects.get(name="palette-reviewers")
        self.assertQuerySetEqual(role.permissions.all(), [self.profile_view])

        edit_page = self.client.get(f"/gestion/roles/{role.pk}/editar/")
        self.assertEqual(edit_page.status_code, 200)
        self.assertContains(
            edit_page,
            f'value="{self.profile_view.pk}"',
        )
        self.assertContains(edit_page, "checked")

        response = self.client.post(
            f"/gestion/roles/{role.pk}/editar/",
            {
                "name": "taken-role",
                "permissions": [self.profile_view.pk, self.profile_add.pk],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{self.profile_view.pk}"')
        self.assertContains(response, "checked")

        response = self.client.post(
            f"/gestion/roles/{role.pk}/editar/",
            {
                "name": "palette-editors",
                "permissions": [self.profile_add.pk],
            },
        )
        self.assertRedirects(response, "/gestion/roles/")
        role.refresh_from_db()
        self.assertEqual(role.name, "palette-editors")
        self.assertQuerySetEqual(role.permissions.all(), [self.profile_add])

    def test_role_permission_grants_access_to_protected_profile_list(self):
        response = self.client.post(
            "/gestion/roles/",
            {
                "name": "profile-list-readers",
                "permissions": [self.profile_view.pk],
            },
        )
        self.assertRedirects(response, "/gestion/roles/")
        role = Group.objects.get(name="profile-list-readers")
        member = get_user_model().objects.create_user(
            username="profile-list-reader-member",
        )
        member.groups.add(role)
        self.client.force_login(member)

        listing = self.client.get("/gestion/perfiles/")

        self.assertEqual(listing.status_code, 200)

    def test_assign_and_remove_multiple_roles_updates_effective_permissions(self):
        user = get_user_model().objects.create_user(username="role-assignment-target")
        first_role = Group.objects.create(name="profile-reader-role")
        first_role.permissions.add(self.profile_view)
        second_role = Group.objects.create(name="profile-creator-role")
        second_role.permissions.add(self.profile_add)

        response = self.client.post(
            f"/gestion/usuarios/{user.pk}/roles/",
            {"groups": [first_role.pk, second_role.pk]},
        )
        self.assertRedirects(response, "/gestion/usuarios/")
        user = get_user_model().objects.get(pk=user.pk)
        self.assertTrue(user.has_perm("usuarios.view_perfilusuario"))
        self.assertTrue(user.has_perm("usuarios.add_perfilusuario"))

        response = self.client.post(
            f"/gestion/usuarios/{user.pk}/roles/",
            {"groups": [second_role.pk]},
        )
        self.assertRedirects(response, "/gestion/usuarios/")
        user = get_user_model().objects.get(pk=user.pk)
        self.assertFalse(user.has_perm("usuarios.view_perfilusuario"))
        self.assertTrue(user.has_perm("usuarios.add_perfilusuario"))
        self.assertQuerySetEqual(user.groups.all(), [second_role])

    def test_role_operations_are_separately_protected(self):
        role = Group.objects.create(name="protected-role")
        reader = get_user_model().objects.create_user(username="role-only-reader")
        read_role = Group.objects.create(name="role-read-only")
        read_role.permissions.add(
            Permission.objects.get(
                content_type__app_label="auth",
                codename="view_group",
            )
        )
        reader.groups.add(read_role)
        self.client.force_login(reader)

        listing = self.client.get("/gestion/roles/")
        self.assertEqual(listing.status_code, 200)
        self.assertContains(listing, role.name)
        self.assertNotContains(listing, "Crear rol")
        self.assertNotContains(listing, "Editar")
        self.assertNotContains(listing, "Eliminar")
        for path, method in (
            ("/gestion/roles/", "post"),
            (f"/gestion/roles/{role.pk}/editar/", "get"),
            (f"/gestion/roles/{role.pk}/editar/", "post"),
            (f"/gestion/roles/{role.pk}/eliminar/", "get"),
            (f"/gestion/roles/{role.pk}/eliminar/", "post"),
            (f"/gestion/usuarios/{reader.pk}/roles/", "get"),
            (f"/gestion/usuarios/{reader.pk}/roles/", "post"),
        ):
            with self.subTest(path=path, method=method):
                response = getattr(self.client, method)(path, {})
                self.assertIn(response.status_code, (302, 403))

    def test_role_deletion_requires_confirmation_and_preserves_user(self):
        role = Group.objects.create(name="removable-role")
        user = get_user_model().objects.create_user(username="role-member-account")
        user.groups.add(role)

        confirmation = self.client.get(f"/gestion/roles/{role.pk}/eliminar/")
        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, "Las cuentas de")
        self.assertContains(confirmation, "no se eliminarán")
        role.refresh_from_db()
        user.refresh_from_db()

        response = self.client.post(f"/gestion/roles/{role.pk}/eliminar/")
        self.assertRedirects(response, "/gestion/roles/")
        self.assertFalse(Group.objects.filter(pk=role.pk).exists())
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())
        user.refresh_from_db()
        self.assertFalse(user.groups.exists())
