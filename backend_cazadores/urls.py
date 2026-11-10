from django.urls import include, path
from django.views.generic.base import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url="/gestion/login/", permanent=False)),
    path("api/", include("niveles.api_urls")),
    path("gestion/", include("usuarios.urls")),
    path("gestion/niveles/", include("niveles.urls")),
]