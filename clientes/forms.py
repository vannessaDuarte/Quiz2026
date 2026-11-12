from core.forms import BSModelForm

from .models import Cliente, Vehiculo


class ClienteForm(BSModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "rut", "telefono", "email"]


class VehiculoForm(BSModelForm):
    class Meta:
        model = Vehiculo
        fields = ["patente", "marca", "modelo", "anio", "color"]

    def clean_patente(self):
        return self.cleaned_data["patente"].upper().replace(" ", "").replace("-", "")
