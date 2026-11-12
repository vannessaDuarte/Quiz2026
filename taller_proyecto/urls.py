from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("clientes/", include("clientes.urls")),
    path("ordenes/", include("ordenes.urls")),
    path("taller/", include("taller.urls")),
    path("facturacion/", include("facturacion.urls")),
]
