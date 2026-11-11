from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    vidas = models.IntegerField(default=5)
    gemas = models.IntegerField(default=0)
    nivel_maximo_desbloqueado = models.IntegerField(default=1)

    class Meta:
        permissions = [
            ("can_reset_lives", "Puede reiniciar vidas de usuarios"),
            ("can_give_gems", "Puede regalar gemas"),
        ]

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    def get_absolute_url(self):
        return reverse('perfil_editar',args=[str(self.id)])

    @property
    def tiene_vidas(self):
        return self.vidas > 0

    @property
    def jugador_avanzado(self):
        return self.nivel_maximo_desbloqueado >=10

    def perder_vidad(self):
        if self.vidas > 0:
            self.vidas -= 1
            self.save()
            return True
        return False

    def sumar_gemas(self,cantidad):
        if cantidad > 0:
            self.gemas += cantidad
            self.save()

class EvaluacionAccesibilidad(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones')
    color_fondo_hex = models.CharField(max_length=7)
    color_texto_hex = models.CharField(max_length=7)
    ratio_contraste = models.DecimalField(max_digits=4, decimal_places=2)
    cumple_wcag_aa = models.BooleanField(default=False)
    cumple_wcag_aaa = models.BooleanField(default=False)
    fecha_evaluacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluación {self.id} de {self.usuario.username}"

    # solo lectura

    @property
    def nivel_aprobacion(self):
        if self.cumple_wcag_aaa:
            return "nivel optimo"
        elif self.cumple_wcag_aa:
            return "nivel aceptable"
        return "no cumple "