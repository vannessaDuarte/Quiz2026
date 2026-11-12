from django import forms

from clientes.models import Vehiculo
from core.forms import BSForm, BSModelForm
from taller.models import Mecanico, Repuesto

from .models import ManoObra


class OrdenForm(BSForm):
    vehiculo = forms.ModelChoiceField(queryset=Vehiculo.objects.select_related("cliente"), label="Vehículo")
    problema = forms.CharField(label="Problema informado", widget=forms.Textarea(attrs={"rows": 3}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vehiculo"].label_from_instance = lambda v: f"{v.patente} - {v.marca} {v.modelo} ({v.cliente.nombre})"


class AsignarForm(BSForm):
    mecanico = forms.ModelChoiceField(queryset=Mecanico.objects.none(), label="Mecánico libre", empty_label="Elige un mecánico libre")

    def __init__(self, *args, libres=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["mecanico"].queryset = Mecanico.objects.filter(pk__in=[m.pk for m in (libres or [])])


class DiagnosticoForm(BSForm):
    diagnostico = forms.CharField(label="Diagnóstico", widget=forms.Textarea(attrs={"rows": 4}))


class RepuestoOrdenForm(BSForm):
    repuesto = forms.ModelChoiceField(queryset=Repuesto.objects.filter(stock__gt=0), label="Repuesto")
    cantidad = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["repuesto"].queryset = Repuesto.objects.filter(stock__gt=0)
        self.fields["repuesto"].label_from_instance = lambda r: f"{r.nombre} (stock {r.stock})"


class ManoObraForm(BSModelForm):
    class Meta:
        model = ManoObra
        fields = ["descripcion", "horas", "valor_hora"]
