from django import forms


class BSMixin:
    """Agrega clases de Bootstrap a todos los campos."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            w = campo.widget
            if isinstance(w, (forms.Select, forms.SelectMultiple)):
                clase = "form-select"
            elif isinstance(w, forms.CheckboxInput):
                clase = "form-check-input"
            else:
                clase = "form-control"
            w.attrs["class"] = (w.attrs.get("class", "") + " " + clase).strip()


class BSForm(BSMixin, forms.Form):
    pass


class BSModelForm(BSMixin, forms.ModelForm):
    pass
