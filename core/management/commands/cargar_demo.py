from django.core.management.base import BaseCommand

from clientes.models import Cliente, Vehiculo
from taller.models import Mecanico, Proveedor, Repuesto


class Command(BaseCommand):
    help = "Carga datos de ejemplo (solo si la base está vacía)."

    def handle(self, *args, **options):
        if Cliente.objects.exists() or Mecanico.objects.exists():
            self.stdout.write("Ya hay datos; no se carga nada.")
            return
        c1 = Cliente.objects.create(nombre="María González", rut="12.345.678-5", telefono="+56 9 1111 1111", email="maria@example.com")
        c2 = Cliente.objects.create(nombre="Pedro Soto", rut="9.876.543-2", telefono="+56 9 2222 2222", email="pedro@example.com")
        Vehiculo.objects.create(cliente=c1, patente="ABCD12", marca="Toyota", modelo="Yaris", anio=2018, color="Rojo")
        Vehiculo.objects.create(cliente=c1, patente="WXYZ34", marca="Suzuki", modelo="Swift", anio=2020, color="Gris")
        Vehiculo.objects.create(cliente=c2, patente="HJKL56", marca="Chevrolet", modelo="Sail", anio=2016, color="Blanco")
        for n in ("Juan Pérez", "Luis Rojas", "Andrés Silva"):
            Mecanico.objects.create(nombre=n)
        p1 = Proveedor.objects.create(nombre="Repuestos del Norte", rut="76.111.222-3", telefono="+56 51 222 0000")
        p2 = Proveedor.objects.create(nombre="AutoPartes Coquimbo", rut="77.333.444-5", telefono="+56 51 333 0000")
        datos = [
            ("FIL-001", "Filtro de aceite", p1, 6000, 20, 5),
            ("PAS-014", "Pastillas de freno delanteras", p1, 28000, 8, 3),
            ("BUJ-004", "Bujía", p2, 4500, 30, 8),
            ("BAT-060", "Batería 60Ah", p2, 85000, 4, 2),
            ("ACE-5W30", "Aceite 5W30 (litro)", p2, 9000, 40, 10),
        ]
        for cod, nom, prov, precio, stock, minimo in datos:
            Repuesto.objects.create(codigo=cod, nombre=nom, proveedor=prov, precio=precio, stock=stock, stock_minimo=minimo)
        self.stdout.write(self.style.SUCCESS("Datos de ejemplo cargados."))
