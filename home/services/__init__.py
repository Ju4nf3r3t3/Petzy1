"""Service layer utilities for the home app."""

from .recommendations import (
    FeaturedProductsProvider,
    DatabaseFeaturedProductsProvider,
    StaticFeaturedProductsProvider,
    get_featured_provider,
)

__all__ = [
    "FeaturedProductsProvider",
    "DatabaseFeaturedProductsProvider",
    "StaticFeaturedProductsProvider",
    "get_featured_provider",
]
