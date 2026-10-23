from django.urls import path

from . import views


urlpatterns = [
    path("", views.NivelListView.as_view(), name="nivel_lista"),
    path("nuevo/", views.NivelCreateView.as_view(), name="nivel_crear"),
    path("<int:pk>/editar/", views.NivelUpdateView.as_view(), name="nivel_editar"),
    path(
        "<int:pk>/eliminar/",
        views.NivelDeleteView.as_view(),
        name="nivel_eliminar",
    ),

    path("progresos/", views.ProgresoListView.as_view(), name="progreso_lista"),
    path(
        "progresos/nuevo/",
        views.ProgresoCreateView.as_view(),
        name="progreso_crear",
    ),
    path(
        "progresos/<int:pk>/editar/",
        views.ProgresoUpdateView.as_view(),
        name="progreso_editar",
    ),
    path(
        "progresos/<int:pk>/eliminar/",
        views.ProgresoDeleteView.as_view(),
        name="progreso_eliminar",
    ),

    path("logros/", views.LogroListView.as_view(), name="logro_lista"),
    path("logros/nuevo/", views.LogroCreateView.as_view(), name="logro_crear"),
    path(
        "logros/<int:pk>/editar/",
        views.LogroUpdateView.as_view(),
        name="logro_editar",
    ),
    path(
        "logros/<int:pk>/eliminar/",
        views.LogroDeleteView.as_view(),
        name="logro_eliminar",
    ),

    path(
        "usuarios-logros/",
        views.UsuarioLogroListView.as_view(),
        name="usuariologro_lista",
    ),
    path(
        "usuarios-logros/nuevo/",
        views.UsuarioLogroCreateView.as_view(),
        name="usuariologro_crear",
    ),
    path(
        "usuarios-logros/<int:pk>/editar/",
        views.UsuarioLogroUpdateView.as_view(),
        name="usuariologro_editar",
    ),
    path(
        "usuarios-logros/<int:pk>/eliminar/",
        views.UsuarioLogroDeleteView.as_view(),
        name="usuariologro_eliminar",
    ),
]