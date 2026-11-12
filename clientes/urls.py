from django.urls import path

from . import views

app_name = "clientes"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nuevo/", views.nuevo, name="nuevo"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/vehiculo/nuevo/", views.vehiculo_nuevo, name="vehiculo_nuevo"),
    path("vehiculos/", views.vehiculos, name="vehiculos"),
    path("vehiculos/<int:pk>/", views.vehiculo_detalle, name="vehiculo_detalle"),
]
