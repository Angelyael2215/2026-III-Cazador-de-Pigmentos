from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from niveles.models import (
    Level,
    LevelProgress,
    Logro,
    Nivel,
    Player,
    Progreso,
    UsuarioLogro,
)
from usuarios.models import PerfilUsuario


DEMO_USERS = {
    "demo_admin": {
        "email": "demo_admin@demo.invalid",
        "first_name": "Demo",
        "last_name": "Administracion",
        "role": "DEMO | Administradores",
        "profile": {
            "vidas": 5,
            "gemas": 120,
            "nivel_maximo_desbloqueado": 3,
        },
    },
    "demo_auditor": {
        "email": "demo_auditor@demo.invalid",
        "first_name": "Demo",
        "last_name": "Auditoria",
        "role": "DEMO | Solo lectura",
        "profile": {
            "vidas": 4,
            "gemas": 60,
            "nivel_maximo_desbloqueado": 2,
        },
    },
    "demo_jugador": {
        "email": "demo_jugador@demo.invalid",
        "first_name": "Demo",
        "last_name": "Jugador",
        "role": "DEMO | Jugadores",
        "profile": {
            "vidas": 3,
            "gemas": 25,
            "nivel_maximo_desbloqueado": 2,
        },
    },
}

DEMO_MODELS = (
    ("auth", "group"),
    ("auth", "permission"),
    ("auth", "user"),
    ("usuarios", "perfilusuario"),
    ("niveles", "nivel"),
    ("niveles", "progreso"),
    ("niveles", "logro"),
    ("niveles", "usuariologro"),
    ("niveles", "level"),
    ("niveles", "player"),
    ("niveles", "levelprogress"),
)
DEMO_CRUD_ACTIONS = ("add", "change", "delete", "view")
DEMO_READ_ACTIONS = ("view",)

DEMO_LEVELS = (
    {
        "number": 9001,
        "kind": "mix",
        "title": "DEMO | Mezcla de colores",
        "instruction": "Identifica los colores primarios de la mezcla.",
        "data": {"colors": ["#FF0000", "#0000FF"]},
        "solution": {"colors": ["#FF0000", "#0000FF"]},
        "active": True,
    },
    {
        "number": 9002,
        "kind": "contrast",
        "title": "DEMO | Contraste accesible",
        "instruction": "Compara el contraste entre dos colores.",
        "data": {"colors": ["#FFFFFF", "#222222"]},
        "solution": {"colors": ["#FFFFFF", "#222222"]},
        "active": True,
    },
    {
        "number": 9003,
        "kind": "branding",
        "title": "DEMO | Identidad de color",
        "instruction": "Relaciona una identidad visual con su color.",
        "data": {"options": [{"id": "a", "color": "#2E7D32"}]},
        "solution": {"option_id": "a"},
        "active": True,
    },
)

DEMO_ACHIEVEMENTS = (
    {
        "nombre_logro": "DEMO | Primer pigmento",
        "descripcion": "Completa tu primer nivel de color.",
    },
    {
        "nombre_logro": "DEMO | Explorador del color",
        "descripcion": "Explora varios conceptos de color.",
    },
)

DEMO_LEVELS_BY_NUMBER = {level["number"]: level for level in DEMO_LEVELS}
DEMO_ACHIEVEMENTS_BY_NAME = {
    achievement["nombre_logro"]: achievement
    for achievement in DEMO_ACHIEVEMENTS
}

LEGACY_LEVELS = (
    {
        "numero": 9001,
        "nombre": "DEMO | Mezcla de colores",
        "descripcion": "Nivel ficticio para probar el panel de administracion.",
        "instrucciones": "Identifica los colores primarios de la mezcla.",
    },
    {
        "numero": 9002,
        "nombre": "DEMO | Contraste accesible",
        "descripcion": "Nivel ficticio para probar filtros y asignaciones.",
        "instrucciones": "Compara el contraste entre dos colores.",
    },
    {
        "numero": 9003,
        "nombre": "DEMO | Identidad de color",
        "descripcion": "Nivel ficticio para probar la gestion de niveles.",
        "instrucciones": "Relaciona una identidad visual con su color.",
    },
)
LEGACY_LEVELS_BY_NUMBER = {level["numero"]: level for level in LEGACY_LEVELS}


