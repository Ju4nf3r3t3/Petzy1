from django.contrib import admin
from .models import Producto, Review

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "precio", "stock", "vendedor")
    search_fields = ("nombre", "vendedor__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("producto", "usuario", "rating", "fecha")
    search_fields = ("producto__nombre", "usuario__username")
    list_filter = ("rating", "fecha")