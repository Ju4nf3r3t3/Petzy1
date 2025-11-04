from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Producto


class ProductosAPITestCase(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
            password="12345pass",
        )
        Producto.objects.create(
            vendedor=usuario,
            nombre="Collar luminoso",
            descripcion="Ideal para paseos nocturnos",
            precio=Decimal("49.990"),
            stock=10,
            categoria="Accesorios",
        )

    def test_productos_disponibles_api(self):
        url = reverse('products:api_available')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('results', payload)
        self.assertEqual(payload['count'], len(payload['results']))
        self.assertGreaterEqual(payload['count'], 1)
        first = payload['results'][0]
        self.assertIn('detail_url', first)
        self.assertIn('/products/', first['detail_url'])
