"""Recommendation providers for the landing page.

This module demonstrates dependency inversion by defining an interface
(`FeaturedProductsProvider`) and two concrete implementations that obtain
featured products from different sources.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List, Sequence

from django.utils.translation import gettext_lazy as _

try:  # pragma: no cover - optional import for typing only
    from products.models import Producto
except Exception:  # pragma: no cover - to avoid circular import errors during typing
    Producto = None  # type: ignore


@dataclass(frozen=True)
class FeaturedProduct:
    """Lightweight representation of an item highlighted on the landing page."""

    name: str
    description: str
    price: Decimal
    url: str
    image_url: str | None = None


class FeaturedProductsProvider(ABC):
    """Interface that abstracts the origin of highlighted products."""

    @abstractmethod
    def get_featured(self, limit: int = 4) -> Sequence[FeaturedProduct]:
        """Return a collection of :class:`FeaturedProduct` instances."""


class DatabaseFeaturedProductsProvider(FeaturedProductsProvider):
    """Loads featured products directly from the database."""

    def __init__(self, queryset=None):
        # Late import to avoid circular dependencies when module is imported at startup
        from products.models import Producto as ProductoModel

        self._queryset = queryset or ProductoModel.objects.filter(stock__gt=0)

    def get_featured(self, limit: int = 4) -> Sequence[FeaturedProduct]:
        productos = self._queryset.order_by("-fecha_creacion")[:limit]
        items: List[FeaturedProduct] = []
        for producto in productos:
            items.append(
                FeaturedProduct(
                    name=producto.nombre,
                    description=producto.descripcion,
                    price=producto.precio,
                    url=producto.get_absolute_url(),
                    image_url=producto.imagen.url if producto.imagen else None,
                )
            )
        return items


class StaticFeaturedProductsProvider(FeaturedProductsProvider):
    """Provides a deterministic fallback when the database has no data."""

    def __init__(self, items: Iterable[FeaturedProduct] | None = None):
        if items is None:
            items = [
                FeaturedProduct(
                    name=_("Paquete de bienvenida para tu mascota"),
                    description=_("Incluye cama acolchada, plato doble y juguete interactivo."),
                    price=Decimal("89900"),
                    url="#",
                    image_url=None,
                ),
                FeaturedProduct(
                    name=_("Kit de aseo esencial"),
                    description=_("Shampoo hipoalergénico, guante cepillador y toallas absorbentes."),
                    price=Decimal("45500"),
                    url="#",
                    image_url=None,
                ),
            ]
        self._items = list(items)

    def get_featured(self, limit: int = 4) -> Sequence[FeaturedProduct]:
        return self._items[:limit]


def get_featured_provider() -> FeaturedProductsProvider:
    """Factory that returns the most suitable provider for the context."""

    provider = DatabaseFeaturedProductsProvider()
    if provider.get_featured(limit=1):
        return provider
    return StaticFeaturedProductsProvider()
