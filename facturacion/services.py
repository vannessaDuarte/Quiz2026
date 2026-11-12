from django.db.models import Max

from taller.services import notificar

from .models import Factura


def crear_factura(orden):
    """RF-21: genera la boleta/factura cuando la orden pasa a 'listo para retiro'."""
    existente = Factura.objects.filter(orden=orden).first()
    if existente:
        return existente
    ultimo = Factura.objects.aggregate(m=Max("numero"))["m"] or 0
    factura = Factura.objects.create(orden=orden, numero=ultimo + 1, neto=orden.neto)
    notificar("admin", f"Se generó la {factura} por la orden #{orden.pk}.", orden=orden)
    return factura
