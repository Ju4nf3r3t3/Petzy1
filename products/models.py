from django.db import models
from users.models import Usuario
from django.db.models import Sum, Count, Avg
from django.core.validators import MinValueValidator, MaxValueValidator


class Producto(models.Model):
    """Productos en venta"""
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="productos")
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=100, blank=True)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    @property
    def total_vendidos(self):
        """Calcula la cantidad total vendida de este producto"""
        return self.orderitem_set.aggregate(
            total=Sum('cantidad')
        )['total'] or 0

    @property
    def promedio_rating(self):
        """Calcula el rating promedio del producto"""
        avg = self.reviews.aggregate(promedio=Avg('rating'))['promedio']
        return round(avg, 1) if avg else 0

    @property
    def cantidad_resenas(self):
        """Cuenta la cantidad de reseñas del producto"""
        return self.reviews.count()

    @classmethod
    def mas_vendidos(cls, limite=5):
        """Obtiene los productos más vendidos"""
        return cls.objects.annotate(
            total_vendidos=Sum('orderitem__cantidad')
        ).order_by('-total_vendidos')[:limite]

    @classmethod
    def mas_comentados(cls, limite=5):
        """Obtiene los productos más comentados"""
        return cls.objects.annotate(
            num_resenas=Count('reviews')
        ).order_by('-num_resenas')[:limite]

    @classmethod
    def mejor_calificados(cls, limite=5):
        """Obtiene los productos mejor calificados"""
        return cls.objects.annotate(
            promedio=Avg('reviews__rating')
        ).filter(promedio__isnull=False).order_by('-promedio')[:limite]


class Review(models.Model):
    """Reseñas hechas por usuarios"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="reviews")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['producto', 'usuario']  # Un usuario solo puede reseñar una vez cada producto

    def __str__(self):
        return f"Review de {self.usuario.username} sobre {self.producto.nombre}"

    def estrellas(self):
        """Devuelve la representación en estrellas del rating"""
        return '⭐' * self.rating