from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse

from .permissions import has_management_access


class AppLoginView(LoginView):
    template_name = "usuarios/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        if has_management_access(self.request.user):
            return reverse("dashboard_admin")

        return reverse("bienvenida_jugador")


class AppLogoutView(LogoutView):
    pass