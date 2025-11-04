from django import forms
from django.utils.translation import gettext_lazy as _


class CheckoutForm(forms.Form):
    email = forms.EmailField(label=_("Correo electrónico"))
    nombre = forms.CharField(label=_("Nombre completo"), max_length=150)
    telefono = forms.CharField(label=_("Teléfono"), max_length=30)
    ciudad = forms.CharField(label=_("Ciudad"), max_length=80)
    direccion = forms.CharField(
        label=_("Dirección"),
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    metodo_pago = forms.ChoiceField(
        label=_("Método de pago"),
        choices=(
            ("tarjeta", _("Tarjeta de crédito/débito")),
            ("paypal", "PayPal"),
        ),
        widget=forms.RadioSelect,
        initial="tarjeta",
    )
    numero_tarjeta = forms.CharField(
        label=_("Número de tarjeta"),
        max_length=32,
        required=False,
    )
    expiracion = forms.CharField(
        label=_("Fecha de expiración"),
        max_length=7,
        required=False,
    )
    cvv = forms.CharField(
        label=_("CVV"),
        max_length=4,
        required=False,
    )

    CARD_REQUIRED_ERROR = _("Este campo es obligatorio para pagos con tarjeta.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_input_classes = (
            "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none "
            "focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        )

        placeholders = {
            "email": "tu@email.com",
            "numero_tarjeta": "1234 5678 9012 3456",
            "expiracion": "MM/AA",
            "cvv": "123",
        }

        for field_name in [
            "email",
            "nombre",
            "telefono",
            "ciudad",
            "numero_tarjeta",
            "expiracion",
            "cvv",
        ]:
            field = self.fields[field_name]
            field.widget.attrs.setdefault("class", base_input_classes)
            placeholder = placeholders.get(field_name, field.label)
            if placeholder:
                field.widget.attrs.setdefault("placeholder", placeholder)

        direccion_field = self.fields["direccion"]
        direccion_field.widget.attrs.setdefault("class", base_input_classes)
        direccion_field.widget.attrs.setdefault("placeholder", direccion_field.label)

        self.fields["metodo_pago"].widget.attrs.setdefault("class", "space-y-2")

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get("metodo_pago")
        if metodo == "tarjeta":
            missing_fields = [
                name
                for name in ("numero_tarjeta", "expiracion", "cvv")
                if not cleaned_data.get(name)
            ]
            for name in missing_fields:
                self.add_error(name, self.CARD_REQUIRED_ERROR)
        return cleaned_data
