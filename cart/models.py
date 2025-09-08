from django.db import models
from users.models import Usuario
from products.models import Producto


class Cart(models.Model):
    """Carrito asociado a un usuario"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="cart")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class CartItem(models.Model):
    """Item dentro del carrito"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} × {self.producto.nombre}"

    def subtotal(self):
        return self.producto.precio * self.cantidad

