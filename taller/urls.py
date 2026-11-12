from django.urls import path

from . import views

app_name = "taller"

urlpatterns = [
    path("mecanicos/", views.mecanicos, name="mecanicos"),
    path("mecanicos/nuevo/", views.mecanico_nuevo, name="mecanico_nuevo"),
    path("mecanicos/<int:pk>/", views.mecanico_detalle, name="mecanico_detalle"),
    path("repuestos/", views.repuestos, name="repuestos"),
    path("repuestos/nuevo/", views.repuesto_nuevo, name="repuesto_nuevo"),
    path("repuestos/<int:pk>/", views.repuesto_detalle, name="repuesto_detalle"),
    path("repuestos/<int:pk>/editar/", views.repuesto_editar, name="repuesto_editar"),
    path("proveedores/", views.proveedores, name="proveedores"),
    path("proveedores/nuevo/", views.proveedor_nuevo, name="proveedor_nuevo"),
    path("reportes/repuestos/", views.reporte_repuestos, name="reporte_repuestos"),
    path("notificaciones/", views.notificaciones, name="notificaciones"),
]
