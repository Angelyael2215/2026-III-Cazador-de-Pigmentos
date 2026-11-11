from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from niveles.models import Player


class AdventureInterfaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.player = get_user_model().objects.create_user(
            username="adventure-ui-player",
            password="test-password",
        )

    def test_login_and_registration_use_the_adventure_design(self):
        login = self.client.get(reverse("login"))
        registration = self.client.get(reverse("registro"))

        self.assertEqual(login.status_code, 200)
        self.assertContains(login, "adventure.css")
        self.assertContains(login, "Entrar a la expedición")
        self.assertContains(login, 'name="username"')
        self.assertContains(login, 'aria-label="Mostrar contraseña"')

        self.assertEqual(registration.status_code, 200)
        self.assertContains(registration, "adventure.css")
        self.assertContains(registration, "Comienza tu aventura")
        self.assertContains(registration, 'name="username"')

    def test_welcome_and_horizontal_map_share_the_responsive_design(self):
        call_command("seed_game_levels")
        self.client.force_login(self.player)
        welcome = self.client.get(reverse("bienvenida_jugador"))
        map_page = self.client.get(reverse("mapa_niveles"))

        self.assertEqual(welcome.status_code, 200)
        self.assertContains(welcome, "adventure.css")
        self.assertContains(welcome, "Mis niveles")

        self.assertEqual(map_page.status_code, 200)
        self.assertContains(map_page, "La ruta del pigmento")
        self.assertContains(map_page, "25 niveles")
        self.assertContains(map_page, "treasure-route__trail--desktop")
        self.assertContains(map_page, "treasure-route__trail--mobile")
        self.assertEqual(map_page.content.count(b'class="treasure-node '), 25)
        self.assertContains(map_page, reverse("jugar_nivel", args=[1]))

    def test_all_seeded_levels_render_the_dynamic_game_and_keep_solutions_private(self):
        call_command("seed_game_levels")
        self.client.force_login(self.player)
        player, _ = Player.objects.get_or_create(user=self.player)
        player.current_level_reached = 25
        player.save(update_fields=["current_level_reached"])

        for level_number in range(1, 26):
            with self.subTest(level=level_number):
                response = self.client.get(
                    reverse("jugar_nivel", args=[level_number])
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "adventure.css")
                self.assertContains(response, f"Nivel {level_number}")
                self.assertNotContains(response, '"solution"')

    def test_legacy_level_url_redirects_to_database_game(self):
        call_command("seed_game_levels")
        self.client.force_login(self.player)

        response = self.client.get(reverse("detalle_nivel", args=[1]))

        self.assertRedirects(response, reverse("jugar_nivel", args=[1]))

    def test_shared_design_has_responsive_and_reduced_motion_rules(self):
        stylesheet = (
            Path(__file__).parent / "static" / "usuarios" / "adventure.css"
        ).read_text()

        self.assertIn("@media (max-width: 760px)", stylesheet)
        self.assertIn("@media (max-width: 430px)", stylesheet)
        self.assertIn("@media (prefers-reduced-motion: reduce)", stylesheet)
        self.assertIn(".treasure-route__trail--mobile", stylesheet)
        self.assertIn(":focus-visible", stylesheet)
