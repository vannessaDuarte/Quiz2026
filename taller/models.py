from django.db import models


class Mecanico(models.Model):
    nombre = models.CharField(max_length=150)
    telefono = models.CharField("Teléfono", max_length=30, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    @property
    def libre(self):
        """Libre = activo y sin órdenes en diagnóstico o reparación."""
        from ordenes.models import OrdenTrabajo

        if not self.activo:
            return False
        return not self.ordenes.filter(
            estado__in=[OrdenTrabajo.DIAGNOSTICO, OrdenTrabajo.EN_REPARACION]
        ).exists()


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    rut = models.CharField("RUT", max_length=12, blank=True)
    telefono = models.CharField("Teléfono", max_length=30, blank=True)
    email = models.EmailField("Correo", blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.nombre


class Repuesto(models.Model):
    codigo = models.CharField("Código", max_length=40, unique=True)
    nombre = models.CharField(max_length=150)
    proveedor = models.ForeignKey(
        Proveedor, null=True, blank=True, on_delete=models.SET_NULL, related_name="repuestos"
    )
    precio = models.PositiveIntegerField("Precio unitario (CLP)", default=0)
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField("Stock mínimo", default=3)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def bajo_stock(self):
        return self.stock <= self.stock_minimo


class Notificacion(models.Model):
    """Notificación interna dirigida a un rol (y a un mecánico/cliente concreto si aplica)."""

    destino = models.CharField(max_length=20, db_index=True)  # admin | recepcion | mecanico | cliente
    mecanico = models.ForeignKey(Mecanico, null=True, blank=True, on_delete=models.CASCADE)
    cliente = models.ForeignKey("clientes.Cliente", null=True, blank=True, on_delete=models.CASCADE)
    orden = models.ForeignKey("ordenes.OrdenTrabajo", null=True, blank=True, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=300)
    leida = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creada"]
        verbose_name_plural = "notificaciones"

    def __str__(self):
        return f"[{self.destino}] {self.mensaje}"
