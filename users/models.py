from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """Extiende el usuario base de Django"""
    # Más adelante podemos añadir roles (cliente/vendedor/admin)
    pass


class Perfil(models.Model):
    """Datos adicionales del usuario"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="perfil")
    # Ejemplo: dirección, teléfono, foto, etc.

