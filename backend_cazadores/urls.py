from django.urls import include, path
from django.views.generic.base import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="/gestion/login/", permanent=False)),
    path("gestion/", include("usuarios.urls")),
    path("gestion/niveles/", include("niveles.urls")),
]