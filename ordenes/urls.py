from django.urls import path

from . import views

app_name = "ordenes"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("nueva/", views.nueva, name="nueva"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/asignar/", views.asignar, name="asignar"),
    path("<int:pk>/diagnostico/", views.diagnostico, name="diagnostico"),
    path("<int:pk>/repuesto/", views.repuesto, name="repuesto"),
    path("<int:pk>/mano-obra/", views.mano_obra, name="mano_obra"),
    path("<int:pk>/enviar/", views.enviar, name="enviar"),
    path("<int:pk>/decidir/", views.decidir_view, name="decidir"),
    path("<int:pk>/generar-reparacion/", views.generar_reparacion, name="generar_reparacion"),
    path("<int:pk>/estado/", views.cambiar_estado, name="cambiar_estado"),
    path("<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
