from django.contrib import admin
from .models import Producto, Review


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'vendedor', 'precio', 'stock', 'categoria', 'total_vendidos', 'promedio_rating',
                    'cantidad_resenas']
    list_filter = ['categoria', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'vendedor__username']
    readonly_fields = ['total_vendidos', 'promedio_rating', 'cantidad_resenas']

    def total_vendidos(self, obj):
        return obj.total_vendidos

    total_vendidos.short_description = 'Total Vendidos'

    def promedio_rating(self, obj):
        return obj.promedio_rating

    promedio_rating.short_description = 'Rating Promedio'

    def cantidad_resenas(self, obj):
        return obj.cantidad_resenas

    cantidad_resenas.short_description = 'N° de Reseñas'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['producto', 'usuario', 'rating', 'fecha']
    list_filter = ['rating', 'fecha']
    search_fields = ['producto__nombre', 'usuario__username', 'comentario']

    def rating_estrellas(self, obj):
        return obj.estrellas()

    rating_estrellas.short_description = 'Rating'