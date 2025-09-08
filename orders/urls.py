from django.urls import path
from .views import order_list, checkout, confirm, generar_factura

app_name = "orders"

urlpatterns = [
    path("", order_list, name="list"),
    path("checkout/", checkout, name="checkout"),
    path("confirm/<int:order_id>/", confirm, name="confirm"),
    path("<int:pk>/factura/", generar_factura, name="factura"),
]
