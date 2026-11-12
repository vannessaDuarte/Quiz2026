from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.roles import ADMIN, CLIENTE, MECANICO, RECEPCION, actor_id, get_actor, rol_actual, rol_requerido
from taller.models import Mecanico

from . import services
from .forms import AsignarForm, DiagnosticoForm, ManoObraForm, OrdenForm, RepuestoOrdenForm
from .models import OrdenTrabajo as O

TODOS = (ADMIN, RECEPCION, MECANICO, CLIENTE)


def _orden_visible(request, orden):
    rol, aid = rol_actual(request), actor_id(request)
    if rol == CLIENTE:
        return orden.vehiculo.cliente_id == aid
    if rol == MECANICO:
        return orden.mecanico_id == aid
    return True


def _cargar(request, pk):
    orden = get_object_or_404(O.objects.select_related("vehiculo__cliente", "mecanico"), pk=pk)
    return orden if _orden_visible(request, orden) else None


def _ejecutar(request, pk, accion, ok=None):
    """Carga la orden, ejecuta la regla de negocio y vuelve al detalle."""
    orden = _cargar(request, pk)
    if orden is None:
        messages.error(request, "No tienes acceso a esa orden.")
        return redirect("ordenes:lista")
    try:
        accion(orden)
        if ok:
            messages.success(request, ok)
    except services.ReglaNegocio as e:
        messages.error(request, str(e))
    return redirect("ordenes:detalle", pk=pk)


@rol_requerido(*TODOS)
def lista(request):
    rol, aid = rol_actual(request), actor_id(request)
    qs = O.objects.select_related("vehiculo__cliente", "mecanico")
    if rol == CLIENTE:  # RF-11
        qs = qs.filter(vehiculo__cliente_id=aid)
    elif rol == MECANICO:
        qs = qs.filter(mecanico_id=aid)
    estado = request.GET.get("estado", "")
    if estado:
        qs = qs.filter(estado=estado)
    return render(request, "ordenes/lista.html", {"ordenes": qs, "estados": O.ESTADOS, "estado_sel": estado})


@rol_requerido(ADMIN, RECEPCION)
def nueva(request):
    form = OrdenForm(request.POST or None, initial={"vehiculo": request.GET.get("vehiculo")})
    if request.method == "POST" and form.is_valid():
        orden = services.crear_orden(form.cleaned_data["vehiculo"], form.cleaned_data["problema"])
        messages.success(request, f"Orden #{orden.pk} registrada como 'Recibido'.")
        return redirect("ordenes:detalle", pk=orden.pk)
    return render(request, "core/form.html", {"form": form, "titulo": "Nueva orden de trabajo", "volver": "ordenes:lista", "boton": "Registrar orden"})


@rol_requerido(*TODOS)
def detalle(request, pk):
    orden = _cargar(request, pk)
    if orden is None:
        messages.error(request, "No tienes acceso a esa orden.")
        return redirect("ordenes:lista")
    rol = rol_actual(request)
    ctx = {
        "orden": orden,
        "repuestos": orden.repuestos.select_related("repuesto"),
        "mano_obra": orden.mano_obra.all(),
        "factura": getattr(orden, "factura", None),
    }
    if rol == ADMIN and orden.estado in services.ESTADOS_ASIGNABLES:
        libres = [m for m in Mecanico.objects.filter(activo=True) if m.libre and m.pk != orden.mecanico_id]
        ctx["asignar_form"] = AsignarForm(libres=libres)
        ctx["hay_libres"] = bool(libres)
        ctx["mecanico_ocupado"] = bool(orden.mecanico) and not orden.mecanico.libre
    if rol == MECANICO:
        if orden.estado == O.DIAGNOSTICO:
            ctx["diag_form"] = DiagnosticoForm(initial={"diagnostico": orden.diagnostico})
        if orden.estado in services.ESTADOS_EDITABLES:
            ctx["repuesto_form"] = RepuestoOrdenForm()
            ctx["mano_form"] = ManoObraForm()
        sig = services.TRANSICIONES_MECANICO.get(orden.estado)
        if sig:
            ctx["siguiente"] = (sig, dict(O.ESTADOS)[sig])
    return render(request, "ordenes/detalle.html", ctx)


@require_POST
@rol_requerido(ADMIN)
def asignar(request, pk):
    def accion(orden):
        libres = [m for m in Mecanico.objects.filter(activo=True) if m.libre]
        form = AsignarForm(request.POST, libres=libres)
        if not form.is_valid():
            raise services.ReglaNegocio("Elige un mecánico libre.")
        services.asignar_mecanico(orden, form.cleaned_data["mecanico"])

    return _ejecutar(request, pk, accion, "Mecánico asignado y notificado.")


@require_POST
@rol_requerido(MECANICO)
def diagnostico(request, pk):
    def accion(orden):
        form = DiagnosticoForm(request.POST)
        if not form.is_valid():
            raise services.ReglaNegocio("Escribe el diagnóstico.")
        services.guardar_diagnostico(orden, form.cleaned_data["diagnostico"])

    return _ejecutar(request, pk, accion, "Diagnóstico guardado.")


@require_POST
@rol_requerido(MECANICO)
def repuesto(request, pk):
    def accion(orden):
        form = RepuestoOrdenForm(request.POST)
        if not form.is_valid():
            raise services.ReglaNegocio("Revisa el repuesto y la cantidad.")
        services.registrar_repuesto(orden, form.cleaned_data["repuesto"], form.cleaned_data["cantidad"])

    return _ejecutar(request, pk, accion, "Repuesto registrado y descontado del stock.")


@require_POST
@rol_requerido(MECANICO)
def mano_obra(request, pk):
    def accion(orden):
        form = ManoObraForm(request.POST)
        if not form.is_valid():
            raise services.ReglaNegocio("Revisa los datos de la mano de obra.")
        d = form.cleaned_data
        services.registrar_mano_obra(orden, d["descripcion"], d["horas"], d["valor_hora"])

    return _ejecutar(request, pk, accion, "Mano de obra registrada.")


@require_POST
@rol_requerido(MECANICO)
def enviar(request, pk):
    return _ejecutar(request, pk, services.enviar_al_cliente, "Orden enviada al cliente; quedó esperando su aprobación.")


@require_POST
@rol_requerido(CLIENTE)
def decidir_view(request, pk):
    aprobar = request.POST.get("decision") == "aprobar"
    return _ejecutar(
        request, pk, lambda o: services.decidir(o, aprobar),
        "Aprobaste la orden. ¡Gracias!" if aprobar else "Rechazaste la orden.",
    )


@require_POST
@rol_requerido(RECEPCION)
def generar_reparacion(request, pk):
    return _ejecutar(request, pk, services.generar_orden_reparacion, "Orden de reparación generada; se avisó al administrador.")


@require_POST
@rol_requerido(MECANICO)
def cambiar_estado(request, pk):
    nuevo = request.POST.get("estado")
    mecanico = get_actor(request)
    return _ejecutar(request, pk, lambda o: services.cambiar_estado_mecanico(o, mecanico, nuevo), "Estado actualizado.")


@require_POST
@rol_requerido(ADMIN)
def eliminar(request, pk):
    orden = _cargar(request, pk)
    try:
        services.eliminar_orden(orden)
    except services.ReglaNegocio as e:
        messages.error(request, str(e))
        return redirect("ordenes:detalle", pk=pk)
    messages.success(request, "Orden eliminada.")
    return redirect("ordenes:lista")
