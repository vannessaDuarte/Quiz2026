from decimal import Decimal

from django.db import models


class OrdenTrabajo(models.Model):
    RECIBIDO = "recibido"
    DIAGNOSTICO = "diagnostico"
    ESPERANDO = "esperando_aprobacion"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    POR_REPARAR = "por_reparar"
    EN_REPARACION = "en_reparacion"
    LISTO = "listo_retiro"

    ESTADOS = [
        (RECIBIDO, "Recibido"),
        (DIAGNOSTICO, "En diagnóstico"),
        (ESPERANDO, "Esperando aprobación del cliente"),
        (APROBADA, "Aprobada por el cliente"),
        (RECHAZADA, "Rechazada por el cliente"),
        (POR_REPARAR, "Orden de reparación generada"),
        (EN_REPARACION, "En reparación"),
        (LISTO, "Listo para retiro"),
    ]
    COLORES = {
        RECIBIDO: "secondary",
        DIAGNOSTICO: "info",
        ESPERANDO: "warning",
        APROBADA: "success",
        RECHAZADA: "danger",
        POR_REPARAR: "primary",
        EN_REPARACION: "primary",
        LISTO: "success",
    }

    vehiculo = models.ForeignKey("clientes.Vehiculo", on_delete=models.PROTECT, related_name="ordenes")
    problema = models.TextField("Problema informado por el cliente")
    estado = models.CharField(max_length=30, choices=ESTADOS, default=RECIBIDO, db_index=True)
    fecha_recepcion = models.DateTimeField("Fecha de recepción", auto_now_add=True)
    mecanico = models.ForeignKey(
        "taller.Mecanico", null=True, blank=True, on_delete=models.SET_NULL, related_name="ordenes"
    )
    diagnostico = models.TextField(blank=True)
    enviada_en = models.DateTimeField(null=True, blank=True)
    decision_en = models.DateTimeField(null=True, blank=True)
    stock_devuelto = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_recepcion"]
        verbose_name = "orden de trabajo"
        verbose_name_plural = "órdenes de trabajo"

    def __str__(self):
        return f"Orden #{self.pk} - {self.vehiculo.patente}"

    @property
    def cliente(self):
        return self.vehiculo.cliente

    @property
    def color(self):
        return self.COLORES.get(self.estado, "secondary")

    @property
    def total_repuestos(self):
        return sum(d.subtotal for d in self.repuestos.all())

    @property
    def total_mano_obra(self):
        return sum(m.subtotal for m in self.mano_obra.all())

    @property
    def neto(self):
        return self.total_repuestos + self.total_mano_obra


class DetalleRepuesto(models.Model):
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="repuestos")
    repuesto = models.ForeignKey("taller.Repuesto", on_delete=models.PROTECT, related_name="usos")
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.PositiveIntegerField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado"]

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


class ManoObra(models.Model):
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="mano_obra")
    descripcion = models.CharField("Descripción", max_length=200)
    horas = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.0"))
    valor_hora = models.PositiveIntegerField("Valor por hora (CLP)", default=15000)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado"]
        verbose_name = "mano de obra"
        verbose_name_plural = "mano de obra"

    @property
    def subtotal(self):
        return int(self.horas * self.valor_hora)
