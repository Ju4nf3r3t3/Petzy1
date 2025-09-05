from django.contrib import admin
from .models import Order, OrderItem, Payment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario")  # agrega estado y total después
    search_fields = ("usuario__username",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "producto")
    search_fields = ("order__id", "producto__id")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order",)  # agrega estado y monto después
