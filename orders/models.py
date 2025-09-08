from django.db import models
from users.models import Usuario
from products.models import Producto


class Order(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("pagado", "Pagado"),
        ("enviado", "Enviado"),
        ("cancelado", "Cancelado"),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="orders")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username}"

    def calcular_total(self):
        total = sum(item.subtotal() for item in self.items.all())
        self.total = total
        self.save()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} × {self.producto.nombre}"

    def subtotal(self):
        return self.cantidad * self.precio_unitario


class Payment(models.Model):
    METODOS = [
        ("tarjeta", "Tarjeta de crédito/débito"),
        ("paypal", "PayPal"),
        ("efectivo", "Efectivo"),
    ]
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    metodo = models.CharField(max_length=20, choices=METODOS, default="tarjeta")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de orden #{self.order.id} - {self.estado}"
