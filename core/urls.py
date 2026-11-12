from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("rol/", views.elegir_rol, name="elegir_rol"),
    path("salir/", views.salir, name="salir"),
]
