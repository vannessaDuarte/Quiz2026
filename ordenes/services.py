"""Reglas de negocio del flujo de una orden de trabajo."""
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from facturacion.services import crear_factura
from taller.models import Repuesto
from taller.services import notificar

from .models import DetalleRepuesto, ManoObra, OrdenTrabajo as O


class ReglaNegocio(Exception):
    """Error que se muestra tal cual al usuario."""


ESTADOS_ASIGNABLES = (O.RECIBIDO, O.DIAGNOSTICO, O.APROBADA, O.POR_REPARAR)
ESTADOS_EDITABLES = (O.DIAGNOSTICO, O.EN_REPARACION)
TRANSICIONES_MECANICO = {O.POR_REPARAR: O.EN_REPARACION, O.EN_REPARACION: O.LISTO}


def crear_orden(vehiculo, problema):
    """RF-03: orden en estado 'recibido' con fecha de recepción automática."""
    orden = O.objects.create(vehiculo=vehiculo, problema=problema)
    notificar("admin", f"Nueva orden #{orden.pk} ({vehiculo.patente}) pendiente de asignar mecánico.", orden=orden)
    return orden


@transaction.atomic
def asignar_mecanico(orden, mecanico):
    """RF-04 (asignar mecánico libre) y RF-16 (reasignar)."""
    if orden.estado not in ESTADOS_ASIGNABLES:
        raise ReglaNegocio("En este estado ya no se puede asignar o reasignar mecánico.")
    if mecanico.pk == orden.mecanico_id:
        raise ReglaNegocio("Ese mecánico ya está asignado a la orden.")
    if not mecanico.libre:
        raise ReglaNegocio(f"{mecanico} no está libre.")
    anterior = orden.mecanico
    es_primera = orden.estado == O.RECIBIDO
    orden.mecanico = mecanico
    if es_primera:
        orden.estado = O.DIAGNOSTICO
    orden.save()
    if es_primera:
        msg = f"Se te asignó la orden #{orden.pk} ({orden.vehiculo}) para diagnóstico."
    else:
        msg = f"Se te reasignó la orden #{orden.pk} ({orden.vehiculo})."
    notificar("mecanico", msg, orden=orden, mecanico=mecanico)  # RF-05
    if anterior:
        notificar("mecanico", f"La orden #{orden.pk} fue reasignada a otro mecánico.", orden=orden, mecanico=anterior)


def guardar_diagnostico(orden, texto):
    if orden.estado != O.DIAGNOSTICO:
        raise ReglaNegocio("El diagnóstico solo se registra mientras la orden está en diagnóstico.")
    orden.diagnostico = texto
    orden.save(update_fields=["diagnostico"])


@transaction.atomic
def registrar_repuesto(orden, repuesto, cantidad):
    """RF-07 / RF-18 / RF-19 / RF-20: registra el repuesto, descuenta stock y alerta si queda bajo."""
    if orden.estado not in ESTADOS_EDITABLES:
        raise ReglaNegocio("No se pueden registrar repuestos en este estado.")
    if cantidad < 1:
        raise ReglaNegocio("La cantidad debe ser al menos 1.")
    rep = Repuesto.objects.select_for_update().get(pk=repuesto.pk)
    if rep.stock < cantidad:
        raise ReglaNegocio(f"Stock insuficiente de {rep.nombre}: quedan {rep.stock}.")
    rep.stock -= cantidad
    rep.save(update_fields=["stock"])
    DetalleRepuesto.objects.create(orden=orden, repuesto=rep, cantidad=cantidad, precio_unitario=rep.precio)
    if rep.stock <= rep.stock_minimo:
        notificar("admin", f"Stock bajo de {rep.nombre}: quedan {rep.stock} (mínimo {rep.stock_minimo}).", orden=orden)


def registrar_mano_obra(orden, descripcion, horas, valor_hora):
    """RF-08"""
    if orden.estado not in ESTADOS_EDITABLES:
        raise ReglaNegocio("No se puede registrar mano de obra en este estado.")
    return ManoObra.objects.create(orden=orden, descripcion=descripcion, horas=horas, valor_hora=valor_hora)


