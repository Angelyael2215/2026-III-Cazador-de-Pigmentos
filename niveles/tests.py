import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from usuarios.models import PerfilUsuario

from .models import Level, LevelProgress, Player
from .services import validate_answer


class LevelAnswerValidationTests(SimpleTestCase):
    def test_mix_compares_colors_without_case_or_order_sensitivity(self):
        level = type("TestLevel", (), {
            "kind": "mix",
            "solution": {"colors": ["#112233", "#AABBCC"]},
        })()

        self.assertTrue(validate_answer(
            level,
            {"colors": ["#aabbcc", "#112233"]},
        ))

    def test_rgb_accepts_values_inside_tolerance(self):
        level = type("TestLevel", (), {
            "kind": "rgb",
            "solution": {"rgb": [100, 100, 100]},
        })()

        self.assertTrue(validate_answer(level, {"rgb": [120, 100, 100]}))
        self.assertFalse(validate_answer(level, {"rgb": [155, 100, 100]}))

    def test_temperature_uses_color_groups(self):
        level = type("TestLevel", (), {
            "kind": "temperature",
            "solution": {
                "warm": ["#FF0000"],
                "cold": ["#0000FF"],
            },
        })()

        self.assertTrue(validate_answer(
            level,
            {"warm": ["#ff0000"], "cold": ["#0000ff"]},
        ))

    def test_saturation_requires_the_exact_order(self):
        level = type("TestLevel", (), {
            "kind": "saturation",
            "solution": {"order": ["#111111", "#EEEEEE"]},
        })()

        self.assertFalse(validate_answer(
            level,
            {"order": ["#EEEEEE", "#111111"]},
        ))

    def test_invalid_color_format_is_rejected(self):
        level = type("TestLevel", (), {
            "kind": "mix",
            "solution": {"colors": ["#112233"]},
        })()

        with self.assertRaisesMessage(ValueError, "formato #RRGGBB"):
            validate_answer(level, {"colors": ["red"]})


class LevelsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Bearer valid-token")
        self.level = Level.objects.create(
            number=1,
            kind="branding",
            title="Color de marca",
            instruction="Elige el color correcto.",
            data={"options": [{"id": "a", "color": "#1E88E5"}]},
            solution={"option_id": "a"},
        )
        self.locked_level = Level.objects.create(
            number=2,
            kind="hex",
            title="Código HEX",
            instruction="Selecciona el código correcto.",
            data={"options": [{"id": "b", "color": "#E53935"}]},
            solution={"option_id": "b"},
        )

    def authenticated_request(self, method, url, **kwargs):
        with (
            patch("niveles.authentication.firebase_admin.get_app"),
            patch(
                "niveles.authentication.auth.verify_id_token",
                return_value={"uid": "firebase-player-1"},
            ),
        ):
            return getattr(self.client, method)(url, **kwargs)

    def test_level_list_excludes_solution_and_hides_inactive_levels(self):
        Level.objects.create(
            number=3,
            kind="mix",
            title="Inactivo",
            instruction="No debe mostrarse.",
            solution={"colors": ["#FFFFFF"]},
            active=False,
        )

        response = self.authenticated_request("get",         "/api/levels/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["current_level_reached"], 1)
        self.assertEqual(len(response.data["levels"]), 2)
        self.assertTrue(response.data["levels"][0]["unlocked"])
        self.assertNotIn("solution", response.data["levels"][0])

    def test_first_correct_answer_awards_rewards_and_unlocks_next_level(self):
        response = self.authenticated_request(
            "post",
            "/api/levels/1/submit/",
            data={"answer": {"option_id": "a"}},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["earned_xp"], 10)
        self.assertEqual(response.data["earned_pigments"], 1)
        self.assertEqual(response.data["current_level_reached"], 2)
        self.assertTrue(response.data["completed"])

        player = Player.objects.get(firebase_uid="firebase-player-1")
        self.assertEqual((player.xp, player.pigments), (10, 1))

        repeated = self.authenticated_request(
            "post",
            "/api/levels/1/submit/",
            data={"answer": {"option_id": "a"}},
            format="json",
        )
        self.assertEqual(repeated.status_code, 200)
        self.assertEqual(repeated.data["earned_xp"], 0)
        self.assertEqual(repeated.data["earned_pigments"], 0)
        self.assertEqual(repeated.data["attempts"], 2)
        self.assertEqual(LevelProgress.objects.get(player=player, level=self.level).attempts, 2)

    def test_cannot_submit_locked_level(self):
        response = self.authenticated_request(
            "post",
            "/api/levels/2/submit/",
            data={"answer": {"option_id": "b"}},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Player.objects.exists())

    def test_invalid_answer_returns_validation_error(self):
        response = self.authenticated_request(
            "post",
            "/api/levels/1/submit/",
            data={"answer": {"colors": ["red"]}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("answer", response.data)

    def test_request_without_token_is_rejected(self):
        self.client.credentials()

        response = self.client.get("/api/levels/")

        self.assertEqual(response.status_code, 401)

    def test_invalid_firebase_token_is_rejected(self):
        with (
            patch("niveles.authentication.firebase_admin.get_app"),
            patch(
                "niveles.authentication.auth.verify_id_token",
                side_effect=ValueError("invalid token"),
            ),
        ):
            response = self.client.get("/api/levels/")

        self.assertEqual(response.status_code, 401)


class PlayerGamePageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="color-player",
            password="test-password",
        )
        self.client.force_login(self.user)
        self.level = Level.objects.create(
            number=1,
            kind="branding",
            title="Color de marca",
            instruction="Elige el color correcto.",
            data={
                "options": [
                    {"id": "a", "color": "#1E88E5"},
                    {"id": "b", "color": "#E53935"},
                ]
            },
            solution={"option_id": "a"},
        )

    def test_profile_lists_playable_level(self):
        response = self.client.get("/gestion/jugador/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mis niveles")
        self.assertContains(response, "Color de marca")
        self.assertContains(response, "/gestion/niveles/jugar/1/")
        self.assertNotContains(response, "option_id")

    def test_game_page_shows_choices_but_not_solution(self):
        response = self.client.get("/gestion/niveles/jugar/1/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "#1E88E5")
        self.assertNotContains(response, '"solution"')
        self.assertNotContains(response, ">Panel</a>")

    def test_staff_user_can_return_to_management_from_game(self):
        admin = get_user_model().objects.create_user(
            username="game-page-admin",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(admin)

        response = self.client.get("/gestion/niveles/jugar/1/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, ">Panel</a>")
        self.assertContains(response, "/gestion/")

    def test_palette_options_and_legacy_answer_key_work_for_level_three(self):
        level = Level.objects.create(
            number=3,
            kind="branding",
            title="Nivel 3",
            instruction="Escoge la opción correcta.",
            data={
                "brand_name": "TechCorp",
                "logo_placeholder": "logo_1.png",
                "palette_options": [
                    {"id": "a", "colors": ["#0000FF", "#00FFFF"]},
                    {"id": "b", "colors": ["#FF0000", "#FFFF00"]},
                ],
            },
            solution={"correct_option_id": "a"},
        )
        player, _ = Player.objects.get_or_create(user=self.user)
        player.current_level_reached = level.number
        player.save()

        response = self.client.get(f"/gestion/niveles/jugar/{level.number}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TechCorp")
        self.assertContains(response, "Paleta A")
        self.assertContains(response, "#0000FF")
        self.assertContains(response, "#00FFFF")
        self.assertNotContains(response, "correct_option_id")

        response = self.client.post(
            f"/gestion/niveles/jugar/{level.number}/",
            {"answer": json.dumps({"option_id": "a"})},
        )
        self.assertRedirects(response, f"/gestion/niveles/jugar/{level.number}/")
        player.refresh_from_db()
        self.assertEqual(player.current_level_reached, 4)

    def test_correct_answer_updates_player_and_profile(self):
        response = self.client.post(
            "/gestion/niveles/jugar/1/",
            {"answer": json.dumps({"option_id": "a"})},
        )

        self.assertRedirects(response, "/gestion/niveles/jugar/1/")
        player = Player.objects.get(user=self.user)
        profile = PerfilUsuario.objects.get(usuario=self.user)
        progress = LevelProgress.objects.get(player=player, level=self.level)
        self.assertEqual((player.xp, player.pigments), (10, 1))
        self.assertEqual((profile.gemas, profile.nivel_maximo_desbloqueado), (1, 2))
        self.assertTrue(progress.completed)
        self.assertEqual(progress.attempts, 1)

    def test_player_cannot_open_locked_level(self):
        locked_level = Level.objects.create(
            number=2,
            kind="branding",
            title="Nivel bloqueado",
            instruction="Completa el anterior.",
            data={"options": [{"id": "a", "color": "#FFFFFF"}]},
            solution={"option_id": "a"},
        )

        response = self.client.get(f"/gestion/niveles/jugar/{locked_level.number}/")

        self.assertEqual(response.status_code, 403)


class LevelManagementPanelTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username="game-admin",
            password="test-password",
            is_staff=True,
        )
        self.client.force_login(self.admin)

    def test_dashboard_links_to_custom_level_management(self):
        response = self.client.get("/gestion/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Niveles del juego")
        self.assertContains(response, "/gestion/niveles/juego/")

    def test_staff_user_has_all_level_management_actions(self):
        response = self.client.get("/gestion/niveles/juego/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear nivel")

    def test_role_permissions_enable_only_granted_level_actions(self):
        reader = get_user_model().objects.create_user(
            username="level-reader",
            password="test-password",
        )
        role = Group.objects.create(name="level-reader-role")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="niveles",
                codename="view_level",
            )
        )
        reader.groups.add(role)
        self.client.force_login(reader)

        dashboard = self.client.get("/gestion/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, "/gestion/niveles/juego/")
        self.assertNotContains(dashboard, "Gestionar Usuarios")

        listing = self.client.get("/gestion/niveles/juego/")
        self.assertEqual(listing.status_code, 200)
        self.assertNotContains(listing, "Crear nivel")

        denied = self.client.get("/gestion/niveles/juego/nuevo/")
        self.assertEqual(denied.status_code, 302)
        self.assertIn("/gestion/login/", denied.url)

    def test_add_permission_enables_create_action_and_view(self):
        creator = get_user_model().objects.create_user(
            username="level-creator",
            password="test-password",
        )
        role = Group.objects.create(name="level-creator-role")
        role.permissions.add(
            Permission.objects.get(
                content_type__app_label="niveles",
                codename="add_level",
            )
        )
        creator.groups.add(role)
        self.client.force_login(creator)

        dashboard = self.client.get("/gestion/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, "/gestion/niveles/juego/nuevo/")

        create_page = self.client.get("/gestion/niveles/juego/nuevo/")
        self.assertEqual(create_page.status_code, 200)
        denied_listing = self.client.get("/gestion/niveles/juego/")
        self.assertEqual(denied_listing.status_code, 302)

    def test_custom_panel_creates_a_level_with_private_solution(self):
        response = self.client.post(
            "/gestion/niveles/juego/nuevo/",
            {
                "number": 1,
                "kind": "branding",
                "title": "Color de marca",
                "instruction": "Selecciona la marca correcta.",
                "data": '{"options": [{"id": "a", "color": "#1E88E5"}]}',
                "solution": '{"option_id": "a"}',
                "active": "on",
            },
        )

        self.assertRedirects(response, "/gestion/niveles/juego/")
        level = Level.objects.get(number=1)
        self.assertEqual(level.data["options"][0]["id"], "a")
        self.assertEqual(level.solution, {"option_id": "a"})

    def test_custom_panel_rejects_invalid_json(self):
        response = self.client.post(
            "/gestion/niveles/juego/nuevo/",
            {
                "number": 1,
                "kind": "branding",
                "title": "Color de marca",
                "instruction": "Selecciona la marca correcta.",
                "data": "{invalid",
                "solution": '{"option_id": "a"}',
                "active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ingresa un JSON válido")
        self.assertFalse(Level.objects.exists())

    def test_custom_panel_edits_and_deletes_levels(self):
        level = Level.objects.create(
            number=1,
            kind="branding",
            title="Nombre anterior",
            instruction="Instrucción",
            data={},
            solution={"option_id": "a"},
        )
        response = self.client.post(
            f"/gestion/niveles/juego/{level.pk}/editar/",
            {
                "number": 1,
                "kind": "hex",
                "title": "Código HEX",
                "instruction": "Elige el código.",
                "data": '{"options": [{"id": "a", "color": "#FFFFFF"}]}',
                "solution": '{"option_id": "a"}',
                "active": "on",
            },
        )

        self.assertRedirects(response, "/gestion/niveles/juego/")
        level.refresh_from_db()
        self.assertEqual(level.title, "Código HEX")
        self.assertEqual(level.kind, "hex")

        response = self.client.post(f"/gestion/niveles/juego/{level.pk}/eliminar/")

        self.assertRedirects(response, "/gestion/niveles/juego/")
        self.assertFalse(Level.objects.exists())

    def test_non_staff_user_cannot_manage_levels(self):
        player = get_user_model().objects.create_user(
            username="regular-player",
            password="test-password",
        )
        self.client.force_login(player)

        response = self.client.get("/gestion/niveles/juego/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/gestion/login/", response.url)

    def test_django_admin_route_is_not_exposed(self):
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 404)
