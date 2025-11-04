from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cart.models import Cart, CartItem
from orders.models import Order
from products.models import Producto


class CheckoutViewTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.customer = self.User.objects.create_user(
            username="cliente",
            email="cliente@example.com",
            password="pass1234",
            first_name="Cliente",
            last_name="Demo",
        )
        self.seller = self.User.objects.create_user(
            username="vendedor",
            email="vendedor@example.com",
            password="pass1234",
        )
        self.producto = Producto.objects.create(
            vendedor=self.seller,
            nombre="Collar inteligente",
            descripcion="Descripción de prueba",
            precio=Decimal("25.00"),
            stock=10,
        )

        self.cart = Cart.objects.create(usuario=self.customer)
        CartItem.objects.create(cart=self.cart, producto=self.producto, cantidad=2)

    def test_checkout_page_contains_csrf_token(self):
        self.client.login(username="cliente", password="pass1234")
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrfmiddlewaretoken", response.content.decode())

    def test_successful_checkout_creates_order_and_clears_cart(self):
        self.client.login(username="cliente", password="pass1234")
        payload = {
            "email": "cliente@example.com",
            "nombre": "Cliente Demo",
            "telefono": "3001234567",
            "ciudad": "Medellín",
            "direccion": "Calle 123 #45-67",
            "metodo_pago": "tarjeta",
            "numero_tarjeta": "4111111111111111",
            "expiracion": "12/30",
            "cvv": "123",
        }

        response = self.client.post(reverse("orders:checkout"), payload)
        self.assertEqual(response.status_code, 302)

        order = Order.objects.get(usuario=self.customer)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, Decimal("50.00"))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 8)
        self.assertFalse(self.cart.items.exists())
        self.assertTrue(response.url.endswith(reverse("orders:confirm", args=[order.id])))

    def test_checkout_with_missing_card_data_shows_errors(self):
        self.client.login(username="cliente", password="pass1234")
        payload = {
            "email": "cliente@example.com",
            "nombre": "Cliente Demo",
            "telefono": "3001234567",
            "ciudad": "Medellín",
            "direccion": "Calle 123 #45-67",
            "metodo_pago": "tarjeta",
            # Falta información de tarjeta deliberadamente
        }

        response = self.client.post(reverse("orders:checkout"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo es obligatorio para pagos con tarjeta.")
        self.assertEqual(Order.objects.count(), 0)
        self.assertTrue(self.cart.items.exists())
