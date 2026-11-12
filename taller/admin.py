from django.contrib import admin

from .models import Mecanico, Notificacion, Proveedor, Repuesto

admin.site.register(Mecanico)
admin.site.register(Proveedor)
admin.site.register(Repuesto)
admin.site.register(Notificacion)
