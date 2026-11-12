from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from core.roles import ADMIN, RECEPCION, rol_requerido

from .forms import ClienteForm, VehiculoForm
from .models import Cliente, Vehiculo


@rol_requerido(ADMIN, RECEPCION)
def lista(request):
    q = request.GET.get("q", "").strip()
    clientes = Cliente.objects.annotate(n_vehiculos=Count("vehiculos"))
    if q:
        clientes = clientes.filter(Q(nombre__icontains=q) | Q(rut__icontains=q))
    return render(request, "clientes/lista.html", {"clientes": clientes, "q": q})


@rol_requerido(ADMIN, RECEPCION)
def nuevo(request):  # RF-01
    form = ClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        c = form.save()
        messages.success(request, "Cliente registrado. Ahora puedes agregar sus vehículos.")
        return redirect("clientes:detalle", pk=c.pk)
    return render(request, "core/form.html", {"form": form, "titulo": "Nuevo cliente", "volver": "clientes:lista", "boton": "Guardar cliente"})


@rol_requerido(ADMIN, RECEPCION)
def detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, "clientes/detalle.html", {"cliente": cliente, "vehiculos": cliente.vehiculos.all()})


@rol_requerido(ADMIN, RECEPCION)
def vehiculo_nuevo(request, pk):  # RF-02 (uno o varios vehículos)
    cliente = get_object_or_404(Cliente, pk=pk)
    form = VehiculoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        v = form.save(commit=False)
        v.cliente = cliente
        v.save()
        messages.success(request, f"Vehículo {v.patente} registrado.")
        return redirect("clientes:detalle", pk=cliente.pk)
    return render(request, "core/form.html", {"form": form, "titulo": f"Nuevo vehículo de {cliente.nombre}", "volver": "clientes:lista", "boton": "Guardar vehículo"})


@rol_requerido(ADMIN, RECEPCION)
def vehiculos(request):  # RF-24
    lista_v = Vehiculo.objects.select_related("cliente").annotate(n_ordenes=Count("ordenes"))
    return render(request, "clientes/vehiculos.html", {"vehiculos": lista_v})


@rol_requerido(ADMIN, RECEPCION)
def vehiculo_detalle(request, pk):
    v = get_object_or_404(Vehiculo.objects.select_related("cliente"), pk=pk)
    return render(request, "clientes/vehiculo_detalle.html", {"v": v, "ordenes": v.ordenes.select_related("mecanico")})
