from django.db import models
from users.models import Usuario

class Producto(models.Model):
    """Productos en venta"""
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="productos")
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=100, blank=True)  # simple por ahora

    def __str__(self):
        return self.nombre


class Review(models.Model):
    """Reseñas hechas por usuarios"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="reviews")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(default=5)  # 1 a 5 estrellas
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review de {self.usuario.username} sobre {self.producto.nombre}"