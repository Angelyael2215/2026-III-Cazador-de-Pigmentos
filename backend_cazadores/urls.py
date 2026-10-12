from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('gestion/', include('usuarios.urls')),
]