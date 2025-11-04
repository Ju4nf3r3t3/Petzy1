from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejorar los placeholders y estilos
        base_classes = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        self.fields['username'].widget.attrs.update({
            'placeholder': _('Nombre de usuario'),
            'class': base_classes,
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': _('Correo electrónico'),
            'class': base_classes,
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': _('Contraseña'),
            'class': base_classes,
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': _('Confirmar contraseña'),
            'class': base_classes,
        })