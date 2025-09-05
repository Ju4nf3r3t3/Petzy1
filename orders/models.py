from django.db import models
from users.models import Usuario
from products.models import Producto

class Order(models.Model):
    """Pedido realizado por un usuario"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="orders")
    # estado, fecha, total


class OrderItem(models.Model):
    """Detalle de productos en un pedido"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    # cantidad, precio_unitario


class Payment(models.Model):
    """Pago asociado a un pedido"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    # método, monto, estado, fecha
