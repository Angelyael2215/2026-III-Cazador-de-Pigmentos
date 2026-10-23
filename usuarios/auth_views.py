from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse


class AppLoginView(LoginView):
    template_name = "usuarios/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse("dashboard_admin")

        return reverse("bienvenida_jugador")


class AppLogoutView(LogoutView):
    pass