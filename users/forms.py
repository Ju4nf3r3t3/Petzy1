from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejorar los placeholders y estilos
        self.fields['username'].widget.attrs.update({'placeholder': 'Nombre de usuario'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Correo electrónico'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirmar contraseña'})