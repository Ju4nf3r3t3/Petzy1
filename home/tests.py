from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from home.services import (
    DatabaseFeaturedProductsProvider,
    FeaturedProduct,
    StaticFeaturedProductsProvider,
    get_featured_provider,
)
from products.models import Producto


class FeaturedProductsProviderTests(TestCase):
    def test_get_featured_provider_returns_static_when_no_products(self):
        provider = get_featured_provider()
        self.assertIsInstance(provider, StaticFeaturedProductsProvider)
        self.assertGreaterEqual(len(provider.get_featured()), 1)

    def test_static_provider_returns_configured_items(self):
        items = [
            FeaturedProduct(
                name="Kit", description="Desc", price="10", url="#"
            )
        ]
        provider = StaticFeaturedProductsProvider(items)
        result = provider.get_featured()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Kit")

    def test_get_featured_provider_prefers_database_when_available(self):
        usuario = get_user_model().objects.create_user(
            username="featured",
            email="featured@example.com",
            password="pass12345",
        )
        Producto.objects.create(
            vendedor=usuario,
            nombre="Cama ortopédica",
            descripcion="Máximo confort",
            precio=Decimal("199.990"),
            stock=3,
            categoria="Descanso",
        )

        provider = get_featured_provider()
        self.assertIsInstance(provider, DatabaseFeaturedProductsProvider)
        destacados = provider.get_featured()
        self.assertGreaterEqual(len(destacados), 1)
        self.assertTrue(any(item.name == "Cama ortopédica" for item in destacados))
