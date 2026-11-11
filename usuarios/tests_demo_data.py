from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from niveles.models import Level, LevelProgress, Logro, Nivel, Player, Progreso
from usuarios.management.commands.demo_data import DEMO_USERS
from usuarios.models import PerfilUsuario


class DemoDataCommandTests(TestCase):
    def run_demo_command(self, action):
        call_command("demo_data", action, stdout=StringIO())

    def demo_record_counts(self):
        return (
            get_user_model()
            .objects.filter(username__in=DEMO_USERS)
            .count(),
            Group.objects.filter(name__startswith="DEMO |").count(),
            PerfilUsuario.objects.filter(
                usuario__username__in=DEMO_USERS
            ).count(),
            Level.objects.filter(number__gte=9001, number__lte=9003).count(),
            Nivel.objects.filter(numero__gte=9001, numero__lte=9003).count(),
            Logro.objects.filter(nombre_logro__startswith="DEMO |").count(),
            Player.objects.filter(user__username__in=DEMO_USERS).count(),
            Progreso.objects.filter(
                usuario__username__in=DEMO_USERS
            ).count(),
            LevelProgress.objects.filter(
                player__user__username__in=DEMO_USERS
            ).count(),
        )

    def test_load_is_idempotent_and_creates_non_loginable_fictional_accounts(self):
        self.run_demo_command("load")
        first_counts = self.demo_record_counts()

        self.run_demo_command("load")

        self.assertEqual(self.demo_record_counts(), first_counts)
        admin = get_user_model().objects.get(username="demo_admin")
        self.assertFalse(admin.has_usable_password())
        self.assertFalse(admin.is_staff)
        self.assertFalse(admin.is_superuser)
        self.assertEqual(
            admin.email,
            "demo_admin@demo.invalid",
        )
        self.assertTrue(
            Group.objects.get(name="DEMO | Administradores")
            in admin.groups.all()
        )

        reader = get_user_model().objects.get(username="demo_auditor")
        reader_role = Group.objects.get(name="DEMO | Solo lectura")
        self.assertTrue(reader.groups.filter(pk=reader_role.pk).exists())
        self.assertTrue(
            all(
                permission.codename.startswith("view_")
                for permission in reader_role.permissions.all()
            )
        )
        self.assertFalse(
            any(
                permission.codename.startswith(("add_", "change_", "delete_"))
                for permission in reader_role.permissions.all()
            )
        )

    def test_existing_account_collision_is_not_overwritten(self):
        user_model = get_user_model()
        existing = user_model.objects.create_user(
            username="demo_admin",
            email="person@example.invalid",
            password="preexisting-password",
            is_staff=True,
        )

        with self.assertRaisesMessage(CommandError, "no es una cuenta DEMO"):
            self.run_demo_command("load")

        existing.refresh_from_db()
        self.assertEqual(existing.email, "person@example.invalid")
        self.assertTrue(existing.is_staff)
        self.assertTrue(existing.check_password("preexisting-password"))
        self.assertEqual(self.demo_record_counts()[1:], (0, 0, 0, 0, 0, 0, 0, 0))

    def test_clean_removes_demo_records_but_preserves_unrelated_data(self):
        self.run_demo_command("load")
        unrelated_user = get_user_model().objects.create_user(
            username="ordinary-player",
            email="ordinary@example.invalid",
        )
        unrelated_level = Nivel.objects.create(
            numero=1,
            nombre="Nivel real",
            descripcion="Debe permanecer.",
        )
        unrelated_group = Group.objects.create(name="Rol real")

        self.run_demo_command("clean")

        self.assertEqual(self.demo_record_counts(), (0, 0, 0, 0, 0, 0, 0, 0, 0))
        self.assertTrue(get_user_model().objects.filter(pk=unrelated_user.pk).exists())
        self.assertTrue(Nivel.objects.filter(pk=unrelated_level.pk).exists())
        self.assertTrue(Group.objects.filter(pk=unrelated_group.pk).exists())

    def test_clean_preserves_existing_account_with_demo_username(self):
        user = get_user_model().objects.create_user(
            username="demo_admin",
            email="person@example.invalid",
        )

        with self.assertRaisesMessage(CommandError, "no conserva su marcador DEMO"):
            self.run_demo_command("clean")

        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())

    def test_clean_preserves_demo_account_that_has_non_demo_activity(self):
        self.run_demo_command("load")
        demo_user = get_user_model().objects.get(username="demo_jugador")
        unrelated_level = Nivel.objects.create(
            numero=1,
            nombre="Nivel agregado durante la demostracion",
        )
        Progreso.objects.create(
            usuario=demo_user,
            nivel=unrelated_level,
            puntaje=10,
        )

        self.run_demo_command("clean")

        demo_user.refresh_from_db()
        self.assertTrue(demo_user.is_active)
        self.assertEqual(self.demo_record_counts()[0], 1)
        self.assertTrue(Nivel.objects.filter(pk=unrelated_level.pk).exists())
        self.assertTrue(
            Nivel.objects.filter(numero=9001, nombre="DEMO | Mezcla de colores").exists()
        )
