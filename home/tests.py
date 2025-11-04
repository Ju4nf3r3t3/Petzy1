from decimal import Decimal

from django.contrib.auth import get_user_model
import tempfile
from pathlib import Path

from django.test import SimpleTestCase, TestCase

from home.services import (
    DatabaseFeaturedProductsProvider,
    FeaturedProduct,
    StaticFeaturedProductsProvider,
    get_featured_provider,
)
from home.utils import format_cop
from home.utils.i18n import ensure_compiled_catalogs
from products.models import Producto


class FeaturedProductsProviderTests(TestCase):
    def test_get_featured_provider_returns_static_when_no_products(self):
        provider = get_featured_provider()
        self.assertIsInstance(provider, StaticFeaturedProductsProvider)
        self.assertGreaterEqual(len(provider.get_featured()), 1)

    def test_static_provider_returns_configured_items(self):
        items = [
            FeaturedProduct(
                name="Kit", description="Desc", price=Decimal("10"), url="#"
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


class TranslationCompilationTests(SimpleTestCase):
    def test_compiles_missing_catalog_on_demand(self):
        with tempfile.TemporaryDirectory() as tmp:
            locale_root = Path(tmp)
            po_dir = locale_root / "en" / "LC_MESSAGES"
            po_dir.mkdir(parents=True)

            po_dir.joinpath("django.po").write_text(
                'msgid ""\n'
                'msgstr ""\n'
                '"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
                'msgid "Hola"\n'
                'msgstr "Hello"\n',
                encoding="utf-8",
            )

            ensure_compiled_catalogs(
                force=True,
                locale_dirs=[locale_root],
                languages=["en"],
            )

            compiled = po_dir / "django.mo"
            self.assertTrue(compiled.exists())
            self.assertGreater(compiled.stat().st_size, 0)


class CurrencyFormatTests(SimpleTestCase):
    def test_formats_integer_amounts(self):
        self.assertEqual(format_cop(3000), "$ 3.000")

    def test_formats_decimal_amounts(self):
        self.assertEqual(format_cop("1234.5"), "$ 1.234,50")

    def test_omits_symbol_when_requested(self):
        self.assertEqual(format_cop(Decimal("2500"), with_symbol=False), "2.500")
