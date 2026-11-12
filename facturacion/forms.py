from django import forms

from core.forms import BSModelForm

from .models import Factura


class FacturaForm(BSModelForm):
    class Meta:
        model = Factura
        fields = ["tipo", "descuento_pct"]
        widgets = {"descuento_pct": forms.NumberInput(attrs={"min": 0, "max": 100})}

    def clean_descuento_pct(self):
        v = self.cleaned_data["descuento_pct"]
        if v > 100:
            raise forms.ValidationError("El descuento no puede superar 100%.")
        return v
