from django.db import models
from django.contrib.auth.models import User

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