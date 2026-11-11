from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from niveles.level_seed_data import GAME_LEVELS
from niveles.models import Level


class Command(BaseCommand):
    help = "Crea los 25 niveles jugables iniciales sin sobrescribir niveles existentes."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-conflicts",
            action="store_true",
            help="Conserva los niveles existentes con contenido distinto y carga los demás.",
        )

    def handle(self, *args, **options):
        created = 0
        existing = 0
        conflicts = []
        with transaction.atomic():
            for definition in GAME_LEVELS:
                number = definition["number"]
                defaults = {
                    field: value
                    for field, value in definition.items()
                    if field != "number"
                }
                level, was_created = Level.objects.get_or_create(
                    number=number,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                    continue
                if any(
                    getattr(level, field) != value
                    for field, value in defaults.items()
                ):
                    if options["skip_conflicts"]:
                        conflicts.append(number)
                        continue
                    raise CommandError(
                        f"El nivel {number} ya existe con contenido diferente. "
                        "No se modificaron niveles."
                    )
                existing += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Niveles listos: {created} creados, {existing} ya estaban cargados."
            )
        )
        if conflicts:
            self.stderr.write(
                self.style.WARNING(
                    "Se conservaron sin cambios los niveles con contenido "
                    f"diferente: {', '.join(map(str, conflicts))}."
                )
            )
