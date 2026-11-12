from django.contrib import messages
from django.db.models import Count, IntegerField, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from core.roles import ADMIN, CLIENTE, MECANICO, RECEPCION, notificaciones_de, rol_requerido

from .forms import MecanicoForm, ProveedorForm, RepuestoForm
from .models import Mecanico, Proveedor, Repuesto


# ---- Mecánicos (RF-15, RF-25) ----
@rol_requerido(ADMIN)
def mecanicos(request):
    lista = [(m, m.libre) for m in Mecanico.objects.annotate(n_ordenes=Count("ordenes"))]
    return render(request, "taller/mecanicos.html", {"mecanicos": lista})


@rol_requerido(ADMIN)
def mecanico_nuevo(request):
    form = MecanicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Mecánico registrado.")
        return redirect("taller:mecanicos")
    return render(request, "core/form.html", {"form": form, "titulo": "Nuevo mecánico", "volver": "taller:mecanicos", "boton": "Guardar"})


@rol_requerido(ADMIN)
def mecanico_detalle(request, pk):
    m = get_object_or_404(Mecanico, pk=pk)
    return render(request, "taller/mecanico_detalle.html", {"m": m, "ordenes": m.ordenes.select_related("vehiculo__cliente")})


# ---- Repuestos (RF-26) ----
@rol_requerido(ADMIN)
def repuestos(request):
    return render(request, "taller/repuestos.html", {"repuestos": Repuesto.objects.select_related("proveedor")})


@rol_requerido(ADMIN)
def repuesto_nuevo(request):
    form = RepuestoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Repuesto registrado.")
        return redirect("taller:repuestos")
    return render(request, "core/form.html", {"form": form, "titulo": "Nuevo repuesto", "volver": "taller:repuestos", "boton": "Guardar"})


@rol_requerido(ADMIN)
def repuesto_editar(request, pk):
    r = get_object_or_404(Repuesto, pk=pk)
    form = RepuestoForm(request.POST or None, instance=r)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Repuesto actualizado (p. ej. nuevo stock).")
        return redirect("taller:repuesto_detalle", pk=pk)
    return render(request, "core/form.html", {"form": form, "titulo": f"Editar {r.nombre}", "volver": "taller:repuestos", "boton": "Guardar cambios"})


@rol_requerido(ADMIN)
def repuesto_detalle(request, pk):
    r = get_object_or_404(Repuesto.objects.select_related("proveedor"), pk=pk)
    usos = r.usos.select_related("orden__vehiculo")
    return render(request, "taller/repuesto_detalle.html", {"r": r, "usos": usos, "total_usado": usos.aggregate(t=Coalesce(Sum("cantidad"), 0, output_field=IntegerField()))["t"]})


# ---- Proveedores (RF-29) ----
@rol_requerido(ADMIN, RECEPCION)
def proveedores(request):
    return render(request, "taller/proveedores.html", {"proveedores": Proveedor.objects.annotate(n=Count("repuestos"))})


@rol_requerido(ADMIN, RECEPCION)
def proveedor_nuevo(request):
    form = ProveedorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proveedor registrado.")
        return redirect("taller:proveedores")
    return render(request, "core/form.html", {"form": form, "titulo": "Nuevo proveedor", "volver": "taller:proveedores", "boton": "Guardar"})


# ---- Reporte de repuestos (RF-28) ----
@rol_requerido(ADMIN)
def reporte_repuestos(request):
    datos = Repuesto.objects.select_related("proveedor").annotate(usado=Coalesce(Sum("usos__cantidad"), 0, output_field=IntegerField())).order_by("-usado", "nombre")
    return render(request, "taller/reporte_repuestos.html", {"repuestos": datos, "bajos": [r for r in datos if r.bajo_stock]})


# ---- Notificaciones (RF-05, RF-13, RF-20) ----
@rol_requerido(ADMIN, RECEPCION, MECANICO, CLIENTE)
def notificaciones(request):
    qs = notificaciones_de(request)
    lista = list(qs[:100])
    qs.filter(leida=False).update(leida=True)
    return render(request, "taller/notificaciones.html", {"notificaciones": lista})
