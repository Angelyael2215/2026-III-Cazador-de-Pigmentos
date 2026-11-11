from django.db import models
from django.contrib.auth.models import User


class LevelKind(models.TextChoices):
    MIX = "mix", "Mezclas"
    BRANDING = "branding", "Branding"
    GRADIENT = "gradient", "Degradados"
    CONTRAST = "contrast", "Contraste"
    HARMONY = "harmony", "Armonía"
    COLOR_BLINDNESS = "color_blindness", "Daltonismo"
    RGB = "rgb", "Laboratorio RGB"
    TEMPERATURE = "temperature", "Temperatura"
    HEX = "hex", "Código HEX"
    ALBERS = "albers", "Ilusión óptica"
    ATMOSPHERE = "atmosphere", "Atmósferas"
    SATURATION = "saturation", "Saturación"


class Level(models.Model):
    number = models.PositiveIntegerField(unique=True)
    kind = models.CharField(max_length=32, choices=LevelKind.choices)
    title = models.CharField(max_length=100)
    instruction = models.TextField()
    data = models.JSONField(default=dict)
    solution = models.JSONField(default=dict)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"{self.number}: {self.title}"


class Player(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="level_player",
        null=True,
        blank=True,
    )
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    current_level_reached = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    pigments = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.firebase_uid or (self.user.get_username() if self.user else str(self.pk))


class LevelProgress(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    attempts = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["player", "level"],
                name="one_progress_per_player_level",
            )
        ]

    def __str__(self):
        return f"{self.player} - {self.level}"


class Nivel(models.Model):
    numero = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    instrucciones = models.TextField(blank=True)

    class Meta:
        permissions = [
            ("can_design_levels", "Puede diseñar y editar niveles"),
        ]

    def __str__(self):
        return f"Nivel {self.numero} - {self.nombre}"

class Progreso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progresos')
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    puntaje = models.IntegerField(default=0)
    completado = models.BooleanField(default=False)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'nivel')

    def __str__(self):
        return f"Progreso de {self.usuario.username} en {self.nivel.nombre}"

class Logro(models.Model):
    nombre_logro = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre_logro

class UsuarioLogro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logros')
    logro = models.ForeignKey(Logro, on_delete=models.CASCADE)
    fecha_obtenido = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'logro')

    def __str__(self):
        return f"{self.usuario.username} - {self.logro.nombre_logro}"

class ModuloTeorico(models.Model):
    titulo = models.CharField(max_length=100) # Ej: "Módulo Especial: El Código Oculto"
    orden = models.IntegerField(unique=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.orden}. {self.titulo}"



class SesionNivel(models.Model):
    perfil = models.ForeignKey('usuarios.PerfilUsuario', on_delete=models.CASCADE, related_name='sesiones')
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    puntaje_obtenido = models.IntegerField(default=0)
    intentos = models.IntegerField(default=1)
    fecha_superado = models.DateTimeField(auto_now=True)