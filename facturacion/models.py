from django.db import models

IVA_PCT = 19


class Factura(models.Model):
    BOLETA = "boleta"
    FACTURA = "factura"
    TIPOS = [(BOLETA, "Boleta"), (FACTURA, "Factura")]

    orden = models.OneToOneField(
        "ordenes.OrdenTrabajo", on_delete=models.PROTECT, related_name="factura"
    )
    tipo = models.CharField(max_length=10, choices=TIPOS, default=BOLETA)
    numero = models.PositiveIntegerField(unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    neto = models.PositiveIntegerField()
    descuento_pct = models.PositiveSmallIntegerField("Descuento (%)", default=0)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.get_tipo_display()} N° {self.numero}"

    @property
    def monto_descuento(self):
        return self.neto * self.descuento_pct // 100

    @property
    def base(self):
        return self.neto - self.monto_descuento

    @property
    def iva(self):
        return round(self.base * IVA_PCT / 100)

    @property
    def total(self):
        return self.base + self.iva
