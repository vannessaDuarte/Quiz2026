from django.contrib import admin

from .models import DetalleRepuesto, ManoObra, OrdenTrabajo


class DetalleInline(admin.TabularInline):
    model = DetalleRepuesto
    extra = 0


class ManoObraInline(admin.TabularInline):
    model = ManoObra
    extra = 0


@admin.register(OrdenTrabajo)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("id", "vehiculo", "estado", "mecanico", "fecha_recepcion")
    list_filter = ("estado",)
    inlines = [DetalleInline, ManoObraInline]
