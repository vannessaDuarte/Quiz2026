from collections import defaultdict

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.roles import ADMIN, CLIENTE, RECEPCION, actor_id, rol_actual, rol_requerido

from .forms import FacturaForm
from .models import Factura


@rol_requerido(ADMIN)
def lista(request):  # RF-22
    facturas = Factura.objects.select_related("orden__vehiculo__cliente")
    return render(request, "facturacion/lista.html", {"facturas": facturas})


@rol_requerido(ADMIN, RECEPCION, CLIENTE)
def detalle(request, pk):
    factura = get_object_or_404(Factura.objects.select_related("orden__vehiculo__cliente"), pk=pk)
    if rol_actual(request) == CLIENTE and factura.orden.vehiculo.cliente_id != actor_id(request):
        messages.error(request, "No tienes acceso a ese documento.")
        return redirect("ordenes:lista")
    ctx = {"f": factura, "orden": factura.orden}
    if rol_actual(request) == ADMIN:
        ctx["form"] = FacturaForm(instance=factura)
    return render(request, "facturacion/detalle.html", ctx)


@rol_requerido(ADMIN)
def descuento(request, pk):  # RF-23
    factura = get_object_or_404(Factura, pk=pk)
    if request.method == "POST":
        form = FacturaForm(request.POST, instance=factura)
        if form.is_valid():
            form.save()
            messages.success(request, "Documento actualizado.")
        else:
            messages.error(request, "; ".join(e for errs in form.errors.values() for e in errs))
    return redirect("facturacion:detalle", pk=pk)


@rol_requerido(ADMIN)
def reportes(request):  # RF-27
    facturas = list(Factura.objects.select_related("orden"))
    por_mes = defaultdict(lambda: {"cantidad": 0, "neto": 0, "descuentos": 0, "total": 0})
    for f in facturas:
        fila = por_mes[timezone.localtime(f.fecha).strftime("%Y-%m")]
        fila["cantidad"] += 1
        fila["neto"] += f.neto
        fila["descuentos"] += f.monto_descuento
        fila["total"] += f.total
    resumen = {
        "cantidad": len(facturas),
        "boletas": sum(1 for f in facturas if f.tipo == Factura.BOLETA),
        "facturas": sum(1 for f in facturas if f.tipo == Factura.FACTURA),
        "descuentos": sum(f.monto_descuento for f in facturas),
        "total": sum(f.total for f in facturas),
    }
    return render(request, "facturacion/reportes.html", {"resumen": resumen, "meses": sorted(por_mes.items(), reverse=True)})
