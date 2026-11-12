from django.urls import path

from . import views

app_name = "facturacion"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/descuento/", views.descuento, name="descuento"),
    path("reportes/", views.reportes, name="reportes"),
]
