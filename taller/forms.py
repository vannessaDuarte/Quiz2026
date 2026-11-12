from core.forms import BSModelForm

from .models import Mecanico, Proveedor, Repuesto


class MecanicoForm(BSModelForm):
    class Meta:
        model = Mecanico
        fields = ["nombre", "telefono", "activo"]


class ProveedorForm(BSModelForm):
    class Meta:
        model = Proveedor
        fields = ["nombre", "rut", "telefono", "email"]


class RepuestoForm(BSModelForm):
    class Meta:
        model = Repuesto
        fields = ["codigo", "nombre", "proveedor", "precio", "stock", "stock_minimo"]