def expected_group_permissions(role_name):
    if role_name == DEMO_USERS["demo_admin"]["role"]:
        actions = DEMO_CRUD_ACTIONS
    elif role_name == DEMO_USERS["demo_auditor"]["role"]:
        actions = DEMO_READ_ACTIONS
    else:
        actions = ()
    permissions = set()
    for app_label, model in DEMO_MODELS:
        content_type = ContentType.objects.get_by_natural_key(app_label, model)
        for action in actions:
            permission = Permission.objects.get(
                content_type=content_type,
                codename=f"{action}_{model}",
            )
            permissions.add(permission)
    if role_name == DEMO_USERS["demo_admin"]["role"]:
        for codename in ("can_design_levels", "can_reset_lives", "can_give_gems"):
            permission = Permission.objects.filter(
                content_type__app_label__in=("niveles", "usuarios"),
                codename=codename,
            ).first()
            if permission:
                permissions.add(permission)
    return permissions


class Command(BaseCommand):
    help = "Carga o limpia cuentas y contenido ficticio para demostrar el panel."

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=("load", "clean"),
            help="load crea los datos; clean elimina solo los datos DEMO identificados.",
        )

    def handle(self, *_args, **options):
        if _args:
            raise CommandError("No se esperaban argumentos adicionales.")
        action = options["action"]
        with transaction.atomic():
            if action == "load":
                self.load_demo_data()
            else:
                self.clean_demo_data()

    def ensure_record(self, model, lookup, defaults, description):
        record = model.objects.filter(**lookup).first()
        if record is None:
            return model.objects.create(**lookup, **defaults), True

        for field, expected in defaults.items():
            if getattr(record, field) != expected:
                raise CommandError(
                    f"Conflicto con {description}; no se modifico ningun dato."
                )
        return record, False

    def ensure_user(self, username, spec):
        user_model = get_user_model()
        user = user_model.objects.filter(username=username).first()
        if user is None:
            user = user_model(
                username=username,
                email=spec["email"],
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            user.set_unusable_password()
            user.save()
            return user, True

        expected_values = {
            "email": spec["email"],
            "first_name": spec["first_name"],
            "last_name": spec["last_name"],
            "is_active": True,
            "is_staff": False,
            "is_superuser": False,
        }
        if any(
            getattr(user, field) != expected
            for field, expected in expected_values.items()
        ):
            raise CommandError(
                f"El usuario '{username}' ya existe y no es una cuenta DEMO "
                "reconocible; no se modifico."
            )
        return user, False

    def ensure_group(self, role_name):
        permissions = expected_group_permissions(role_name)
        group = Group.objects.filter(name=role_name).first()
        if group is None:
            group = Group.objects.create(name=role_name)
            group.permissions.set(permissions)
            return group

        current_permissions = set(group.permissions.all())
        if current_permissions != permissions:
            raise CommandError(
                f"El rol '{role_name}' ya existe con permisos diferentes; "
                "no se modifico."
            )
        return group

    def load_demo_data(self):
        groups = {
            role: self.ensure_group(role)
            for role in {spec["role"] for spec in DEMO_USERS.values()}
        }

        users = {}
        for username, spec in DEMO_USERS.items():
            user, created = self.ensure_user(username, spec)
            users[username] = user
            user.groups.add(groups[spec["role"]])
            self.ensure_record(
                PerfilUsuario,
                {"usuario": user},
                spec["profile"],
                f"el perfil DEMO de '{username}'",
            )
            if created:
                self.stdout.write(f"Cuenta DEMO creada: {username}")

        legacy_levels = {}
        api_levels = {}
        for level_data in DEMO_LEVELS:
            number = level_data["number"]
            api_levels[number], _ = self.ensure_record(
                Level,
                {"number": number},
                {
                    field: value
                    for field, value in level_data.items()
                    if field != "number"
                },
                f"el nivel DEMO {number}",
            )
            legacy_data = LEGACY_LEVELS_BY_NUMBER[number]
            legacy_levels[number], _ = self.ensure_record(
                Nivel,
                {"numero": number},
                {
                    field: value
                    for field, value in legacy_data.items()
                    if field != "numero"
                },
                f"el nivel DEMO heredado {number}",
            )

        achievements = {}
        for achievement_data in DEMO_ACHIEVEMENTS:
            achievement, _ = self.ensure_record(
                Logro,
                {"nombre_logro": achievement_data["nombre_logro"]},
                {"descripcion": achievement_data["descripcion"]},
                f"el logro '{achievement_data['nombre_logro']}'",
            )
            achievements[achievement_data["nombre_logro"]] = achievement

        player, _ = self.ensure_record(
            Player,
            {"user": users["demo_jugador"]},
            {
                "current_level_reached": 2,
                "xp": 20,
                "pigments": 2,
            },
            "el jugador DEMO",
        )

        self.ensure_record(
            Progreso,
            {
                "usuario": users["demo_jugador"],
                "nivel": legacy_levels[9001],
            },
            {"puntaje": 100, "completado": True},
            "el progreso DEMO del primer nivel",
        )
        self.ensure_record(
            Progreso,
            {
                "usuario": users["demo_jugador"],
                "nivel": legacy_levels[9002],
            },
            {"puntaje": 45, "completado": False},
            "el progreso DEMO del segundo nivel",
        )

        for number, attempts, completed in ((9001, 1, True), (9002, 2, False)):
            self.ensure_record(
                LevelProgress,
                {"player": player, "level": api_levels[number]},
                {
                    "attempts": attempts,
                    "completed": completed,
                    "completed_at": None,
                },
                f"el progreso API DEMO del nivel {number}",
            )

        for achievement_name in DEMO_ACHIEVEMENTS_BY_NAME:
            self.ensure_record(
                UsuarioLogro,
                {
                    "usuario": users["demo_jugador"],
                    "logro": achievements[achievement_name],
                },
                {},
                f"la asignacion DEMO del logro '{achievement_name}'",
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Datos DEMO listos. Para iniciar sesion, establece contrasenas "
                "localmente con: python manage.py changepassword demo_admin "
                "(tambien demo_auditor o demo_jugador)."
            )
        )

    def demo_users(self):
        user_model = get_user_model()
        users = []
        for username, spec in DEMO_USERS.items():
            user = user_model.objects.filter(username=username).first()
            if user is None:
                continue
            if user.email != spec["email"]:
                raise CommandError(
                    f"El usuario '{username}' no conserva su marcador DEMO; "
                    "se cancelo la limpieza."
                )
            users.append(user)
        return users

    def user_has_only_demo_data(self, user):
        spec = DEMO_USERS[user.username]
        profile = PerfilUsuario.objects.filter(usuario=user).first()
        if profile and any(
            getattr(profile, field) != expected
            for field, expected in spec["profile"].items()
        ):
            return False
        if profile and profile.sesiones.exists():
            return False

        demo_roles = {user_spec["role"] for user_spec in DEMO_USERS.values()}
        if user.groups.exclude(name__in=demo_roles).exists():
            return False
        if user.user_permissions.exists():
            return False

        if user.evaluaciones.exists():
            return False

        expected_legacy_progress = (
            {9001: (100, True), 9002: (45, False)}
            if user.username == "demo_jugador"
            else {}
        )
        legacy_progress = list(
            Progreso.objects.filter(usuario=user).select_related("nivel")
        )
        if len(legacy_progress) != len(expected_legacy_progress):
            return False
        for progress in legacy_progress:
            expected = expected_legacy_progress.get(progress.nivel.numero)
            if expected != (progress.puntaje, progress.completado):
                return False

        expected_achievements = (
            set(DEMO_ACHIEVEMENTS_BY_NAME)
            if user.username == "demo_jugador"
            else set()
        )
        assigned_achievements = {
            assignment.logro.nombre_logro
            for assignment in UsuarioLogro.objects.filter(usuario=user).select_related(
                "logro"
            )
        }
        if assigned_achievements != expected_achievements:
            return False

        player = Player.objects.filter(user=user).first()
        if user.username != "demo_jugador":
            return player is None
        if player is None or (
            player.current_level_reached,
            player.xp,
            player.pigments,
            player.firebase_uid,
        ) != (2, 20, 2, None):
            return False

        expected_api_progress = {
            9001: (1, True, None),
            9002: (2, False, None),
        }
        api_progress = list(
            LevelProgress.objects.filter(player=player).select_related("level")
        )
        if len(api_progress) != len(expected_api_progress):
            return False
        return all(
            expected_api_progress.get(progress.level.number)
            == (
                progress.attempts,
                progress.completed,
                progress.completed_at,
            )
            for progress in api_progress
        )

    def clean_demo_data(self):
        users = self.demo_users()
        user_model = get_user_model()

        cleanable_users = [
            user for user in users if self.user_has_only_demo_data(user)
        ]
        preserved_users = len(users) - len(cleanable_users)
        for user in cleanable_users:
            user.delete()

        removed_groups = 0
        for role_name in {spec["role"] for spec in DEMO_USERS.values()}:
            group = Group.objects.filter(name=role_name).first()
            if group is None:
                continue
            external_members = user_model.objects.filter(groups=group).exists()
            expected_permissions = expected_group_permissions(role_name)
            if (
                not external_members
                and set(group.permissions.all()) == expected_permissions
            ):
                group.delete()
                removed_groups += 1

        removed_levels = 0
        for number, level_data in DEMO_LEVELS_BY_NUMBER.items():
            level = Level.objects.filter(number=number).first()
            if level is None:
                continue
            expected_fields = {
                field: value
                for field, value in level_data.items()
                if field != "number"
            }
            if any(
                getattr(level, field) != expected
                for field, expected in expected_fields.items()
            ):
                continue
            if LevelProgress.objects.filter(level=level).exists():
                continue
            level.delete()
            removed_levels += 1

        removed_legacy_levels = 0
        for number, level_data in LEGACY_LEVELS_BY_NUMBER.items():
            level = Nivel.objects.filter(numero=number).first()
            if level is None:
                continue
            expected_fields = {
                field: value
                for field, value in level_data.items()
                if field != "numero"
            }
            if any(
                getattr(level, field) != expected
                for field, expected in expected_fields.items()
            ):
                continue
            if Progreso.objects.filter(nivel=level).exists():
                continue
            if level.sesionnivel_set.exists():
                continue
            level.delete()
            removed_legacy_levels += 1

        removed_achievements = 0
        for name, achievement_data in DEMO_ACHIEVEMENTS_BY_NAME.items():
            achievement = Logro.objects.filter(nombre_logro=name).first()
            if achievement is None:
                continue
            if achievement.descripcion != achievement_data["descripcion"]:
                continue
            if UsuarioLogro.objects.filter(logro=achievement).exists():
                continue
            achievement.delete()
            removed_achievements += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Limpieza DEMO completada: "
                f"{len(cleanable_users)} cuentas eliminadas, "
                f"{preserved_users} cuentas conservadas por tener datos ajenos "
                f"a DEMO, {removed_groups} roles, "
                f"{removed_levels} niveles API, {removed_legacy_levels} niveles "
                f"y {removed_achievements} logros eliminados."
            )
        )
