from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    rut = models.CharField("RUT", max_length=12, unique=True)
    telefono = models.CharField("Teléfono", max_length=30, blank=True)
    email = models.EmailField("Correo", blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class Vehiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="vehiculos")
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=60)
    anio = models.PositiveSmallIntegerField("Año", null=True, blank=True)
    color = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["patente"]

    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"
