"""Custom template filters for currency formatting."""
from __future__ import annotations

from django import template

from home.utils.currency import format_cop, should_include_symbol

register = template.Library()


@register.filter(name="currency_cop")
def currency_cop(value, show_symbol: bool = True):
    """Format ``value`` as Colombian pesos inside templates."""

    include_symbol = should_include_symbol(show_symbol)
    return format_cop(value, with_symbol=include_symbol)