def enviar_al_cliente(orden):
    """RF-09 y RF-10: envía el detalle al cliente y pasa a 'esperando aprobación'."""
    if orden.estado != O.DIAGNOSTICO:
        raise ReglaNegocio("Solo se puede enviar una orden que esté en diagnóstico.")
    if not orden.diagnostico.strip():
        raise ReglaNegocio("Falta registrar el diagnóstico.")
    if not (orden.repuestos.exists() or orden.mano_obra.exists()):
        raise ReglaNegocio("Registra al menos un repuesto o mano de obra antes de enviar.")
    orden.estado = O.ESPERANDO
    orden.enviada_en = timezone.now()
    orden.save(update_fields=["estado", "enviada_en"])
    cliente = orden.cliente
    notificar(
        "cliente",
        f"Tu orden #{orden.pk} ({orden.vehiculo.patente}) tiene un presupuesto de ${orden.neto:,} + IVA. Revísala y apruébala o recházala.".replace(",", "."),
        orden=orden,
        cliente=cliente,
    )
    if cliente.email:
        detalle = "\n".join(f"- {d.cantidad} x {d.repuesto.nombre}: ${d.subtotal}" for d in orden.repuestos.all())
        detalle += "\n" + "\n".join(f"- {m.descripcion} ({m.horas} h): ${m.subtotal}" for m in orden.mano_obra.all())
        send_mail(
            f"Orden de trabajo #{orden.pk} - {orden.vehiculo.patente}",
            f"Hola {cliente.nombre},\n\nDiagnóstico: {orden.diagnostico}\n\nDetalle:\n{detalle}\n\nTotal neto: ${orden.neto}",
            None,
            [cliente.email],
            fail_silently=True,
        )


@transaction.atomic
def decidir(orden, aprobar):
    """RF-12 y RF-13: el cliente aprueba o rechaza; se notifica a recepción y administrador."""
    if orden.estado != O.ESPERANDO:
        raise ReglaNegocio("Esta orden no está esperando tu aprobación.")
    orden.decision_en = timezone.now()
    if aprobar:
        orden.estado = O.APROBADA
        texto = "APROBÓ"
    else:
        orden.estado = O.RECHAZADA
        texto = "RECHAZÓ"
        _devolver_stock(orden)
    orden.save()
    msg = f"{orden.cliente.nombre} {texto} la orden #{orden.pk} ({orden.vehiculo.patente})."
    notificar("recepcion", msg, orden=orden)
    notificar("admin", msg, orden=orden)


def _devolver_stock(orden):
    if orden.stock_devuelto:
        return
    for d in orden.repuestos.all():
        Repuesto.objects.filter(pk=d.repuesto_id).update(stock=F("stock") + d.cantidad)
    orden.stock_devuelto = True
    orden.save(update_fields=["stock_devuelto"])


@transaction.atomic
def generar_orden_reparacion(orden):
    """RF-14: la recepcionista genera la orden de reparación y se avisa al administrador."""
    if orden.estado != O.APROBADA:
        raise ReglaNegocio("Solo se puede generar la orden de reparación cuando el cliente aprobó.")
    if not orden.mecanico:
        raise ReglaNegocio("La orden no tiene mecánico asignado.")
    orden.estado = O.POR_REPARAR
    orden.save(update_fields=["estado"])
    aviso = "" if orden.mecanico.libre else f" Atención: {orden.mecanico} no está libre, puede requerir reasignación."
    notificar("admin", f"Orden #{orden.pk} lista para reparar (mecánico: {orden.mecanico}).{aviso}", orden=orden)
    notificar("mecanico", f"La orden #{orden.pk} ({orden.vehiculo}) fue aprobada; puedes iniciar la reparación.", orden=orden, mecanico=orden.mecanico)


@transaction.atomic
def cambiar_estado_mecanico(orden, mecanico, nuevo):
    """RF-17 (+ RF-21: al quedar listo se genera la boleta/factura)."""
    if orden.mecanico_id != mecanico.pk:
        raise ReglaNegocio("Esta orden no está asignada a ti.")
    if TRANSICIONES_MECANICO.get(orden.estado) != nuevo:
        raise ReglaNegocio("Ese cambio de estado no es válido para esta orden.")
    orden.estado = nuevo
    orden.save(update_fields=["estado"])
    if nuevo == O.LISTO:
        factura = crear_factura(orden)
        notificar("cliente", f"Tu vehículo {orden.vehiculo.patente} está listo para retiro ({factura}).", orden=orden, cliente=orden.cliente)
        notificar("recepcion", f"Orden #{orden.pk} ({orden.vehiculo.patente}) lista para retiro.", orden=orden)


@transaction.atomic
def eliminar_orden(orden):
    """RF-30: borra la orden (devuelve el stock si no se había devuelto)."""
    if hasattr(orden, "factura"):
        raise ReglaNegocio("No se puede borrar una orden que ya tiene boleta/factura.")
    _devolver_stock(orden)
    orden.delete()
