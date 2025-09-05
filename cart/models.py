from django.db import models
from users.models import Usuario
from products.models import Producto

class Cart(models.Model):
    """Carrito asociado a un usuario"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="cart")
    # total, creado_en, actualizado_en


class CartItem(models.Model):
    """Item dentro del carrito"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    # cantidad
